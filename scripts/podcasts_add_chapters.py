#!/usr/bin/env python

"""
Adds chapters to a podcast entry in a YAML file using real episode data
fetched from the podcast's RSS feed.
Each run appends the next N episodes (default 10), continuing from where
the last run left off.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

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


def _set_rss_fields(chapter, ep):
    """Set RSS metadata fields on a chapter dict from an episode dict."""
    rss_fields = [
        ("description", True), ("pubDate", False), ("episodeType", False),
        ("explicit", False), ("enclosure_url", False), ("image", False),
        ("author", False), ("guid", False),
    ]
    for field, truncate in rss_fields:
        if ep[field]:
            chapter[field] = DQ(ep[field][:200] if truncate else ep[field])
    if ep["episode"] is not None:
        chapter["episode"] = ep["episode"]
    if ep["duration"] is not None:
        chapter["duration"] = ep["duration"]


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
        _set_rss_fields(chapter, ep)
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

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

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
    episodes = parse_rss_episodes(rss_feed)
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
        yaml.dump(data, sys.stdout)
    else:
        with open(file_path, "w", encoding="UTF8") as f:
            yaml.dump(data, f)
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
