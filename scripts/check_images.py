#!/usr/bin/env python

"""
Check that every media item that should have a local image actually has one
in static/images/.

Checks:
- Movies: static/images/movie-{imdb_id}.jpg
- Series: static/images/series-{imdb_id}.jpg
- Museums: static/images/museum-{internal_id}.jpg
- Concerts: static/images/{image}, the file each show names

Usage:
  scripts/check_images.py [--output-files STAMP]

The build runs it as an explicit step (rsconstruct.toml), which appends
--inputs and --output-files: the inputs are only there so the build reruns it
when one changes, and the stamp is written empty when every image is present.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

# Resolved from this file rather than the cwd, so the script works from
# anywhere instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
# static/images, not blog/images: the 2026-08 migration moved the image tree and
# this path was never updated, so the check reported all 312 images missing.
IMAGE_DIR = REPO_ROOT / "static" / "images"
DATA_DIR = REPO_ROOT / "data" / "yaml"


def parse_yaml_entries(path):
    """Load the item list from a YAML file. Returns a list of dicts.

    Uses yaml.safe_load rather than scanning lines: the previous hand-rolled
    parser split on the first ":" and would mangle multi-line values, quoted
    strings containing colons, and comments.
    """
    with open(path, "rt", encoding="utf-8") as handle:
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



def check_museums():
    """Check museum images.

    One entry per visit, so a museum visited twice has two entries. Only the
    lowest-numbered visit owns an image file, which repeat visits share, so
    only the first visit to each museum is checked here.
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


def check_concerts():
    """Check concert images: every show names one; shows may share a file."""
    entries = parse_yaml_entries(os.path.join(str(DATA_DIR), "concerts.yaml"))
    errors = 0
    for entry in entries:
        image = entry.get("image")
        if not image:
            print(f"  NO IMAGE: {entry.get('name', '?')}")
            errors += 1
            continue
        path = os.path.join(str(IMAGE_DIR), image)
        if not os.path.exists(path):
            print(f"  MISSING: {path} ({entry.get('name', '?')})")
            errors += 1
    return len(entries), errors



def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--inputs", nargs="*", default=[])
    parser.add_argument("--output-files", nargs="*", type=Path, default=[])
    args = parser.parse_args()
    total_errors = 0
    checks = [
        ("Movies", check_movies),
        ("Series", check_series),
        ("Museums", check_museums),
        ("Concerts", check_concerts),
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
    print("All images present.")
    for stamp in args.output_files:
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.write_text("")


if __name__ == "__main__":
    main()
