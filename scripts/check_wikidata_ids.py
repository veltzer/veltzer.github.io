#!/usr/bin/env python
"""
Check that every wikidata_id in the video yaml belongs to its imdb_id.

Run by rsconstruct (processor.checker.script.wikidata_ids) with the yaml
files as arguments:

  check_wikidata_ids.py <video_series.yaml> [<video_features.yaml> ...]

A ``wikidata_id`` is right when the Wikidata item's IMDb id (P345) is the
entry's ``imdb_id``. scripts/videos_fetch_wikidata.py records that mapping
in shelve/wikidata_imdb.json when it writes the ids, and this check reads
only that committed cache, so it never touches the network. An entry fails
when its wikidata_id is not the item the cache has for its imdb_id, which
catches a hand-typed or stale id and an imdb_id changed without its
wikidata_id. An imdb_id missing from the cache fails too: run the fetch
script to look it up.
"""

import json
import sys
from pathlib import Path

import yaml

CACHE_PATH = Path("shelve/wikidata_imdb.json")


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    errors = []
    for name in sys.argv[1:]:
        with open(name, encoding="utf-8") as handle:
            items = yaml.safe_load(handle)["items"]
        for item in items:
            wikidata_id = item.get("wikidata_id")
            if wikidata_id is None:
                continue
            imdb_id = item["imdb_id"]
            if imdb_id not in cache:
                errors.append(f"{name}: {item['name']}: tt{imdb_id} is not in {CACHE_PATH}; run scripts/videos_fetch_wikidata.py")
                continue
            entry = cache[imdb_id]
            expected = entry.get("item") if entry else None
            if wikidata_id != expected:
                errors.append(f"{name}: {item['name']}: wikidata_id {wikidata_id} but tt{imdb_id} is {expected or 'not on Wikidata'}")
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
