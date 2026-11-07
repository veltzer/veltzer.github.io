#!/usr/bin/env python
"""
Check the wikidata_id and rotten_tomatoes_id of every entry in the video yaml.

Run by rsconstruct (processor.checker.script.wikidata_ids) with the yaml
files as arguments:

  check_wikidata_ids.py <video_series.yaml> [<video_features.yaml> ...]

A ``wikidata_id`` is right when the Wikidata item's IMDb id (P345) is the
entry's ``imdb_id``. Every entry must have a ``rotten_tomatoes_id``, and it
is right when it is the Rotten Tomatoes path (P1258) on that item, or, when
Wikidata has none, the hand-verified path in data/rotten_tomatoes_manual.json
(where null records that Rotten Tomatoes has no page for the work).

scripts/videos_fetch_wikidata.py records the Wikidata side in
shelve/wikidata_imdb.json when it writes the ids, and this check reads only
that committed cache and the hand list, so it never touches the network. It
catches a hand-typed or stale id, an imdb_id changed without the ids derived
from it, and a new entry nobody looked up yet (run the fetch script).
"""

import json
import sys
from pathlib import Path

import yaml

CACHE_PATH = Path("shelve/wikidata_imdb.json")
MANUAL_PATH = Path("data/rotten_tomatoes_manual.json")
MISSING = object()


def check_item(name: str, item: dict, cache: dict, manual: dict) -> list[str]:
    where = f"{name}: {item['name']}"
    imdb_id = item["imdb_id"]
    if imdb_id not in cache:
        return [f"{where}: tt{imdb_id} is not in {CACHE_PATH}; run scripts/videos_fetch_wikidata.py"]
    entry = cache[imdb_id] or {}
    errors = []
    wikidata_id = item.get("wikidata_id")
    if wikidata_id is not None and wikidata_id != entry.get("item"):
        errors.append(f"{where}: wikidata_id {wikidata_id} but tt{imdb_id} is {entry.get('item') or 'not on Wikidata'}")
    if "item" in entry and "rotten_tomatoes" not in entry:
        return [*errors, f"{where}: no Rotten Tomatoes lookup for {entry['item']} in {CACHE_PATH}; run scripts/videos_fetch_wikidata.py"]
    from_wikidata = entry.get("rotten_tomatoes")
    if isinstance(from_wikidata, str):
        expected, source = from_wikidata, f"Wikidata {entry['item']}"
    elif imdb_id in manual:
        expected, source = manual[imdb_id]["rotten_tomatoes_id"], str(MANUAL_PATH)
    else:
        return [*errors, f"{where}: no Rotten Tomatoes id on Wikidata for tt{imdb_id}; find the page and add it to {MANUAL_PATH}"]
    actual = item.get("rotten_tomatoes_id", MISSING)
    shown = expected if expected is not None else "null (no Rotten Tomatoes page)"
    if actual is MISSING:
        errors.append(f"{where}: rotten_tomatoes_id missing ({source} has {shown}); run scripts/videos_fetch_wikidata.py")
    elif actual != expected:
        errors.append(f"{where}: rotten_tomatoes_id {actual} but {source} has {shown}")
    return errors


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    manual = json.loads(MANUAL_PATH.read_text(encoding="utf-8"))["entries"]
    errors = []
    for name in sys.argv[1:]:
        with open(name, encoding="utf-8") as handle:
            items = yaml.safe_load(handle)["items"]
        for item in items:
            errors.extend(check_item(name, item, cache, manual))
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
