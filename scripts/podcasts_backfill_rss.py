#!/usr/bin/env python

"""
Backfills rss_feed URLs for podcasts in the YAML file.
Looks up each podcast by name on the iTunes Search API to find its RSS feed URL.
"""

import argparse
import sys
import time

import requests
from podcast_utils import dump_to_string, make_yaml, normalise_title, save_yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

SEARCH_URL = "https://itunes.apple.com/search"
# Seconds between iTunes requests; the API throttles bursts.
REQUEST_DELAY = 3.0


def _plausible(name, candidate):
    """True when the iTunes result name equals or contains the wanted name (normalised), or the reverse."""
    want = normalise_title(name)
    got = normalise_title(candidate)
    return bool(want) and bool(got) and (want == got or want in got or got in want)


def find_rss_feed(podcast_name):
    """
    Search iTunes for a podcast by name and return the feedUrl of the first
    result whose name plausibly matches, or None (the caller reports it).
    """
    params = {
        "term": podcast_name,
        "media": "podcast",
        "entity": "podcast",
        "limit": 5,
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    for result in resp.json().get("results", []):
        candidate = result.get("trackName") or result.get("collectionName") or ""
        if result.get("feedUrl") and _plausible(podcast_name, candidate):
            return result["feedUrl"]
        print(f"[skipped non-matching hit: {candidate!r}]", end=" ")
    return None


def backfill_rss(file_path, dry_run=False):
    """Add rss_feed to podcasts that don't have one. Saves after each podcast found."""
    yaml = make_yaml()

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return

    updated = 0
    failed = []
    first = True
    for item in data["items"]:
        name = str(item.get("name", ""))
        if item.get("rss_feed"):
            print(f"  Already has rss_feed: {name}")
            continue

        if not first:
            time.sleep(REQUEST_DELAY)
        first = False
        print(f"  Looking up: {name}...", end=" ")
        try:
            feed_url = find_rss_feed(name)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"ERROR: {e}")
            failed.append(name)
            continue
        if feed_url:
            # Insert rss_feed right after url (or after name if no url)
            keys = list(item.keys())
            if "url" in keys:
                insert_pos = keys.index("url") + 1
            elif "name" in keys:
                insert_pos = keys.index("name") + 1
            else:
                insert_pos = 0
            item.insert(insert_pos, "rss_feed", DQ(feed_url))
            print(f"found: {feed_url}")
            updated += 1
            if not dry_run:
                save_yaml(yaml, data, file_path)
        else:
            print("NOT FOUND")
            failed.append(name)

    if failed:
        print(f"\nNo feed for {len(failed)} podcast(s): {', '.join(failed)}")
    if updated == 0:
        print("\nNo updates needed.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({updated} would be updated) ---")
        sys.stdout.write(dump_to_string(yaml, data))
    else:
        print(f"\nSaved. Updated {updated} podcast(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Backfill rss_feed URLs for podcasts in a YAML file."
    )
    parser.add_argument("yaml_file", nargs="?", default="data/yaml/podcasts.yaml", help="The YAML file to process.")
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of saving.")
    args = parser.parse_args()
    backfill_rss(args.yaml_file, args.dry_run)


if __name__ == "__main__":
    main()
