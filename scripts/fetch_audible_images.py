#!/usr/bin/env python

"""
Fetch cover images for Audible books using the cover_url from the YAML.

Images saved as blog/images/audible-{asin}.jpg

Incremental: skips books that already have an image.

Usage:
  scripts/fetch_audible_images.py [--force]
"""

import argparse
import os
import time
import urllib.error
import urllib.request

IMAGE_DIR = "blog/images"
YAML_PATH = "../data/yaml/audible.yaml"


def download(url, dest):
    """Download a URL to a file."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


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
                # cover_url value contains ":" so re-join
                idx = line.find("cover_url:")
                current_cover = line[idx + len("cover_url:"):].strip().strip("'\"")
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
            download(cover_url, dest)
            downloaded += 1
            print(f"  Downloaded: {name} -> {dest}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            print(f"  Failed {name}: {e}")
            failed += 1

        time.sleep(0.1)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
