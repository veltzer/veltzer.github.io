#!/usr/bin/env python

"""
Backfills RSS metadata into existing podcast chapters.
For each chapter, matches by title against the RSS feed and adds:
  description, pubDate, episode, duration, episodeType, explicit,
  enclosure_url, image, author, guid.
Also renames 'name' to 'title' in chapters to match RSS field names.
"""

import argparse
import sys
import xml.etree.ElementTree as ET

import requests
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


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


def _set_rss_fields(target, ep, only_missing=False):
    """Set RSS metadata fields on a target dict from an episode dict."""
    rss_fields = [
        ("description", True), ("pubDate", False), ("episodeType", False),
        ("explicit", False), ("enclosure_url", False), ("image", False),
        ("author", False), ("guid", False),
    ]
    for field, truncate in rss_fields:
        if ep[field] and (not only_missing or field not in target):
            target[field] = DQ(ep[field][:200] if truncate else ep[field])
    if ep["episode"] is not None and (not only_missing or "episode" not in target):
        target["episode"] = ep["episode"]
    if ep["duration"] is not None and (not only_missing or "duration" not in target):
        target["duration"] = ep["duration"]


def _rebuild_chapter_from_name(chapter, ep):
    """Rebuild a chapter that has 'name' key, renaming to 'title' and adding RSS fields."""
    new_chapter = {}
    new_chapter["title"] = DQ(str(chapter["name"]))
    _set_rss_fields(new_chapter, ep)
    for key in ["date_utcz", "date_timezone", "location", "device", "rating", "review"]:
        if key in chapter:
            new_chapter[key] = chapter[key]
    chapter.clear()
    chapter.update(new_chapter)


def backfill_rss_data(file_path, podcast_index=None, dry_run=False):
    """Backfill RSS metadata into existing chapters."""
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

    total_updated = 0

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

        chapters = podcast.get("chapters", [])
        if not chapters:
            print(f"  [{idx}] {pname}: no chapters, skipping.")
            continue

        print(f"  [{idx}] {pname}: fetching RSS feed...")
        episodes = parse_rss_episodes(rss_feed)
        print(f"       Found {len(episodes)} episodes in feed.")

        # Build title lookup from episodes list by index
        for i, chapter in enumerate(chapters):
            # Get the current title (might be under 'name' or 'title')
            chapter_title = str(chapter.get("title", chapter.get("name", "")))

            # Match by position (chapter index = episode index)
            if i >= len(episodes):
                print(f"       Chapter {i} '{chapter_title}': no matching episode, skipping.")
                continue

            ep = episodes[i]

            # Rename 'name' to 'title' if needed
            if "name" in chapter:
                _rebuild_chapter_from_name(chapter, ep)
                total_updated += 1
                print(f"       + {chapter_title}")
            elif "title" in chapter and not chapter.get("guid"):
                # Already has 'title' but missing RSS data — backfill
                _set_rss_fields(chapter, ep, only_missing=True)
                total_updated += 1
                print(f"       + {chapter_title}")

    if total_updated == 0:
        print("\nNo chapters needed updating.")
        return

    if dry_run:
        print(f"\n--- Dry Run ({total_updated} would be updated) ---")
        yaml.dump(data, sys.stdout)
    else:
        with open(file_path, "w", encoding="UTF8") as f:
            yaml.dump(data, f)
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
