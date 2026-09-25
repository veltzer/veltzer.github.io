#!/usr/bin/env python

"""
Backfills rss_feed URLs for podcasts in the YAML file.
Looks up each podcast by name on the iTunes Search API to find its RSS feed URL.
"""

import argparse
import sys

import requests
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

SEARCH_URL = "https://itunes.apple.com/search"


def find_rss_feed(podcast_name):
    """Search iTunes for a podcast by name and return the feedUrl."""
    params = {
        "term": podcast_name,
        "media": "podcast",
        "entity": "podcast",
        "limit": 5,
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    # Return the first result's feed URL
    return results[0].get("feedUrl")


def backfill_rss(file_path, dry_run=False):
    """Add rss_feed to podcasts that don't have one."""
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return

    updated = 0
    for item in data["items"]:
        name = str(item.get("name", ""))
        if item.get("rss_feed"):
            print(f"  Already has rss_feed: {name}")
            continue

        print(f"  Looking up: {name}...", end=" ")
        feed_url = find_rss_feed(name)
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
        else:
            print("NOT FOUND")

    if updated == 0:
        print("\nNo updates needed.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({updated} would be updated) ---")
        yaml.dump(data, sys.stdout)
    else:
        with open(file_path, "w", encoding="UTF8") as f:
            yaml.dump(data, f)
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
