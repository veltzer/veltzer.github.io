#!/usr/bin/env python

"""
Fetch cover images for Audible books using the cover_url from the YAML.

Images saved as static/images/audible-{asin}.jpg

Incremental: skips books that already have an image.

Usage:
  scripts/fetch_audible_images.py [--force]
"""

import argparse
import os
import time
from pathlib import Path

from image_standard import download_image

# Resolved from this file rather than the cwd, so the script works from anywhere
# instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = str(REPO_ROOT / "static" / "images")
YAML_PATH = str(REPO_ROOT / "data" / "yaml" / "audible.yaml")


def load_entries():
    """Load audible entries with ASIN and cover_url from YAML."""
    entries = []
    current_asin: str | None = None
    current_name: str | None = None
    current_cover: str | None = None
    with open(YAML_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- asin:"):
                if current_asin and current_cover:
                    entries.append((current_name or current_asin, current_asin, current_cover))
                current_asin = s.split(":", 1)[1].strip().strip("'\"")
                current_name = None
                current_cover = None
            elif s.startswith("title:") and current_asin:
                current_name = s.split(":", 1)[1].strip().strip("'\"")
            elif s.startswith("cover_url:") and current_asin:
                current_cover = s.split(":", 1)[1].strip().strip("'\"")
    if current_asin and current_cover:
        entries.append((current_name or current_asin, current_asin, current_cover))
    return entries


def main():
    parser = argparse.ArgumentParser(description="Fetch Audible book cover images")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    args = parser.parse_args()

    os.makedirs(IMAGE_DIR, exist_ok=True)
    entries = load_entries()

    downloaded = 0
    skipped = 0
    failed = 0

    print(f"Found {len(entries)} Audible books\n")

    for name, asin, cover_url in entries:
        dest = os.path.join(IMAGE_DIR, f"audible-{asin}.jpg")
        if os.path.exists(dest) and not args.force:
            skipped += 1
            continue

        try:
            download_image(cover_url, dest)
            downloaded += 1
            print(f"  Downloaded: {name} -> {dest}")
        except OSError as e:  # ImageError and network errors: one item, not the run
            print(f"  Failed {name}: {e}")
            failed += 1

        time.sleep(0.1)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
