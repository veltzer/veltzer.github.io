#!/usr/bin/env python

"""
Check that lecturer names in the YAML match the professor names
on The Great Courses website for courses that have a great_courses_slug.

Usage:
  scripts/check_audio_courses_lecturers.py
"""

import re
import sys
import time
import urllib.error
import urllib.request

YAML_PATH = "data/yaml/audio_courses.yaml"
COURSE_PAGE_URL = "https://shop.thegreatcourses.com/{slug}"
PROF_RE = re.compile(r"professor-name[^>]*>([^<]+)")


def fetch_professor(slug):
    """Fetch professor name from a Great Courses page."""
    url = COURSE_PAGE_URL.format(slug=slug)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  Could not fetch {slug}: {e}", file=sys.stderr)
        return None
    m = PROF_RE.search(html)
    return m.group(1).strip() if m else None


def normalize(name):
    """Normalize a name for comparison: lowercase, remove dots/extra spaces."""
    return re.sub(r"\s+", " ", name.replace(".", "").lower().strip())


def load_entries():
    """Load entries with slug and lecturers from YAML."""
    entries = []
    current = None
    fields = {}
    with open(YAML_PATH, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("- name:"):
                if current and fields.get("great_courses_slug"):
                    entries.append((current, dict(fields)))
                current = stripped.split(":", 1)[1].strip().strip("'\"")
                fields = {}
            elif ":" in stripped and current:
                key, val = stripped.split(":", 1)
                fields[key.strip()] = val.strip().strip("'\"")
    if current and fields.get("great_courses_slug"):
        entries.append((current, dict(fields)))
    return entries


def main():
    entries = load_entries()
    print(f"Checking {len(entries)} courses with Great Courses slugs\n")

    mismatches = 0
    checked = 0

    for name, fields in entries:
        slug = fields["great_courses_slug"]
        lecturers_raw = fields.get("lecturers", "")
        # Parse lecturers list from YAML string like ["Name1", "Name2"]
        yaml_names = re.findall(r'"([^"]+)"', lecturers_raw)
        if not yaml_names:
            yaml_names = [lecturers_raw.strip("[]")]

        professor = fetch_professor(slug)
        time.sleep(0.3)
        checked += 1

        if not professor:
            print(f"  {name}: could not fetch professor from site")
            continue

        # Check if any YAML lecturer matches the site professor
        normalized_prof = normalize(professor)
        matched = any(normalize(n) == normalized_prof for n in yaml_names)

        if not matched:
            # Try partial match (last name)
            prof_parts = normalized_prof.split()
            partial = any(
                prof_parts[-1] in normalize(n)
                for n in yaml_names
            ) if prof_parts else False

            if partial:
                print(f"  {name}: PARTIAL MATCH")
                print(f"    YAML:  {yaml_names}")
                print(f"    Site:  {professor}")
            else:
                print(f"  {name}: MISMATCH")
                print(f"    YAML:  {yaml_names}")
                print(f"    Site:  {professor}")
                mismatches += 1

    if mismatches:
        print(f"\n{mismatches} mismatch(es) found out of {checked} checked.")
        sys.exit(1)
    else:
        print(f"\nOK: all {checked} courses checked, no mismatches.")


if __name__ == "__main__":
    main()
