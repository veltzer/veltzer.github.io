#!/usr/bin/env python

"""
Backfills RSS metadata into existing podcast chapters.
Each chapter is matched to a feed episode by guid, then by normalised title,
then - only when its title is absent or a bare number - by its 0-based
position in the chapter list (chapter i is episode i, oldest first, the way
podcasts_add_chapters.py appends them). A chapter whose title matches no
episode is reported and left alone. Adds, where missing:
  description, pubDate, episode, duration, episodeType, explicit,
  enclosure_url, image, author, guid.
Also renames 'name' to 'title' in chapters to match RSS field names, keeping
every other key. A podcast whose feed fails is reported and skipped; the
file is saved after each podcast that changed.
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


def _rebuild_chapter_from_name(chapter, ep):
    """
    Rename a chapter's 'name' to 'title' and add the RSS fields, keeping every
    other key (and its value) the chapter had. Order: title, RSS fields, the rest.
    """
    rest = [(k, v) for k, v in chapter.items() if k != "name"]
    title = chapter["title"] if "title" in chapter else chapter["name"]
    for key in list(chapter):  # not clear(): ruamel's CommentedMap keeps stale ordering keys
        del chapter[key]
    chapter["title"] = DQ(str(title))
    set_rss_fields(chapter, ep)
    for key, value in rest:
        chapter[key] = value


def _backfill_podcast(podcast, episodes):
    """Backfill one podcast's chapters. Returns the number changed."""
    updated = 0
    for i, chapter in enumerate(podcast.get("chapters", [])):
        title = str(chapter.get("title", chapter.get("name", "")))
        ep = match_episode(chapter, i, episodes)
        if ep is None:
            print(f"       Chapter {i} '{title}': no matching episode, skipping.")
            continue
        if "name" in chapter:
            _rebuild_chapter_from_name(chapter, ep)
            changed = True
        else:
            changed = set_rss_fields(chapter, ep, only_missing=True)
        if changed:
            updated += 1
            print(f"       + {title}")
    return updated


def backfill_rss_data(file_path, podcast_index=None, dry_run=False):
    """Backfill RSS metadata into existing chapters."""
    yaml = make_yaml()

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return

    indices = [podcast_index] if podcast_index is not None else range(len(data["items"]))
    total_updated = 0
    failed = []

    for idx in indices:
        if idx >= len(data["items"]):
            print(f"Error: Podcast index {idx} out of range.")
            continue

        podcast = data["items"][idx]
        pname = str(podcast.get("name", "?"))
        rss_feed = str(podcast.get("rss_feed", ""))

        if not rss_feed:
            print(f"  [{idx}] {pname}: no rss_feed, skipping.")
            continue
        if not podcast.get("chapters"):
            print(f"  [{idx}] {pname}: no chapters, skipping.")
            continue

        print(f"  [{idx}] {pname}: fetching RSS feed...")
        try:
            episodes = parse_rss_episodes(rss_feed)
        except FEED_ERRORS as e:
            print(f"       ERROR: {e}")
            failed.append(pname)
            continue
        print(f"       Found {len(episodes)} episodes in feed.")

        updated = _backfill_podcast(podcast, episodes)
        total_updated += updated
        if updated and not dry_run:
            save_yaml(yaml, data, file_path)

    if failed:
        print(f"\nFailed feeds ({len(failed)}): {', '.join(failed)}")
    if total_updated == 0:
        print("\nNo chapters needed updating.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({total_updated} would be updated) ---")
        sys.stdout.write(dump_to_string(yaml, data))
    else:
        print(f"\nSaved. Updated {total_updated} chapter(s) total.")


def main():
    parser = argparse.ArgumentParser(
        description="Backfill RSS metadata into existing podcast chapters."
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
    backfill_rss_data(args.yaml_file, args.podcast_index, args.dry_run)


if __name__ == "__main__":
    main()
