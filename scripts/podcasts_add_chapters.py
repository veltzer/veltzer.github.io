#!/usr/bin/env python

"""
Adds chapters to a podcast entry in a YAML file using real episode data
fetched from the podcast's RSS feed.
Each run appends the next N episodes (default 10), continuing from where
the last run left off.
"""

import argparse
import sys
from datetime import UTC, datetime

from podcast_utils import (
    FEED_ERRORS,
    dump_to_string,
    make_yaml,
    parse_rss_episodes,
    save_yaml,
    set_rss_fields,
)
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ


def _append_episodes(chapters, eps_to_add):
    """Build chapter dicts from episodes and append them to the chapters list."""
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if chapters:
        last = chapters[-1]
        location = str(last.get("location", ""))
        device = str(last.get("device", ""))
        date_timezone = str(last.get("date_timezone", ""))
    else:
        location = ""
        device = ""
        date_timezone = ""
    for ep in eps_to_add:
        print(f"  + {ep['title']}")
        chapter = {"title": DQ(ep["title"])}
        set_rss_fields(chapter, ep)
        chapter["date_utcz"] = DQ(now_utc)
        chapter["date_timezone"] = DQ(date_timezone)
        if location:
            chapter["location"] = DQ(location)
        chapter["device"] = DQ(device)
        chapters.append(chapter)


def add_chapters(file_path, count=10, podcast_index=0, dry_run=False):
    """
    Adds `count` new chapters to the podcast at the given index,
    using real episode data from the RSS feed.
    """
    print(f"--- Processing '{file_path}' ---")

    yaml = make_yaml()

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return

    if podcast_index >= len(data["items"]):
        print(f"Error: Podcast index {podcast_index} out of range (have {len(data['items'])} items).")
        return

    podcast = data["items"][podcast_index]
    print(f"Podcast: {podcast['name']}")

    rss_feed = str(podcast.get("rss_feed", ""))
    if not rss_feed:
        print("Error: No rss_feed URL found for this podcast. Run podcasts_backfill_rss.py first.")
        return

    print("Fetching episodes from RSS feed...")
    try:
        episodes = parse_rss_episodes(rss_feed)
    except FEED_ERRORS as e:
        print(f"Error: could not read the feed: {e}")
        return
    print(f"Found {len(episodes)} episodes in feed.")

    if "chapters" not in podcast:
        podcast["chapters"] = []

    chapters = podcast["chapters"]
    current_count = len(chapters)

    start = current_count
    end = min(start + count, len(episodes))

    if start >= len(episodes):
        print(f"Already have {current_count} chapters — no more episodes in feed ({len(episodes)} total).")
        return

    eps_to_add = episodes[start:end]
    print(f"Adding {len(eps_to_add)} chapters (episodes {start + 1} to {end}):")
    _append_episodes(chapters, eps_to_add)

    if dry_run:
        print("\n--- Dry Run ---")
        sys.stdout.write(dump_to_string(yaml, data))
    else:
        save_yaml(yaml, data, file_path)
        print(f"\nSaved. Now have {len(chapters)} chapters total.")


def main():
    parser = argparse.ArgumentParser(
        description="Add more chapters to a podcast using real episode data from RSS."
    )
    parser.add_argument("yaml_file", nargs="?", default="data/yaml/podcasts.yaml", help="The YAML file to process.")
    parser.add_argument(
        "--count", type=int, default=10,
        help="Number of chapters to add (default: 10)."
    )
    parser.add_argument(
        "--podcast-index", type=int, default=0,
        help="Index of the podcast in the items list (default: 0)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print output instead of saving."
    )
    args = parser.parse_args()
    add_chapters(args.yaml_file, args.count, args.podcast_index, args.dry_run)


if __name__ == "__main__":
    main()
