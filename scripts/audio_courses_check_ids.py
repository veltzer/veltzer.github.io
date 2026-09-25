#!/usr/bin/env python

"""
Check that every audio course has at least one identifier:
great_courses_id, audible_asin, or internal_id.

Usage:
  scripts/check_audio_courses_ids.py
"""

import sys

YAML_PATH = "data/yaml/audio_courses.yaml"


def main():
    current = None
    has_gc = False
    has_audible = False
    has_internal = False
    errors = 0
    total = 0

    with open(YAML_PATH, encoding="utf-8") as f:
        for _, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith("- name:"):
                if current and not (has_gc or has_audible or has_internal):
                    print(f"Missing ID: {current}")
                    errors += 1
                current = stripped.split(":", 1)[1].strip().strip("'\"")
                if current:
                    total += 1
                has_gc = False
                has_audible = False
                has_internal = False
            elif stripped.startswith("great_courses_id:"):
                has_gc = True
            elif stripped.startswith("audible_asin:"):
                has_audible = True
            elif stripped.startswith("internal_id:"):
                has_internal = True

    # Check last entry
    if current and not (has_gc or has_audible or has_internal):
        print(f"Missing ID: {current}")
        errors += 1

    if errors:
        print(f"\n{errors} course(s) out of {total} have no ID.")
        sys.exit(1)
    else:
        print(f"OK: all {total} courses have at least one ID.")


if __name__ == "__main__":
    main()
