#!/usr/bin/env python

"""Import the organizations I taught at from data/yaml/organizations.yaml.

organizations.yaml records every organization I dealt with -- taught at,
consulted for, was certified by -- with research notes, sources, three
geocoded place fields and logo provenance. The companies tab of the media
page wants only the ones with ``teaching`` among their ``functions``, and
only the fields a card shows: the name, the logo path, the current status
and what happened, where the company is and where its Israel office was,
the one map point chosen for it, the static map image of that point, and
the logo attribution. The media page prints ``review`` under every card's
name, so each company gets one: what happened to it, or a word on its status
when nothing did.

The map image is ``static/images/map-<lat>_<lon>.jpg``, rendered by
scripts/organizations_fetch_maps.py and committed. It is named after the
point, not the company, because every company in a city sits on that city's
centroid and one image per point avoids byte-identical copies. The name is
computed here (``map_path``) so the renderer and the card agree, and with
``--images-dir`` the importer fails when an image is missing, which is how
the build catches a new organization whose map was never rendered.

Everything else stays behind: the research ``sources``, the three per-field
``*_geo`` blocks the ``geo`` point was picked from, the bitmap the logo was
traced from, and the ``old_url`` the 2019 database held.

Unlike the other importers this one is a build step, not a copy_data.py
step: the YAML lives in this repo, so build_site.py runs it on every build
and writes the gzipped JSON straight into the output directory. Nothing is
committed. The logo paths are kept as they are in the YAML, relative to
data/ (``logos/<slug>.svg``), because build_site.py copies data/logos/ to
the same path under the site root.
"""

import argparse
import gzip
import json
import sys
from pathlib import Path

import yaml

TEACHING = "teaching"

# Fields copied verbatim when present. The order is the order in the JSON.
KEPT = (
    "name",
    "slug",
    "functions",
    "logo",
    "logo_kind",
    "logo_source",
    "logo_license",
    "website",
    "status",
    "location",
    "israel_office",
    "from_date",
    "remark",
)
GEO_KEYS = ("place", "lat", "lon")
MAP_PREFIX = "images/map-"
MAP_SUFFIX = ".jpg"
STATUS_BLURB = {
    "active": "Still active.",
    "unknown": "Whereabouts unknown.",
}


def taught_at(item):
    """True when the organization's functions include teaching."""
    return TEACHING in (item.get("functions") or [])


def blurb(item):
    """The line under the name: what happened, or the status when nothing did."""
    if item.get("what_happened"):
        return item["what_happened"]
    status = item.get("status") or "unknown"
    return STATUS_BLURB.get(status, status.capitalize() + ".")


def map_path(geo):
    """The site-relative path of the static map image for a geo point."""
    return f"{MAP_PREFIX}{geo['lat']}_{geo['lon']}{MAP_SUFFIX}"


def convert_item(item):
    """Keep the card fields of one organization, its one map point and map image."""
    out = {}
    for key in KEPT:
        value = item.get(key)
        if value is None or value == "":
            continue
        out[key] = value
    out["review"] = blurb(item)
    geo = item.get("geo")
    if geo and all(key in geo for key in GEO_KEYS):
        out["geo"] = {key: geo[key] for key in GEO_KEYS}
        out["map"] = map_path(geo)
    return out


def missing_maps(items, images_dir):
    """The map paths of ``items`` whose image is not in ``images_dir``, sorted, unique."""
    return sorted({item["map"] for item in items if "map" in item and not (images_dir / item["map"].rsplit("/", 1)[-1]).is_file()})


def convert(data):
    """Filter to the teaching organizations and trim each to its card fields."""
    items = data.get("items") or []
    return {"items": [convert_item(item) for item in items if taught_at(item)]}


def write_json_gz(path, data):
    """Write gzipped JSON with a fixed mtime and no name so rebuilds are byte-identical."""
    payload = json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    with open(path, "wb") as handle, gzip.GzipFile(filename="", fileobj=handle, mode="wb", mtime=0) as gz:
        gz.write(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="path to data/yaml/organizations.yaml")
    parser.add_argument("output", help="path of the .json.gz to write")
    parser.add_argument("--images-dir", type=Path,
                        help="static/images/; when given, fail if any company's map image is missing")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not data or "items" not in data:
        print(f"ERROR: {args.input} has no items", file=sys.stderr)
        return 1
    converted = convert(data)
    if not converted["items"]:
        print(f"ERROR: {args.input} has no organization with '{TEACHING}' among its functions", file=sys.stderr)
        return 1
    if args.images_dir is not None:
        missing = missing_maps(converted["items"], args.images_dir)
        if missing:
            print(f"ERROR: {len(missing)} map image(s) missing under {args.images_dir}, run scripts/organizations_fetch_maps.py:",
                  file=sys.stderr)
            for path in missing:
                print(f"  {path}", file=sys.stderr)
            return 1
    write_json_gz(args.output, converted)
    print(f"Imported {len(converted['items'])} companies to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
