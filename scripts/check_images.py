#!/usr/bin/env python

"""
Check that every media item that should have a local image actually has one
in static/images/.

Checks:
- Movies: static/images/movie-{imdb_id}.jpg
- Series: static/images/series-{imdb_id}.jpg
- Audible: static/images/audible-{asin}.jpg
- Audio Courses: static/images/audiocourse-gc-{gc_id}.jpg
                 or audiocourse-audible-{asin}.jpg
                 or audiocourse-internal-{internal_id}.jpg
- Museums: static/images/museum-{internal_id}.jpg
- Podcasts: static/images/podcast-{internal_id}.jpg
- YouTube: skipped (uses external thumbnails)

Usage:
  scripts/check_images.py
"""

import gzip
import logging
import os
import sys
from pathlib import Path

import yaml

# Resolved from this file rather than the cwd, so the script works from
# anywhere instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
# static/images, not blog/images: the zola migration moved the image tree and
# this path was never updated, so the check reported all 312 images missing.
IMAGE_DIR = REPO_ROOT / "static" / "images"
DATA_DIR = REPO_ROOT.parent / "data" / "yaml"

logger = logging.getLogger(__name__)


def parse_yaml_entries(path, compressed=False):
    """Load the item list from a YAML file. Returns a list of dicts.

    Uses yaml.safe_load rather than scanning lines: the previous hand-rolled
    parser split on the first ":" and would mangle multi-line values, quoted
    strings containing colons, and comments.
    """
    opener = gzip.open if compressed else open
    with opener(path, "rt", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not data:
        return []
    items = data.get("items", data) if isinstance(data, dict) else data
    return [item for item in items if isinstance(item, dict)]


def check_movies():
    """Check movie images."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "video_features.yaml"))
    errors = 0
    for entry in entries:
        imdb_id = entry.get("imdb_id")
        if not imdb_id:
            continue
        path = os.path.join(str(IMAGE_DIR), f"movie-{imdb_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_series():
    """Check series images."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "video_series.yaml"))
    errors = 0
    for entry in entries:
        imdb_id = entry.get("imdb_id")
        if not imdb_id:
            continue
        path = os.path.join(str(IMAGE_DIR), f"series-{imdb_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_audible():
    """Check audible images."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "audible.yaml"))
    errors = 0
    for entry in entries:
        asin = entry.get("asin")
        if not asin:
            continue
        path = os.path.join(str(IMAGE_DIR), f"audible-{asin}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('title', '?')})")
            errors += 1
    return len(entries), errors


def check_audio_courses():
    """Check audio course images."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "audio_courses.yaml"))
    errors = 0
    for entry in entries:
        gc_id = entry.get("great_courses_id")
        asin = entry.get("audible_asin")
        internal_id = entry.get("internal_id")
        name = entry.get("name", "?")
        if gc_id:
            path = os.path.join(str(IMAGE_DIR), f"audiocourse-gc-{gc_id}.jpg")
        elif asin:
            path = os.path.join(str(IMAGE_DIR), f"audiocourse-audible-{asin}.jpg")
        elif internal_id:
            path = os.path.join(str(IMAGE_DIR), f"audiocourse-internal-{internal_id}.jpg")
        else:
            print(f"  NO ID: {name}")
            errors += 1
            continue
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({name})")
            errors += 1
    return len(entries), errors


def check_museums():
    """Check museum images.

    One entry per visit, so a museum visited twice has two entries. Only the
    lowest-numbered visit owns an image file -- repeat visits render that same
    image via canonicalMuseumImageId() in plugin-museums.js -- so only the
    first visit to each museum is checked here.
    """
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "museums.yaml"))
    errors = 0
    owns_image = {}
    for entry in entries:
        name = entry.get("name")
        internal_id = entry.get("internal_id")
        if not name or not internal_id:
            continue
        if name not in owns_image or internal_id < owns_image[name]:
            owns_image[name] = internal_id
    expected = set(owns_image.values())
    for entry in entries:
        internal_id = entry.get("internal_id")
        if not internal_id:
            print(f"  NO ID: {entry.get('name', '?')}")
            errors += 1
            continue
        if internal_id not in expected:
            continue
        path = os.path.join(str(IMAGE_DIR), f"museum-{internal_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_podcasts():
    """Check podcast images."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "podcasts.yaml"))
    # Only entries with internal_id are top-level podcasts (not chapters)
    podcast_entries = [e for e in entries if "internal_id" in e]
    errors = 0
    for entry in podcast_entries:
        internal_id = entry["internal_id"]
        path = os.path.join(str(IMAGE_DIR), f"podcast-{internal_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(podcast_entries), errors


def main():
    total_errors = 0
    checks = [
        ("Movies", check_movies),
        ("Series", check_series),
        ("Audible", check_audible),
        ("Audio Courses", check_audio_courses),
        ("Museums", check_museums),
        ("Podcasts", check_podcasts),
    ]

    for label, check_fn in checks:
        print(f"Checking {label}...")
        count, errors = check_fn()
        if errors:
            print(f"  {errors} missing out of {count}")
        else:
            print(f"  OK ({count} items)")
        total_errors += errors

    print()
    if total_errors:
        print(f"FAILED: {total_errors} missing image(s)")
        sys.exit(1)
    else:
        print("All images present.")


if __name__ == "__main__":
    main()
