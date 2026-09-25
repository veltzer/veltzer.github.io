#!/usr/bin/env python

"""
Replaces numeric chapter titles ("1", "2", "3"...) with real episode data
fetched from the podcast's RSS feed. Non-numeric titles (e.g. "Trailer")
are left unchanged. Also backfills all RSS metadata fields.
"""

import argparse
import sys
import xml.etree.ElementTree as ET

import requests
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def duration_to_seconds(val):
    """Convert a duration string (seconds or HH:MM:SS or MM:SS) to integer seconds."""
    s = str(val).strip()
    if ":" in s:
        parts = [int(p) for p in s.split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
    return int(s)


def parse_rss_episodes(rss_url):
    """
    Fetch and parse all episodes from an RSS feed.
    Returns a list of dicts in chronological order (oldest first).
    """
    resp = requests.get(rss_url, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = root.findall(".//item")
    episodes = []
    for item in items:
        ep = {}
        title_el = item.find("title")
        ep["title"] = title_el.text.strip() if title_el is not None and title_el.text else ""

        desc_el = item.find("description")
        ep["description"] = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

        pub_el = item.find("pubDate")
        ep["pubDate"] = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

        episode_el = item.find(f"{{{ITUNES_NS}}}episode")
        if episode_el is not None and episode_el.text and episode_el.text.strip().isdigit():
            ep["episode"] = int(episode_el.text.strip())
        else:
            ep["episode"] = None

        dur_el = item.find(f"{{{ITUNES_NS}}}duration")
        ep["duration"] = duration_to_seconds(dur_el.text) if dur_el is not None and dur_el.text else None

        etype_el = item.find(f"{{{ITUNES_NS}}}episodeType")
        ep["episodeType"] = etype_el.text.strip() if etype_el is not None and etype_el.text else ""

        explicit_el = item.find(f"{{{ITUNES_NS}}}explicit")
        ep["explicit"] = explicit_el.text.strip() if explicit_el is not None and explicit_el.text else ""

        enc_el = item.find("enclosure")
        ep["enclosure_url"] = enc_el.get("url", "") if enc_el is not None else ""

        img_el = item.find(f"{{{ITUNES_NS}}}image")
        ep["image"] = img_el.get("href", "") if img_el is not None else ""

        author_el = item.find(f"{{{ITUNES_NS}}}author")
        ep["author"] = author_el.text.strip() if author_el is not None and author_el.text else ""

        guid_el = item.find("guid")
        ep["guid"] = guid_el.text.strip() if guid_el is not None and guid_el.text else ""

        episodes.append(ep)
    episodes.reverse()
    return episodes


def _backfill_rss_fields(chapter, ep):
    """Backfill missing RSS metadata fields into a chapter."""
    rss_fields = [
        ("description", True), ("pubDate", False), ("episodeType", False),
        ("explicit", False), ("enclosure_url", False), ("image", False),
        ("author", False), ("guid", False),
    ]
    for field, truncate in rss_fields:
        if ep[field] and field not in chapter:
            chapter[field] = DQ(ep[field][:200] if truncate else ep[field])
    if ep["episode"] is not None and "episode" not in chapter:
        chapter["episode"] = ep["episode"]
    if ep["duration"] is not None and "duration" not in chapter:
        chapter["duration"] = ep["duration"]


def _process_podcast(data, idx):
    """Process a single podcast, renaming numeric chapter titles. Returns count of renamed chapters."""
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
    episodes = parse_rss_episodes(rss_feed)
    print(f"       Found {len(episodes)} episodes in feed.")

    renamed = 0
    for _, chapter in numeric_chapters:
        num = int(str(chapter[title_key]))
        if num < len(episodes):
            ep = episodes[num]
            old_title = str(chapter[title_key])
            chapter[title_key] = DQ(ep["title"])
            _backfill_rss_fields(chapter, ep)
            print(f"       {old_title} -> {ep['title']}")
            renamed += 1
        else:
            print(f"       {num}: out of range (only {len(episodes)} episodes), skipping.")

    print(f"       Renamed {renamed} chapter(s).")
    return renamed


def fill_chapter_names(file_path, podcast_index=None, dry_run=False):
    """
    Replace numeric chapter titles with real episode data from RSS.
    If podcast_index is None, process all podcasts.
    """
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

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
    for idx in indices:
        total_renamed += _process_podcast(data, idx)

    if total_renamed == 0:
        print("\nNo chapters needed renaming.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({total_renamed} would be renamed) ---")
        yaml.dump(data, sys.stdout)
    else:
        with open(file_path, "w", encoding="UTF8") as f:
            yaml.dump(data, f)
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
