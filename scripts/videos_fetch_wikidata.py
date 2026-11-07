#!/usr/bin/env python
"""
Add Wikidata ids to data/yaml/video_series.yaml and video_features.yaml.

Every entry carries an ``imdb_id``. Wikidata records the IMDb id of a work
as property P345 (``tt0306414``), so the Wikidata item of each entry can be
found by asking the Wikidata Query Service which item has that P345. The
answer is written as a ``wikidata_id`` line right after the ``imdb_id`` line::

    - name: "The Wire"
      imdb_id: "0306414"
      wikidata_id: "Q478360"

The Wikidata id is the hub for the other sites a card may link to: the same
item carries the Rotten Tomatoes (P1258), Metacritic (P1712) and TMDB ids
and the Wikipedia articles, so later links can be derived from it.

Lookups are cached in ``shelve/wikidata_imdb.json`` (committed, like the
other lookup caches), mapping each IMDb id to its item and label, or to
null when Wikidata has no item for it. A re-run only queries ids that are
not cached yet, and the build's check (scripts/check_wikidata_ids.py) reads
only that cache, so CI never touches the network. An IMDb id that matches
more than one item is reported and left without a ``wikidata_id``.

Reading Wikidata needs no account or key. The query service asks for a
descriptive User-Agent and modest request rates: ids go out in batches of
100, one batch per second.

The yaml is edited textually, not re-dumped, so nothing else in the hand
formatted files moves. An existing ``wikidata_id`` line is left alone.

Run from the repo root:

    scripts/videos_fetch_wikidata.py            # look up and write what is missing
    scripts/videos_fetch_wikidata.py --dry-run  # look up and report, do not write the yaml
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

YAML_PATHS = [Path("data/yaml/video_series.yaml"), Path("data/yaml/video_features.yaml")]
CACHE_PATH = Path("shelve/wikidata_imdb.json")
ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "veltzer.org-media-tracker/1.0 (https://github.com/veltzer/veltzer.github.io)"
BATCH = 100

NAME_RE = re.compile(r'^  - name: (.*)$')
IMDB_RE = re.compile(r'^    imdb_id: "(\d+)"$')
WIKIDATA_RE = re.compile(r'^    wikidata_id: ')


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def query(imdb_ids: list[str]) -> dict[str, list[tuple[str, str]]]:
    """Map each IMDb id (without tt) to the (item, label) pairs whose P345 is that id."""
    values = " ".join(f'"tt{i}"' for i in imdb_ids)
    sparql = f"""
SELECT ?imdb ?item ?itemLabel WHERE {{
  VALUES ?imdb {{ {values} }}
  ?item wdt:P345 ?imdb .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,mul". }}
}}"""
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": sparql, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        rows = json.load(resp)["results"]["bindings"]
    found: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        imdb = row["imdb"]["value"].removeprefix("tt")
        item = row["item"]["value"].rsplit("/", 1)[-1]
        found.setdefault(imdb, []).append((item, row["itemLabel"]["value"]))
    return found


def imdb_ids_in(path: Path) -> list[str]:
    return [m.group(1) for line in path.read_text(encoding="utf-8").splitlines() if (m := IMDB_RE.match(line))]


def write_ids(path: Path, cache: dict) -> int:
    """Insert a wikidata_id line after every imdb_id line that lacks one; return how many were added."""
    lines = path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    added = 0
    for index, line in enumerate(lines):
        out.append(line)
        m = IMDB_RE.match(line)
        if not m:
            continue
        nxt = lines[index + 1] if index + 1 < len(lines) else ""
        entry = cache.get(m.group(1))
        if WIKIDATA_RE.match(nxt) or not entry or "ambiguous" in entry:
            continue
        out.append(f'    wikidata_id: "{entry["item"]}"')
        added += 1
    path.write_text("\n".join(out), encoding="utf-8")
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="look up and report, but do not write the yaml")
    args = parser.parse_args()

    cache = load_cache()
    wanted = sorted({i for path in YAML_PATHS for i in imdb_ids_in(path)})
    missing = [i for i in wanted if i not in cache]
    for start in range(0, len(missing), BATCH):
        batch = missing[start:start + BATCH]
        found = query(batch)
        for imdb in batch:
            hits = found.get(imdb, [])
            if len(hits) == 1:
                cache[imdb] = {"item": hits[0][0], "label": hits[0][1]}
            elif hits:
                cache[imdb] = {"ambiguous": sorted(item for item, _ in hits)}
            else:
                cache[imdb] = None
        save_cache(cache)
        if start + BATCH < len(missing):
            time.sleep(1)
    print(f"{len(wanted)} imdb ids, {len(missing)} looked up, {len(wanted) - len(missing)} from the cache")
    for imdb in wanted:
        entry = cache[imdb]
        if entry is None:
            print(f"  no Wikidata item for tt{imdb}")
        elif "ambiguous" in entry:
            print(f"  tt{imdb} matches several items, left out: {', '.join(entry['ambiguous'])}")
    if not args.dry_run:
        for path in YAML_PATHS:
            print(f"{path}: {write_ids(path, cache)} wikidata_id lines added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
