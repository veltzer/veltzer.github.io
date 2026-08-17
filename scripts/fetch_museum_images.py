#!/usr/bin/env python

"""
Fetch images for museum visits via DuckDuckGo image search with GUI picker.

Images saved as static/images/museum-{internal_id}.jpg

Incremental: skips museums that already have an image.

The data records one entry per *visit*, so the same museum can appear several
times with different internal_ids (the Met is 2 and 6, the Louvre 15 and 17).
Every visit shows the same photo, so only the lowest-numbered visit gets an
image file; later visits are skipped entirely rather than fetching a second
copy of the same picture.

plugin-museums.js resolves a repeat visit to that lowest id when it builds the
image path, so each visit still renders an image. Keep the two in step: if this
rule changes, canonicalMuseumImageId() there has to change with it.

Usage:
  scripts/fetch_museum_images.py [--force]
"""

import argparse
import os
from pathlib import Path

from image_picker import pick_image

# Resolved from this file rather than the cwd, so the script works from anywhere
# instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = str(REPO_ROOT / "static" / "images")
YAML_PATH = str(REPO_ROOT.parent / "data" / "yaml" / "museums.yaml")


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
    repeats = 0
    # Museum name -> the path already fetched for it in this run or a previous
    # one. Repeat visits reuse this id instead of searching again.
    fetched_by_name: dict[str, str] = {}

    print(f"Found {len(entries)} museums\n")

    for name, fields in entries:
        internal_id = fields.get("internal_id")
        if not internal_id:
            print(f"  WARNING: {name} has no internal_id, skipping.")
            continue

        dest = get_dest_path(internal_id)
        if os.path.exists(dest) and not args.force:
            fetched_by_name.setdefault(name, dest)
            skipped += 1
            continue

        # A previous visit to this museum already owns the image. Skip rather
        # than prompting for the same search and writing a duplicate file.
        source = fetched_by_name.get(name)
        if source and os.path.exists(source):
            print(f"  REPEAT: {name} (image is {os.path.basename(source)})")
            repeats += 1
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
            fetched_by_name[name] = dest
            downloaded += 1
        elif status == "quit":
            print("Quitting.")
            break
        else:
            skipped += 1

    print(f"\nDone: {downloaded} downloaded, {repeats} repeat visits, {skipped} skipped")


if __name__ == "__main__":
    main()
