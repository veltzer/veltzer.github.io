#!/usr/bin/env python
"""
Add Wikidata and Rotten Tomatoes ids to the video yaml files.

Every entry in data/yaml/video_series.yaml and video_features.yaml carries
an ``imdb_id``. Wikidata records the IMDb id of a work as property P345
(``tt0306414``), so the Wikidata item of each entry can be found by asking
the Wikidata Query Service which item has that P345. The same item records
the work's Rotten Tomatoes path as property P1258 (``tv/the-wire``). Both
are written after the ``imdb_id`` line, the Rotten Tomatoes path taken from
data/rotten_tomatoes_manual.json when Wikidata has none (hand-verified
paths, or null for a work Rotten Tomatoes does not list)::

    - name: "The Wire"
      imdb_id: "0306414"
      wikidata_id: "Q478360"
      rotten_tomatoes_id: "tv/the-wire"

The item also carries the Metacritic (P1712) and TMDB ids and the Wikipedia
articles, so more links can be derived from it the same way.

P1258 statements can be ranked: a deprecated value (typically an old slug
spelling) is ignored, a single preferred value wins, otherwise the one
remaining value is taken. An item with several equally ranked values is
reported and gets no ``rotten_tomatoes_id``.

Lookups are cached in ``shelve/wikidata_imdb.json`` (committed, like the
other lookup caches), keyed by IMDb id: the item, its label and its
Rotten Tomatoes path (null when it has none), or null when Wikidata has no
item for the IMDb id. A re-run only queries what is not cached yet, and
the build's check (scripts/check_wikidata_ids.py) reads only that cache,
so CI never touches the network. An IMDb id that matches more than one
item is reported and left without either id.

Reading Wikidata needs no account or key. The query service asks for a
descriptive User-Agent and modest request rates: ids go out in batches of
100, one batch per second.

The yaml is edited textually, not re-dumped, so nothing else in the hand
formatted files moves. Existing ``wikidata_id`` and ``rotten_tomatoes_id``
lines are left alone.

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
MANUAL_PATH = Path("data/rotten_tomatoes_manual.json")
ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "veltzer.org-media-tracker/1.0 (https://github.com/veltzer/veltzer.github.io)"
BATCH = 100

IMDB_RE = re.compile(r'^    imdb_id: "(\d+)"$')
WIKIDATA_RE = re.compile(r'^    wikidata_id: ')
ROTTEN_RE = re.compile(r'^    rotten_tomatoes_id: ')


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def sparql(query_text: str) -> list[dict]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query_text, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["results"]["bindings"]


def items_for_imdb(imdb_ids: list[str]) -> dict[str, list[tuple[str, str]]]:
    """Map each IMDb id (without tt) to the (item, label) pairs whose P345 is that id."""
    values = " ".join(f'"tt{i}"' for i in imdb_ids)
    rows = sparql(f"""
SELECT ?imdb ?item ?itemLabel WHERE {{
  VALUES ?imdb {{ {values} }}
  ?item wdt:P345 ?imdb .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,mul". }}
}}""")
    found: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        imdb = row["imdb"]["value"].removeprefix("tt")
        item = row["item"]["value"].rsplit("/", 1)[-1]
        found.setdefault(imdb, []).append((item, row["itemLabel"]["value"]))
    return found


def rotten_for_items(items: list[str]) -> dict[str, list[tuple[str, str]]]:
    """Map each item to its (Rotten Tomatoes path, rank) statements."""
    values = " ".join(f"wd:{q}" for q in items)
    rows = sparql(f"""
