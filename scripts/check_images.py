#!/usr/bin/env python

"""
Check that every media item that should have a local image actually has one
in blog/images/.

Checks:
- Movies: blog/images/movie-{imdb_id}.jpg
- Series: blog/images/series-{imdb_id}.jpg
- Audible: blog/images/audible-{asin}.jpg
- Audio Courses: blog/images/audiocourse-gc-{gc_id}.jpg
                 or audiocourse-audible-{asin}.jpg
                 or audiocourse-internal-{internal_id}.jpg
- Museums: blog/images/museum-{internal_id}.jpg
- Podcasts: blog/images/podcast-{internal_id}.jpg
- YouTube: skipped (uses external thumbnails)

Usage:
  scripts/check_images.py
"""

import gzip
import os
import sys

IMAGE_DIR = "blog/images"
DATA_DIR = "../data/yaml"


def parse_yaml_entries(path, compressed=False):
    """Parse top-level entries from a YAML file. Returns list of dicts."""
    entries = []
    current: dict[str, str] | None = None
    opener = gzip.open if compressed else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- name:") or s.startswith("- asin:") or s.startswith("- title:"):
                if current:
                    entries.append(current)
                current = {}
            if current is not None and ":" in s:
                key = s.lstrip("- ").split(":", 1)[0].strip()
                val = s.split(":", 1)[1].strip().strip("'\"")
                # Handle cover_url which has ":" in the value
                if key == "cover_url":
                    idx = line.find("cover_url:")
                    val = line[idx + len("cover_url:"):].strip().strip("'\"")
                current[key] = val
    if current:
        entries.append(current)
    return entries


def check_movies():
    """Check movie images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "video_features.yaml"))
    errors = 0
    for entry in entries:
        imdb_id = entry.get("imdb_id")
        if not imdb_id:
            continue
        path = os.path.join(IMAGE_DIR, f"movie-{imdb_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_series():
    """Check series images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "video_series.yaml"))
    errors = 0
    for entry in entries:
        imdb_id = entry.get("imdb_id")
        if not imdb_id:
            continue
        path = os.path.join(IMAGE_DIR, f"series-{imdb_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_audible():
    """Check audible images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "audible.yaml"))
    errors = 0
    for entry in entries:
        asin = entry.get("asin")
        if not asin:
            continue
        path = os.path.join(IMAGE_DIR, f"audible-{asin}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('title', '?')})")
            errors += 1
    return len(entries), errors


def check_audio_courses():
    """Check audio course images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "audio_courses.yaml"))
    errors = 0
    for entry in entries:
        gc_id = entry.get("great_courses_id")
        asin = entry.get("audible_asin")
        internal_id = entry.get("internal_id")
        name = entry.get("name", "?")
        if gc_id:
            path = os.path.join(IMAGE_DIR, f"audiocourse-gc-{gc_id}.jpg")
        elif asin:
            path = os.path.join(IMAGE_DIR, f"audiocourse-audible-{asin}.jpg")
        elif internal_id:
            path = os.path.join(IMAGE_DIR, f"audiocourse-internal-{internal_id}.jpg")
        else:
            print(f"  NO ID: {name}")
            errors += 1
            continue
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({name})")
            errors += 1
    return len(entries), errors


def check_museums():
    """Check museum images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "museums.yaml"))
    errors = 0
    for entry in entries:
        internal_id = entry.get("internal_id")
        if not internal_id:
            print(f"  NO ID: {entry.get('name', '?')}")
            errors += 1
            continue
        path = os.path.join(IMAGE_DIR, f"museum-{internal_id}.jpg")
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors


def check_podcasts():
    """Check podcast images."""
    entries = parse_yaml_entries(os.path.join(DATA_DIR, "podcasts.yaml"))
    # Only entries with internal_id are top-level podcasts (not chapters)
    podcast_entries = [e for e in entries if "internal_id" in e]
    errors = 0
    for entry in podcast_entries:
        internal_id = entry["internal_id"]
        path = os.path.join(IMAGE_DIR, f"podcast-{internal_id}.jpg")
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
