#!/usr/bin/env python

"""
Look up Great Courses IDs and slugs by searching shop.thegreatcourses.com.

For each audio course in the YAML that lacks a great_courses_id,
searches by title (or uses existing slug), extracts the numeric ID
from the course page, and asks for confirmation before writing it.

Incremental: skips entries that already have both great_courses_id and
great_courses_slug. Writes after each confirmed entry so progress is not lost.

Usage:
  scripts/fetch_great_courses_ids.py [--dry-run]
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

YAML_PATH = "data/yaml/audio_courses.yaml"
CACHE_PATH = "/tmp/great_courses_cache.json"
SEARCH_URL = "https://shop.thegreatcourses.com/catalogsearch/result/?q={query}"
COURSE_PAGE_URL = "https://shop.thegreatcourses.com/{slug}"
RESULT_RE = re.compile(
    r'data-product-sku="(\d+)"(.*?)(?=data-product-sku|</section)',
    re.DOTALL,
)
TITLE_RE = re.compile(r'<span class="title">([^<]+)</span>')
DESC_RE = re.compile(r"<p>([^<]+)</p>")
SLUG_RE = re.compile(r'href="https://shop\.thegreatcourses\.com/([^"?]+)"')
PROF_RE = re.compile(r'professor-name[^>]*>([^<]+)')
PAGE_IMAGE_ID_RE = re.compile(r'secureimages\.teach12\.com/tgc/images/m2/wondrium/courses/(\d+)/\d+\.jpg')
IMAGE_BASE = "https://secureimages.teach12.com/tgc/images/m2/wondrium/courses"


def load_cache():
    """Load search cache from disk."""
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache):
    """Save search cache to disk."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def fetch_page(url):
    """Fetch a URL and return HTML or None."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return None


def fetch_course_page(slug, cache):
    """Fetch course page details by slug. Returns dict with id, title, professor, description."""
    cache_key = f"page:{slug}"
    if cache_key in cache:
        return cache[cache_key]

    html = fetch_page(COURSE_PAGE_URL.format(slug=slug))
    if not html:
        return None

    sku_match = PAGE_IMAGE_ID_RE.search(html)
    prof_match = PROF_RE.search(html)
    title_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)

    result = {
        "id": sku_match.group(1) if sku_match else None,
        "title": title_match.group(1).strip() if title_match else None,
        "professor": prof_match.group(1).strip() if prof_match else None,
        "description": desc_match.group(1).strip()[:200] if desc_match else None,
        "slug": slug,
    }
    cache[cache_key] = result
    save_cache(cache)
    return result


def search_course(title, cache):
    """Search The Great Courses site. Returns dict with id, title, slug, description or None."""
    cache_key = f"search:{title}"
    if cache_key in cache:
        return cache[cache_key]

    query = urllib.parse.quote_plus(title)
    url = SEARCH_URL.format(query=query)
    html = fetch_page(url)
    if not html:
        print(f"  Search failed for: {title}", file=sys.stderr)
        return None

    m = RESULT_RE.search(html)
    if not m:
        cache[cache_key] = None
        save_cache(cache)
        return None

    card = m.group(2)
    t = TITLE_RE.search(card)
    d = DESC_RE.search(card)
    s = SLUG_RE.search(card)

    result = {
        "id": m.group(1),
        "title": t.group(1).strip() if t else "(unknown)",
        "slug": s.group(1) if s else None,
        "description": d.group(1).strip()[:200] if d else None,
    }
    cache[cache_key] = result
    save_cache(cache)
    return result


_image_proc = None


def show_image(course_id):
    """Open the course image in an external viewer window."""
    global _image_proc  # pylint: disable=global-statement
    close_image()
    url = f"{IMAGE_BASE}/{course_id}/{course_id}.jpg"
    import tempfile  # pylint: disable=import-outside-toplevel
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
            urllib.request.urlretrieve(url, tmp_path)
        _image_proc = subprocess.Popen(  # pylint: disable=consider-using-with
            ["eog", tmp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, OSError):
        pass


def close_image():
    """Close the image viewer if open."""
    global _image_proc  # pylint: disable=global-statement
    if _image_proc is not None:
        _image_proc.terminate()
        _image_proc.wait()
        _image_proc = None


def read_yaml():
    """Read YAML file lines."""
    with open(YAML_PATH, encoding="utf-8") as f:
        return f.readlines()


def write_yaml(lines):
    """Write YAML file lines."""
    with open(YAML_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def find_entries(lines):
    """Find course entries: list of (line_index, name, needs_work, yaml_fields)."""
    entries = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- name:"):
            continue
        name = stripped.split(":", 1)[1].strip().strip("'\"")
        if not name:
            continue
        has_id = False
        has_slug = False
        fields = {}
        for j in range(i + 1, min(i + 20, len(lines))):
            fline = lines[j].strip()
            if fline.startswith("- name:"):
                break
            if fline.startswith("great_courses_id:"):
                has_id = True
            if fline.startswith("great_courses_slug:"):
                has_slug = True
            if ":" in fline:
                key, val = fline.split(":", 1)
                fields[key.strip()] = val.strip().strip("'\"")
        # Needs work if missing either id or slug
        needs_work = not (has_id and has_slug)
        entries.append((i, name, needs_work, fields))
    return entries


def show_match(name, yaml_fields, result):
    """Display course info for user to compare."""
    print(f"\n  YOUR YAML:   {name}")
    if "lecturers" in yaml_fields:
        print(f"    lecturers: {yaml_fields['lecturers']}")

    print("  FOUND MATCH:")
    if result.get("title"):
        print(f"    title:     {result['title']}")
    if result.get("id"):
        print(f"    id:        {result['id']}")
    if result.get("slug"):
        print(f"    slug:      {result['slug']}")
        print(f"    page:      https://shop.thegreatcourses.com/{result['slug']}")
    if result.get("professor"):
        print(f"    professor: {result['professor']}")
    if result.get("description"):
        print(f"    about:     {result['description']}")
    if result.get("id"):
        print(f"    image:     {IMAGE_BASE}/{result['id']}/{result['id']}.jpg")


def find_entry_range(lines, name):
    """Find start and end line index of a course entry by name. Returns (start, end) or (None, None)."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- name:"):
            continue
        entry_name = stripped.split(":", 1)[1].strip().strip("'\"")
        if entry_name != name:
            continue
        end = i + 1
        while end < len(lines):
            if lines[end].strip().startswith("- name:"):
                break
            end += 1
        # Back up past blank lines
        while end > i + 1 and lines[end - 1].strip() == "":
            end -= 1
        return i, end
    return None, None


