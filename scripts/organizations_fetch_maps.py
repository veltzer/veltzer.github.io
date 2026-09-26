#!/usr/bin/env python
"""
Render the small map image each company card shows from OpenStreetMap tiles.

The companies tab used to embed a Google Maps iframe per card, which pulls a
whole maps application into every card for a link that is rarely clicked.
A card now shows a static image of the same point, rendered here once and
committed like every other card image, so a visitor pays for one lazy-loaded
JPEG served from the site and no third-party request at all. The "on Google
Maps" link under it still opens the real map. doc/DECISIONS.md has the
comparison with the Maps Static API and Leaflet.

For every organization the companies tab shows (``teaching`` among its
``functions``) the ``geo`` point chosen in organizations.yaml is rendered
at zoom 13 (city level) into ``static/images/map-<lat>_<lon>.jpg``, the
name ``import_companies.map_path`` gives it. The file is keyed by the
coordinates, not the slug: Nominatim puts every company in a city on that
city's centroid, so 88 companies share 24 points, and one image per point
keeps ``static/images/`` free of byte-identical copies (which the
duplicate-image check would refuse anyway).

Tiles come from tile.openstreetmap.org, whose usage policy asks for a real
User-Agent, no bulk downloading and visible attribution: requests are
paced, every tile is cached under ``out/osm_tiles/`` (gitignored) so a
re-render fetches nothing, and plugin-companies.js prints the
"© OpenStreetMap contributors" credit under each map. The rendered image
is 800x320, already within image_standard's MAX_EDGE, and is saved at its
JPEG quality straight from Pillow, so it does not go through normalise().

An image that already exists is left alone unless ``--force`` is given.
Run from the repo root after adding an organization or changing its point:

    scripts/organizations_fetch_maps.py
    scripts/organizations_fetch_maps.py --force    # re-render everything
"""

import argparse
import io
import math
import sys
import time
from pathlib import Path

import requests
import yaml
from import_companies import map_path, taught_at
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = REPO_ROOT / "data" / "yaml" / "organizations.yaml"
IMAGES_DIR = REPO_ROOT / "static" / "images"
TILE_CACHE = REPO_ROOT / "out" / "osm_tiles"
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
USER_AGENT = "veltzer.github.io company map renderer (https://veltzer.org)"
TILE_SIZE = 256
# City level: at Israel's latitude an 800 px strip spans about 13 km.
ZOOM = 13
# 2x the card's map box (about 400x160 CSS pixels), the same reasoning as
# image_standard.MAX_EDGE; QUALITY matches image_standard too.
WIDTH, HEIGHT = 800, 320
QUALITY = 85
# Seconds between tile fetches that miss the cache.
PACE = 0.25
MARKER_FILL = (211, 51, 51)
MARKER_OUTLINE = (255, 255, 255)


def project(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    """Web Mercator pixel coordinates of a WGS84 point at a zoom level."""
    scale = TILE_SIZE * 2**zoom
    x = (lon + 180.0) / 360.0 * scale
    rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(rad) + 1.0 / math.cos(rad)) / math.pi) / 2.0 * scale
    return x, y


class Tiles:
    """Fetch OSM tiles through the on-disk cache, paced when they miss."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.fetched = 0

    def get(self, zoom: int, x: int, y: int) -> Image.Image:
        cached = TILE_CACHE / str(zoom) / str(x) / f"{y}.png"
        if not cached.exists():
            response = self.session.get(TILE_URL.format(z=zoom, x=x, y=y), timeout=30)
            response.raise_for_status()
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(response.content)
            self.fetched += 1
            time.sleep(PACE)
        return Image.open(io.BytesIO(cached.read_bytes())).convert("RGB")


def draw_marker(image: Image.Image, cx: float, cy: float) -> None:
    """A red pin whose tip is at (cx, cy), drawn oversampled for smooth edges."""
    factor = 4
    layer = Image.new("RGBA", (image.width * factor, image.height * factor), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = cx * factor, cy * factor
    radius = 14 * factor
    head_y = y - 22 * factor
    draw.polygon([(x - radius * 0.7, head_y + radius * 0.7), (x + radius * 0.7, head_y + radius * 0.7), (x, y)],
                 fill=MARKER_OUTLINE)
    draw.ellipse((x - radius - factor, head_y - radius - factor, x + radius + factor, head_y + radius + factor),
                 fill=MARKER_OUTLINE)
    draw.polygon([(x - radius * 0.6, head_y + radius * 0.6), (x + radius * 0.6, head_y + radius * 0.6),
                  (x, y - 2 * factor)], fill=MARKER_FILL)
    draw.ellipse((x - radius, head_y - radius, x + radius, head_y + radius), fill=MARKER_FILL)
    draw.ellipse((x - radius * 0.35, head_y - radius * 0.35, x + radius * 0.35, head_y + radius * 0.35),
                 fill=MARKER_OUTLINE)
    layer = layer.resize(image.size, Image.Resampling.LANCZOS)
    image.paste(layer, (0, 0), layer)


def render(tiles: Tiles, lat: float, lon: float) -> Image.Image:
    """Stitch the tiles around a point into a WIDTH x HEIGHT image with a pin on it."""
    px, py = project(lat, lon, ZOOM)
    left, top = px - WIDTH / 2, py - HEIGHT / 2
    image = Image.new("RGB", (WIDTH, HEIGHT))
    for tx in range(math.floor(left / TILE_SIZE), math.floor((left + WIDTH) / TILE_SIZE) + 1):
        for ty in range(math.floor(top / TILE_SIZE), math.floor((top + HEIGHT) / TILE_SIZE) + 1):
            image.paste(tiles.get(ZOOM, tx, ty), (round(tx * TILE_SIZE - left), round(ty * TILE_SIZE - top)))
    draw_marker(image, WIDTH / 2, HEIGHT / 2)
    return image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--force", action="store_true", help="re-render images that already exist")
    args = parser.parse_args()
    with open(YAML_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    points: dict[str, tuple[float, float]] = {}
    for item in data.get("items") or []:
        if taught_at(item) and item.get("geo"):
            points[map_path(item["geo"])] = (item["geo"]["lat"], item["geo"]["lon"])
    tiles = Tiles()
    rendered = 0
    for relative, (lat, lon) in sorted(points.items()):
        target = IMAGES_DIR / Path(relative).name
        if target.exists() and not args.force:
            continue
        render(tiles, lat, lon).save(target, quality=QUALITY, optimize=True, progressive=True)
        rendered += 1
        print(f"rendered {target.relative_to(REPO_ROOT)} ({lat}, {lon})")
    print(f"{len(points)} points, {rendered} rendered, {tiles.fetched} tiles fetched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
