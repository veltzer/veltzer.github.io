#!/usr/bin/env python

"""
Fetch images for museum visits via DuckDuckGo image search with GUI picker.

Images saved as blog/images/museum-{internal_id}.jpg

Incremental: skips museums that already have an image.

Usage:
  scripts/fetch_museum_images.py [--force]
"""

import argparse
import os

from image_picker import pick_image

IMAGE_DIR = "blog/images"
YAML_PATH = "../data/yaml/museums.yaml"


def load_entries():
    """Load museum entries from YAML."""
    entries = []
    current: str | None = None
    fields: dict[str, str] = {}
    with open(YAML_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- name:"):
                if current:
                    entries.append((current, dict(fields)))
                current = s.split(":", 1)[1].strip().strip("'\"")
                fields = {}
            elif ":" in s and current:
                key, val = s.split(":", 1)
                fields[key.strip()] = val.strip().strip("'\"")
    if current:
        entries.append((current, dict(fields)))
    return entries


def get_dest_path(internal_id):
    """Get destination file path."""
    return os.path.join(IMAGE_DIR, f"museum-{internal_id}.jpg")


def main():
    parser = argparse.ArgumentParser(description="Fetch museum visit images")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    args = parser.parse_args()

    os.makedirs(IMAGE_DIR, exist_ok=True)
    entries = load_entries()

    downloaded = 0
    skipped = 0

    print(f"Found {len(entries)} museums\n")

    for name, fields in entries:
        internal_id = fields.get("internal_id")
        if not internal_id:
            print(f"  WARNING: {name} has no internal_id, skipping.")
            continue

        dest = get_dest_path(internal_id)
        if os.path.exists(dest) and not args.force:
            skipped += 1
            continue

        city = fields.get("city", "")
        info_lines = []
        for field in ("city", "rating", "review", "date_utcz", "url"):
            if field in fields:
                info_lines.append(f"{field}: {fields[field]}")

        search_query = f"{name} museum {city}"
        cache_key = f"museum-{internal_id}-{name}"

        status = pick_image(
            title=name,
            info_lines=info_lines,
            search_query=search_query,
            cache_key=cache_key,
            dest_path=dest,
        )

        if status == "found":
            downloaded += 1
        elif status == "quit":
            print("Quitting.")
            break
        else:
            skipped += 1

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped")


if __name__ == "__main__":
    main()