SELECT ?item ?rt ?rank WHERE {{
  VALUES ?item {{ {values} }}
  ?item p:P1258 ?st .
  ?st ps:P1258 ?rt ; wikibase:rank ?rank .
}}""")
    found: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        item = row["item"]["value"].rsplit("/", 1)[-1]
        found.setdefault(item, []).append((row["rt"]["value"], row["rank"]["value"].rsplit("#", 1)[-1]))
    return found


def pick_rotten(statements: list[tuple[str, str]]) -> str | dict | None:
    """The one path to use, None when there is none, or {"ambiguous": [...]}."""
    preferred = [rt for rt, rank in statements if rank == "PreferredRank"]
    live = [rt for rt, rank in statements if rank != "DeprecatedRank"]
    choice = preferred if len(preferred) == 1 else live
    if not choice:
        return None
    if len(choice) == 1:
        return choice[0]
    return {"ambiguous": sorted(choice)}


def batches(seq: list[str]):
    for start in range(0, len(seq), BATCH):
        if start:
            time.sleep(1)
        yield seq[start:start + BATCH]


def imdb_ids_in(path: Path) -> list[str]:
    return [m.group(1) for line in path.read_text(encoding="utf-8").splitlines() if (m := IMDB_RE.match(line))]


def write_ids(path: Path, cache: dict, manual: dict) -> tuple[int, int]:
    """Insert missing wikidata_id / rotten_tomatoes_id lines after each imdb_id; return the counts added."""
    lines = path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    added_wikidata = added_rotten = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        out.append(line)
        index += 1
        m = IMDB_RE.match(line)
        if not m:
            continue
        entry: dict = cache.get(m.group(1)) or {}
        usable = "item" in entry
        if index < len(lines) and WIKIDATA_RE.match(lines[index]):
            out.append(lines[index])
            index += 1
        elif usable:
            out.append(f'    wikidata_id: "{entry["item"]}"')
            added_wikidata += 1
        if index < len(lines) and ROTTEN_RE.match(lines[index]):
            continue
        rotten = entry.get("rotten_tomatoes") if usable else None
        if not isinstance(rotten, str) and m.group(1) in manual:
            rotten = manual[m.group(1)]["rotten_tomatoes_id"]
            out.append(f'    rotten_tomatoes_id: "{rotten}"' if rotten else "    rotten_tomatoes_id: null")
            added_rotten += 1
        elif isinstance(rotten, str):
            out.append(f'    rotten_tomatoes_id: "{rotten}"')
            added_rotten += 1
    path.write_text("\n".join(out), encoding="utf-8")
    return added_wikidata, added_rotten


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="look up and report, but do not write the yaml")
    args = parser.parse_args()

    cache = load_cache()
    manual = json.loads(MANUAL_PATH.read_text(encoding="utf-8"))["entries"]
    wanted = sorted({i for path in YAML_PATHS for i in imdb_ids_in(path)})

    missing = [i for i in wanted if i not in cache]
    for batch in batches(missing):
        found = items_for_imdb(batch)
        for imdb in batch:
            hits = found.get(imdb, [])
            if len(hits) == 1:
                cache[imdb] = {"item": hits[0][0], "label": hits[0][1]}
            elif hits:
                cache[imdb] = {"ambiguous": sorted(item for item, _ in hits)}
            else:
                cache[imdb] = None
        save_cache(cache)

    no_rotten = sorted({cache[i]["item"] for i in wanted
                        if isinstance(cache[i], dict) and "item" in cache[i] and "rotten_tomatoes" not in cache[i]})
    for batch in batches(no_rotten):
        found = rotten_for_items(batch)
        for imdb in wanted:
            entry = cache[imdb]
            if isinstance(entry, dict) and entry.get("item") in batch:
                entry["rotten_tomatoes"] = pick_rotten(found.get(entry["item"], []))
        save_cache(cache)

    print(f"{len(wanted)} imdb ids: {len(missing)} items and {len(no_rotten)} Rotten Tomatoes ids looked up, the rest from the cache")
    for imdb in wanted:
        entry = cache[imdb]
        if entry is None:
            print(f"  no Wikidata item for tt{imdb}")
        elif "ambiguous" in entry:
            print(f"  tt{imdb} matches several items, left out: {', '.join(entry['ambiguous'])}")
        elif entry.get("rotten_tomatoes") is None and imdb not in manual:
            print(f"  no Rotten Tomatoes id on {entry['item']} ({entry['label']}) and none in {MANUAL_PATH}")
        elif isinstance(entry["rotten_tomatoes"], dict):
            print(f"  {entry['item']} has several Rotten Tomatoes ids, left out: {', '.join(entry['rotten_tomatoes']['ambiguous'])}")
    for imdb, hand in manual.items():
        entry = cache.get(imdb)
        if isinstance(entry, dict) and isinstance(entry.get("rotten_tomatoes"), str):
            print(f"  {MANUAL_PATH}: Wikidata now has {entry['rotten_tomatoes']} for tt{imdb} ({hand['name']}); drop the hand entry")
    if not args.dry_run:
        for path in YAML_PATHS:
            wikidata, rotten = write_ids(path, cache, manual)
            print(f"{path}: {wikidata} wikidata_id and {rotten} rotten_tomatoes_id lines added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
