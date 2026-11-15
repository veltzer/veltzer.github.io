#!/usr/bin/env python

"""
Check that every audio course has at least one identifier:
great_courses_id, audible_asin, or internal_id.

Usage:
  scripts/audio_courses_check_ids.py
"""

import sys

import yaml

YAML_PATH = "data/yaml/audio_courses.yaml"
ID_KEYS = ("great_courses_id", "audible_asin", "internal_id")


def main():
    with open(YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    errors = 0
    total = 0
    for item in data["items"]:
        total += 1
        if not any(key in item for key in ID_KEYS):
            print(f"Missing ID: {item.get('name')}")
            errors += 1

    if errors:
        print(f"\n{errors} course(s) out of {total} have no ID.")
        sys.exit(1)
    else:
        print(f"OK: all {total} courses have at least one ID.")


if __name__ == "__main__":
    main()
