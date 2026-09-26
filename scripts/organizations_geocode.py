#!/usr/bin/env python
"""
Add map coordinates to data/yaml/organizations.yaml.

For every organization, each of the free-text place fields (``location``,
``israel_office`` and ``former_location``) gets a sibling ``<field>_geo``
mapping right after it::

    location: Espoo, Finland
    location_geo:
      place: Espoo, Finland
      lat: 60.20549
      lon: 24.6559

``place`` is the query the coordinates were resolved for: the free text
reduced to its first city (parentheticals, ``;`` tails and ``and``/``/``
lists dropped, ``, Israel`` appended for Israel offices). It stays in the
file so a reader can see which city a point stands for without re-parsing
the prose. ``lat``/``lon`` are WGS84 decimal degrees, which is what Leaflet,
OpenLayers, Google Maps and friends take directly.

Coordinates come from Nominatim (OpenStreetMap), one request per second as
its usage policy asks, and are cached in ``shelve/nominatim_geocode.json``
(committed, like the other lookup caches in ``shelve/``), so a re-run after
adding an organization only resolves the new places. A ``<field>_geo`` that
is already present is left alone unless ``--force`` is given, so a hand
correction survives re-runs. Places that name no city (``unknown``,
``Israel (city unknown)``) get no ``_geo``.

The yaml is edited textually, not re-dumped: the file is hand-wrapped and no
dumper reproduces it byte for byte, so the ``_geo`` blocks are spliced in
after the line(s) of the field they describe and nothing else moves.

Run from the repo root:

    scripts/organizations_geocode.py            # add what is missing
    scripts/organizations_geocode.py --force    # recompute everything
    scripts/organizations_geocode.py --dry-run  # only print the resolution table
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

YAML_PATH = Path("data/yaml/organizations.yaml")
CACHE_PATH = Path("shelve/nominatim_geocode.json")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "veltzer.github.io organizations geocoder (https://veltzer.org)"
PLACE_FIELDS = ("location", "israel_office", "former_location")

# Queries that Nominatim resolves to the wrong place when built mechanically
# from the prose. Keyed by the mechanical query; the value is either a better
# free-text query or a structured query (Nominatim's city/state/country
# parameters), which is the only way to get a city whose county shares its name.
OVERRIDES: dict[str, str | dict[str, str]] = {
    # Nominatim prefers the Chesterfield in Derbyshire for the bare name.
    "Chesterfield, Missouri, USA": "Chesterfield, St. Louis County, Missouri, USA",
    # The free-text query lands on the county centroid, ~20 km from the city.
    "Santa Clara, California, USA": {"city": "Santa Clara", "state": "California", "country": "USA"},
    "San Mateo, California, USA": {"city": "San Mateo", "state": "California", "country": "USA"},
}

# Prose that names no place worth a point on a map.
UNRESOLVABLE = ("unknown", "israel")

ITEM_RE = re.compile(r"^- id: (\d+)\s*$")
KEY_RE = re.compile(r"^  ([a-z_]+):")


def place_query(text: str, israel: bool) -> str | None:
    """Reduce a free-text place to a single geocodable ``City, Country`` string.

    ``israel`` says the field is ``israel_office``, whose values often name
    the city alone (``Herzliya``) or several cities (``Yokneam and Petah
    Tikva``); the first city wins and ``, Israel`` is appended.
    """
    text = text.strip()
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = text.split(";", 1)[0]
    text = re.split(r"\s+(?:with|and|plus)\s+|\s+/\s+", text, maxsplit=1)[0]
    text = text.replace(" area", "")
    text = re.sub(r"\s+R&D center.*$", "", text)
    text = text.strip(" ,")
    if not text or text.lower().startswith(UNRESOLVABLE):
        return None
    if israel:
        parts = [p.strip() for p in text.split(",")]
        parts = [p for p in parts if p and p.lower() != "israel"]
        if not parts:
            return None
        text = f"{parts[0]}, Israel"
    return text


def load_cache() -> dict[str, Any]:
    if CACHE_PATH.exists():
        with CACHE_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict[str, Any]) -> None:
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def nominatim(query: str) -> dict[str, Any] | None:
    """One Nominatim lookup; returns the best hit or None."""
    override = OVERRIDES.get(query, query)
    params = {"q": override} if isinstance(override, str) else dict(override)
    params.update({"format": "jsonv2", "limit": "1", "accept-language": "en"})
    response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    hits = response.json()
    time.sleep(1.1)  # Nominatim usage policy: at most one request per second
    if not hits:
        return None
    hit = hits[0]
    return {
        "lat": float(hit["lat"]),
        "lon": float(hit["lon"]),
        "display_name": hit["display_name"],
        "osm_type": hit["osm_type"],
        "osm_id": hit["osm_id"],
        "type": hit.get("type"),
    }


def geocode(query: str, cache: dict[str, Any]) -> dict[str, Any] | None:
    if query not in cache:
        cache[query] = nominatim(query)
        save_cache(cache)
    return cache[query]


def geo_lines(field: str, query: str, hit: dict[str, Any]) -> list[str]:
    # safe_dump quotes the scalar if yaml needs it (e.g. a leading quote in "Ra'anana" does not, a colon would)
    # and appends a document-end marker to a bare scalar, which is dropped.
    place = yaml.safe_dump(query, allow_unicode=True, width=10000).strip().removesuffix("...").strip()
    return [
        f"  {field}_geo:\n",
        f"    place: {place}\n",
        f"    lat: {round(hit['lat'], 5)}\n",
        f"    lon: {round(hit['lon'], 5)}\n",
    ]


def splice(lines: list[str], blocks: dict[tuple[int, str], list[str]], force: bool) -> list[str]:
    """Insert each ``blocks[(item id, field)]`` after that field's line(s), dropping an old ``_geo`` when forced."""
    out: list[str] = []
    item_id = 0
    pending: list[str] | None = None  # block waiting for the end of the current field's lines
    skipping = False  # inside an existing _geo block that --force replaces
    for line in lines:
        m_item = ITEM_RE.match(line)
        m_key = KEY_RE.match(line)
        if m_item or m_key or not line.startswith(" "):
            # A new top-level key of the item (or a new item): the previous field is complete.
            if pending is not None:
                out.extend(pending)
                pending = None
            skipping = False
        if m_item:
            item_id = int(m_item.group(1))
        elif m_key:
            key = m_key.group(1)
            if key.endswith("_geo") and force and (item_id, key.removesuffix("_geo")) in blocks:
                skipping = True
            elif key in PLACE_FIELDS and (item_id, key) in blocks:
                pending = blocks[(item_id, key)]
        if not skipping:
            out.append(line)
    if pending is not None:
        out.extend(pending)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="recompute _geo blocks that already exist")
    parser.add_argument("--dry-run", action="store_true", help="resolve and print, but do not write the yaml")
    args = parser.parse_args()

    with YAML_PATH.open(encoding="utf-8") as f:
        text = f.read()
    data = yaml.safe_load(text)

    cache = load_cache()
    blocks: dict[tuple[int, str], list[str]] = {}
    unresolved: list[str] = []
    for item in data["items"]:
        for field in PLACE_FIELDS:
            if field not in item:
                continue
            if f"{field}_geo" in item and not args.force:
                continue
            query = place_query(str(item[field]), israel=field == "israel_office")
            if query is None:
                print(f"{item['id']:>4} {field:16} {'(no place)':45} <- {item[field]}")
                continue
            hit = geocode(query, cache)
            if hit is None:
                unresolved.append(f"{item['id']} {item['name']} {field}: {query!r} <- {item[field]!r}")
                print(f"{item['id']:>4} {field:16} {query:45} !! NOT FOUND")
                continue
            print(f"{item['id']:>4} {field:16} {query:45} -> {hit['display_name']}")
            blocks[(item["id"], field)] = geo_lines(field, query, hit)

    if unresolved:
        print("\nUnresolved places (add an OVERRIDES entry or fix the prose):", file=sys.stderr)
        for line in unresolved:
            print(f"  {line}", file=sys.stderr)
    if args.dry_run:
        print(f"\ndry run: {len(blocks)} _geo blocks would be written")
        return 1 if unresolved else 0
    new_lines = splice(text.splitlines(keepends=True), blocks, args.force)
    with YAML_PATH.open("w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"\nwrote {len(blocks)} _geo blocks to {YAML_PATH}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
