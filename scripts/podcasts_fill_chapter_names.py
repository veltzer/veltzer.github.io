#!/usr/bin/env python

"""
Replaces numeric chapter titles ("1", "2", "3"...) with real episode data
fetched from the podcast's RSS feed. Non-numeric titles (e.g. "Trailer")
are left unchanged. Also backfills all RSS metadata fields.
A chapter is paired with an episode by its 0-based position in the chapter
list (chapter i is episodes[i], oldest first), the same convention as
podcasts_add_chapters.py and podcasts_backfill_rss_data.py; the number in the
title is only a label. A podcast whose feed fails is reported and skipped, and
the file is saved after each podcast that changed.
"""

import argparse
import sys

from podcast_utils import (
    FEED_ERRORS,
    dump_to_string,
    make_yaml,
    match_episode,
    parse_rss_episodes,
    save_yaml,
    set_rss_fields,
)
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ


def _process_podcast(data, idx):
    """Process a single podcast, renaming numeric chapter titles. Returns count of renamed chapters, or None when the feed failed."""
    if idx >= len(data["items"]):
        print(f"Error: Podcast index {idx} out of range.")
        return 0

    podcast = data["items"][idx]
    name = str(podcast.get("name", "?"))
    rss_feed = str(podcast.get("rss_feed", ""))

    if not rss_feed:
        print(f"  [{idx}] {name}: no rss_feed, skipping.")
        return 0

    chapters = podcast.get("chapters", [])
    if not chapters:
        print(f"  [{idx}] {name}: no chapters, skipping.")
        return 0

    title_key = "title" if "title" in chapters[0] else "name"
    numeric_chapters = [
        (i, ch) for i, ch in enumerate(chapters)
        if str(ch.get(title_key, "")).isdigit()
    ]
    if not numeric_chapters:
        print(f"  [{idx}] {name}: no numeric chapter titles, skipping.")
        return 0

    print(f"  [{idx}] {name}: fetching RSS feed...")
    try:
        episodes = parse_rss_episodes(rss_feed)
    except FEED_ERRORS as e:
        print(f"       ERROR: {e}")
        return None
    print(f"       Found {len(episodes)} episodes in feed.")

    renamed = 0
    for pos, chapter in numeric_chapters:
        old_title = str(chapter[title_key])
        ep = match_episode(chapter, pos, episodes)
        if ep is None:
            print(f"       {old_title}: no episode at position {pos} (only {len(episodes)} episodes), skipping.")
            continue
        if old_title.isdigit() and int(old_title) not in (pos, pos + 1):
            print(f"       note: chapter {pos} is titled {old_title!r}; pairing it with episode {pos} by position.")
        chapter[title_key] = DQ(ep["title"])
        set_rss_fields(chapter, ep, only_missing=True)
        print(f"       {old_title} -> {ep['title']}")
        renamed += 1

    print(f"       Renamed {renamed} chapter(s).")
    return renamed


def fill_chapter_names(file_path, podcast_index=None, dry_run=False):
    """
    Replace numeric chapter titles with real episode data from RSS.
    If podcast_index is None, process all podcasts.
    """
    yaml = make_yaml()

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return

    if podcast_index is not None:
        indices = [podcast_index]
    else:
        indices = range(len(data["items"]))

    total_renamed = 0
    failed = []
    for idx in indices:
        renamed = _process_podcast(data, idx)
        if renamed is None:
            failed.append(idx)
            continue
        total_renamed += renamed
        if renamed and not dry_run:
            save_yaml(yaml, data, file_path)

    if failed:
        print(f"\nFailed feeds (podcast indices): {', '.join(map(str, failed))}")

    if total_renamed == 0:
        print("\nNo chapters needed renaming.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({total_renamed} would be renamed) ---")
        sys.stdout.write(dump_to_string(yaml, data))
    else:
        print(f"\nSaved. Renamed {total_renamed} chapter(s) total.")


def main():
    parser = argparse.ArgumentParser(
        description="Replace numeric chapter titles with real episode data from RSS."
    )
    parser.add_argument("yaml_file", nargs="?", default="data/yaml/podcasts.yaml", help="The YAML file to process.")
    parser.add_argument(
        "--podcast-index", type=int, default=None,
        help="Index of a specific podcast to process (default: all)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print output instead of saving."
    )
    args = parser.parse_args()
    fill_chapter_names(args.yaml_file, args.podcast_index, args.dry_run)


if __name__ == "__main__":
    main()