def write_course_data(name, course_id, slug):
    """Write great_courses_id and great_courses_slug at end of entry."""
    lines = read_yaml()
    start_idx, end_idx = find_entry_range(lines, name)
    if end_idx is None:
        print("  WARNING: Could not find entry in file (already added?)\n")
        return False
    # Check what already exists in this entry
    entry_text = "".join(lines[start_idx:end_idx])
    to_insert = []
    if "great_courses_id:" not in entry_text and course_id:
        to_insert.append(f"    great_courses_id: {course_id}\n")
    if "great_courses_slug:" not in entry_text and slug:
        to_insert.append(f"    great_courses_slug: \"{slug}\"\n")
    if not to_insert:
        print("  Nothing new to write.\n")
        return True
    for line in reversed(to_insert):
        lines.insert(end_idx, line)
    write_yaml(lines)
    print("  Written.\n")
    return True


def rename_course(old_name, new_name):
    """Rename a course's name field in the YAML."""
    lines = read_yaml()
    idx, _ = find_entry_range(lines, old_name)
    if idx is None:
        print("  WARNING: Could not find entry to rename.\n")
        return False
    lines[idx] = lines[idx].replace(old_name, new_name, 1)
    write_yaml(lines)
    print(f"  Renamed to: {new_name}")
    return True


def enrich_with_page(result, cache):
    """Enrich a result dict with course page details if slug is available."""
    slug = result.get("slug")
    if not slug:
        return
    page_info = fetch_course_page(slug, cache)
    if not page_info:
        return
    if page_info.get("id"):
        result["id"] = page_info["id"]
    if page_info.get("professor"):
        result["professor"] = page_info["professor"]
    if page_info.get("title"):
        result.setdefault("title", page_info["title"])
    if page_info.get("description"):
        result.setdefault("description", page_info["description"])


