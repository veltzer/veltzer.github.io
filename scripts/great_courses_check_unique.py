#!/usr/bin/env python

"""
Check that all great_courses_id and great_courses_slug values
in the audio courses YAML are unique.

Usage:
  scripts/great_courses_check_unique.py
"""

import sys

import yaml

YAML_PATH = "data/yaml/audio_courses.yaml"


def main():
    ids = {}
    slugs = {}
    errors = 0

    with open(YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for n, item in enumerate(data["items"], 1):
        name = f"{item.get('name')} (item {n})"
        if "great_courses_id" in item:
            value = item["great_courses_id"]
            if value in ids:
                print(f"Duplicate great_courses_id {value}:")
                print(f"  {ids[value]}")
                print(f"  {name}")
                errors += 1
            else:
                ids[value] = name
        if "great_courses_slug" in item:
            value = item["great_courses_slug"]
            if value in slugs:
                print(f"Duplicate great_courses_slug \"{value}\":")
                print(f"  {slugs[value]}")
                print(f"  {name}")
                errors += 1
            else:
                slugs[value] = name

    if errors:
        print(f"\n{errors} duplicate(s) found.")
        sys.exit(1)
    else:
        print(f"OK: {len(ids)} IDs and {len(slugs)} slugs, all unique.")


if __name__ == "__main__":
    main()
