#!/usr/bin/env python
"""
Check the wikidata_id and rotten_tomatoes_id of every entry in the video yaml.

Run by rsconstruct (processor.checker.script.wikidata_ids) with the yaml
files as arguments:

  check_wikidata_ids.py <video_series.yaml> [<video_features.yaml> ...]

A ``wikidata_id`` is right when the Wikidata item's IMDb id (P345) is the
entry's ``imdb_id``, and a ``rotten_tomatoes_id`` is right when it is the
Rotten Tomatoes path (P1258) recorded on that item.
scripts/videos_fetch_wikidata.py records both in shelve/wikidata_imdb.json
when it writes the ids, and this check reads only that committed cache, so
it never touches the network. It catches a hand-typed or stale id, and an
imdb_id changed without the ids derived from it. An imdb_id missing from
the cache fails too: run the fetch script to look it up. A
rotten_tomatoes_id needs a wikidata_id, since that is where it comes from.
"""

import json
import sys
from pathlib import Path

import yaml

CACHE_PATH = Path("shelve/wikidata_imdb.json")


def check_item(name: str, item: dict, cache: dict) -> list[str]:
    wikidata_id = item.get("wikidata_id")
    rotten_id = item.get("rotten_tomatoes_id")
    if wikidata_id is None and rotten_id is None:
        return []
    where = f"{name}: {item['name']}"
    if wikidata_id is None:
        return [f"{where}: rotten_tomatoes_id without a wikidata_id"]
    imdb_id = item["imdb_id"]
    if imdb_id not in cache:
        return [f"{where}: tt{imdb_id} is not in {CACHE_PATH}; run scripts/videos_fetch_wikidata.py"]
    entry = cache[imdb_id] or {}
    if wikidata_id != entry.get("item"):
        return [f"{where}: wikidata_id {wikidata_id} but tt{imdb_id} is {entry.get('item') or 'not on Wikidata'}"]
    if rotten_id is not None:
        if "rotten_tomatoes" not in entry:
            return [f"{where}: no Rotten Tomatoes lookup for {wikidata_id} in {CACHE_PATH}; run scripts/videos_fetch_wikidata.py"]
        expected = entry["rotten_tomatoes"]
        if rotten_id != expected:
            shown = expected if isinstance(expected, str) else "not a single path on Wikidata"
            return [f"{where}: rotten_tomatoes_id {rotten_id} but {wikidata_id} has {shown}"]
    return []


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    errors = []
    for name in sys.argv[1:]:
        with open(name, encoding="utf-8") as handle:
            items = yaml.safe_load(handle)["items"]
        for item in items:
            errors.extend(check_item(name, item, cache))
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
