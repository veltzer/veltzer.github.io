#!/usr/bin/env python

"""
Check that all great_courses_id and great_courses_slug values
in the audio courses YAML are unique.

Usage:
  scripts/check_great_courses_unique.py
"""

import sys

YAML_PATH = "data/yaml/audio_courses.yaml"


def main():
    ids = {}
    slugs = {}
    errors = 0

    with open(YAML_PATH, encoding="utf-8") as f:
        current_name = None
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith("- name:"):
                current_name = stripped.split(":", 1)[1].strip().strip("'\"")
            elif stripped.startswith("great_courses_id:"):
                value = stripped.split(":", 1)[1].strip()
                if value in ids:
                    print(f"Duplicate great_courses_id {value}:")
                    print(f"  {ids[value]}")
                    print(f"  {current_name} (line {lineno})")
                    errors += 1
                else:
                    ids[value] = f"{current_name} (line {lineno})"
            elif stripped.startswith("great_courses_slug:"):
                value = stripped.split(":", 1)[1].strip().strip("'\"")
                if value in slugs:
                    print(f"Duplicate great_courses_slug \"{value}\":")
                    print(f"  {slugs[value]}")
                    print(f"  {current_name} (line {lineno})")
                    errors += 1
                else:
                    slugs[value] = f"{current_name} (line {lineno})"

    if errors:
        print(f"\n{errors} duplicate(s) found.")
        sys.exit(1)
    else:
        print(f"OK: {len(ids)} IDs and {len(slugs)} slugs, all unique.")


if __name__ == "__main__":
    main()
