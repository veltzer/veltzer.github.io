#!/usr/bin/env python

"""
Fetch images for podcasts via DuckDuckGo image search with GUI picker.

Images saved as blog/images/podcast-{internal_id}.jpg

Incremental: skips podcasts that already have an image.

Usage:
  scripts/fetch_podcast_images.py [--force]
"""

import argparse
import os

import yaml

from image_picker import pick_image

IMAGE_DIR = "blog/images"
YAML_PATH = "../data/yaml/podcasts.yaml"


def load_entries():
    """Load top-level podcast entries from YAML."""
    with open(YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data if isinstance(data, list) else data.get("items", [])
    entries = []
    for item in items:
        name = item.get("name")
        if not name:
            continue
        fields = {k: str(v) for k, v in item.items() if k not in ("name", "chapters")}
        entries.append((name, fields))
    return entries


def main():
    parser = argparse.ArgumentParser(description="Fetch podcast images")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    args = parser.parse_args()

    os.makedirs(IMAGE_DIR, exist_ok=True)
    entries = load_entries()

    downloaded = 0
    skipped = 0

    print(f"Found {len(entries)} podcasts\n")

    for name, fields in entries:
        internal_id = fields.get("internal_id")
        if not internal_id:
            print(f"  WARNING: {name} has no internal_id, skipping.")
            continue

        dest = os.path.join(IMAGE_DIR, f"podcast-{internal_id}.jpg")
        if os.path.exists(dest) and not args.force:
            skipped += 1
            continue

        info_lines = []
        for field in ("url", "rating", "review"):
            if field in fields:
                info_lines.append(f"{field}: {fields[field]}")

        status = pick_image(
            title=name,
            info_lines=info_lines,
            search_query=f"{name} podcast logo",
            cache_key=f"podcast-{internal_id}-{name}",
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