def lookup_course(name, yaml_fields, cache):
    """Look up course info. Priority: existing ID > existing slug > search."""
    existing_id = yaml_fields.get("great_courses_id")
    existing_slug = yaml_fields.get("great_courses_slug")

    have = []
    need = []
    if existing_id:
        have.append(f"id={existing_id}")
    else:
        need.append("ID")
    if existing_slug:
        have.append(f"slug={existing_slug}")
    else:
        need.append("SLUG")
    print(f"  >>> Have: {', '.join(have) or 'nothing'}  |  Need: {', '.join(need)} <<<")

    # 1. If we have an ID and slug, enrich with page details
    if existing_id and existing_slug:
        result = {"id": existing_id, "slug": existing_slug}
        enrich_with_page(result, cache)
        return result

    # 2. If we have a slug but no ID, fetch the course page for the ID
    if existing_slug:
        result = fetch_course_page(existing_slug, cache)
        if result:
            result["slug"] = existing_slug
            return result

    # 3. If we have an ID but no slug, search to find the slug
    if existing_id:
        search_result = search_course(name, cache)
        result = {"id": existing_id, "slug": search_result.get("slug") if search_result else None}
        enrich_with_page(result, cache)
        return result

    # 4. Fall back to search for both
    result = search_course(name, cache)
    if not result:
        return None
    time.sleep(0.3)
    enrich_with_page(result, cache)
    return result


def is_rejected(name, cache):
    """Check if this course was previously rejected by the user."""
    return cache.get(f"rejected:{name}") is True


def reject_entry(name, cache):
    """Mark a course as rejected in the cache."""
    cache[f"rejected:{name}"] = True
    save_cache(cache)


def prompt_user(name, result, cache):
    """Prompt user to accept/reject/rename. Returns (action, name) where action is y/n/r/q."""
    titles_match = (
        result.get("title")
        and name.lower().strip() == result["title"].lower().strip()
    )
    if titles_match:
        prompt = "  Accept? [y/N/q] "
    else:
        prompt = "  Accept? [y/N/r/q] (r=rename to match) "

    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return "q", name

    if answer == "q":
        return "q", name
    if answer in ("r", "rename") and not titles_match:
        rename_course(name, result["title"])
        return "y", result["title"]
    if answer not in ("y", "yes"):
        reject_entry(name, cache)
        print("  Skipped.\n")
        return "n", name
    return "y", name


def process_entry(name, yaml_fields, cache, dry_run):
    """Process a single entry. Returns 'found', 'skipped', 'not_found', or 'quit'."""
    close_image()

    has_partial = yaml_fields.get("great_courses_id") or yaml_fields.get("great_courses_slug")
    if is_rejected(name, cache) and not has_partial:
        print(f"Skipping (previously rejected): {name}")
        return "skipped"

    print(f"Looking up: {name}")
    result = lookup_course(name, yaml_fields, cache)
    time.sleep(0.5)

    if not result:
        print("  NOT FOUND\n")
        return "not_found"

    show_match(name, yaml_fields, result)
    if result.get("id"):
        show_image(result["id"])

    if dry_run:
        print("  (dry run — not writing)\n")
        return "found"

    action, name = prompt_user(name, result, cache)
    if action == "q":
        return "quit"
    if action == "n":
        return "skipped"

    if write_course_data(name, result.get("id"), result.get("slug")):
        return "found"
    return "not_found"


def main():
    parser = argparse.ArgumentParser(description="Fetch Great Courses IDs and slugs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be added without modifying the file")
    args = parser.parse_args()

    lines = read_yaml()
    entries = find_entries(lines)
    to_process = [(name, fields) for _, name, needs_work, fields in entries if needs_work]

    done = sum(1 for _, _, needs_work, _ in entries if not needs_work)
    print(f"Found {len(entries)} courses, {done} complete, "
          f"{len(to_process)} to look up\n")

    if not to_process:
        print("Nothing to do.")
        return

    cache = load_cache()
    found = 0
    skipped_by_user = 0
    not_found = 0

    for name, yaml_fields in to_process:
        status = process_entry(name, yaml_fields, cache, args.dry_run)
        if status == "found":
            found += 1
        elif status == "skipped":
            skipped_by_user += 1
        elif status == "not_found":
            not_found += 1
        elif status == "quit":
            print("Quitting.")
            break

    close_image()
    print(f"\nDone: {found} added, {skipped_by_user} skipped by user, {not_found} not found")


if __name__ == "__main__":
    main()
