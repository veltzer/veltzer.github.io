#!/usr/bin/env python

"""
Fetch cover images for all audio courses.

Priority:
1. great_courses_id -> download from Great Courses CDN
   -> audiocourse-gc-{id}.jpg
2. audible_asin -> download from Audible page (og:image)
   -> audiocourse-audible-{asin}.jpg
3. Neither -> DuckDuckGo image search with GUI picker
   -> audiocourse-internal-{n}.jpg

Usage:
  scripts/fetch_audiocourse_images.py [--force]
"""

import argparse
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import image_picker
import yaml
from bs4 import BeautifulSoup
from image_standard import normalise

# Resolved from this file rather than the cwd, so the script works from
# anywhere instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = str(REPO_ROOT / "blog" / "images")

logger = logging.getLogger(__name__)
GC_IMAGE_URL = "https://secureimages.teach12.com/tgc/images/m2/wondrium/courses/{cid}/{cid}.jpg"
AUDIBLE_URL = "https://www.audible.com/pd/{asin}"
YAML_PATH = str(REPO_ROOT.parent / "data" / "yaml" / "audio_courses.yaml")

def download(url, dest):
    """Download a URL to a file."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=15) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    # Normalise to the site standard; see scripts/image_standard.py.
    normalise(dest)


def fetch_audible_image_url(asin):
    """Fetch the og:image URL from an Audible page."""
    url = AUDIBLE_URL.format(asin=asin)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        logger.error("  Audible fetch failed: %s", e)
        return None
    # Parsed rather than regexed: the previous pattern required exactly one
    # space and attributes in property-then-content order, so any markup change
    # on Audible's side silently returned None instead of the image.
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", property="og:image")
    if tag is None:
        tag = soup.find("meta", attrs={"name": "og:image"})
    content = tag.get("content") if tag else None
    return content or None


def load_entries():
    """Load course entries from YAML as (name, fields) pairs.

    Uses yaml.safe_load rather than scanning lines: the previous hand-rolled
    parser split on the first ":" and would mangle quoted values containing
    colons, multi-line values and comments. It also silently dropped any entry
    whose first key was not "name".
    """
    with open(YAML_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not data:
        return []
    items = data.get("items", data) if isinstance(data, dict) else data
    entries = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name is None:
            continue
        fields = {k: v for k, v in item.items() if v is not None}
        entries.append((str(name), fields))
    return entries


def get_dest_path(entry_type, entry_id):
    """Get destination file path."""
    return os.path.join(IMAGE_DIR, f"audiocourse-{entry_type}-{entry_id}.jpg")



def handle_image_search(name, fields, force):
    """Search for images and show the shared browser picker."""
    internal_id = fields.get("internal_id")
    if not internal_id:
        logger.warning("  %s has no internal_id, skipping.", name)
        return "skip"

    dest = get_dest_path("internal", internal_id)
    if os.path.exists(dest) and not force:
        return "skip"

    logger.info("")
    logger.info("  No external ID for: %s (internal_id: %s)", name, internal_id)
    info_lines = []
    for field in ("lecturers", "rating", "review", "device", "location", "progress"):
        if field in fields:
            info_lines.append(f"{field + ':':11s} {fields[field]}")
            logger.info("    %s", info_lines[-1])

    # Delegates to image_picker rather than re-implementing the search, cache
    # and tkinter browser. That copy also lacked the shared version's
    # window-close and SIGINT handling, so quitting the picker left it hanging.
    return image_picker.pick_image(
        title=f"Pick image for: {name}",
        info_lines=fields,
        search_query=name,
        cache_key=name,
        dest_path=dest,
    )

def fetch_gc_image(name, gc_id, force):
    """Download image from Great Courses CDN. Returns 'downloaded', 'skipped', or 'failed'."""
    dest = get_dest_path("gc", gc_id)
    if os.path.exists(dest) and not force:
        return "skipped"
    url = GC_IMAGE_URL.format(cid=gc_id)
    try:
        download(url, dest)
        logger.info("  Downloaded (GC): %s -> %s", name, dest)
        return "downloaded"
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        logger.error("  Failed (GC) %s: %s", name, e)
        return "failed"


def fetch_audible_image(name, asin, force):
    """Download image from Audible. Returns 'downloaded', 'skipped', or 'failed'."""
    dest = get_dest_path("audible", asin)
    if os.path.exists(dest) and not force:
        return "skipped"
    image_url = fetch_audible_image_url(asin)
    if not image_url:
        logger.info("  No image found on Audible for: %s", name)
        return "failed"
    try:
        download(image_url, dest)
        logger.info("  Downloaded (Audible): %s -> %s", name, dest)
        return "downloaded"
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        logger.error("  Failed (Audible) %s: %s", name, e)
        return "failed"


def process_entry(name, fields, force):
    """Process one entry. Returns 'downloaded', 'skipped', 'failed', or 'quit'."""
    gc_id = fields.get("great_courses_id")
    asin = fields.get("audible_asin")
    if gc_id:
        result = fetch_gc_image(name, gc_id, force)
        time.sleep(0.2)
        return result
    if asin:
        result = fetch_audible_image(name, asin, force)
        time.sleep(0.3)
        return result
    return handle_image_search(name, fields, force)


def main():
    parser = argparse.ArgumentParser(description="Fetch audio course cover images")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    args = parser.parse_args()

    # Bare message format: this is an interactive tool whose output is read by a
    # person, not a log file, so the level/timestamp prefixes would only add noise.
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    os.makedirs(IMAGE_DIR, exist_ok=True)
    entries = load_entries()
    downloaded = 0
    skipped = 0
    failed = 0

    logger.info("Found %d courses\n", len(entries))

    for name, fields in entries:
        status = process_entry(name, fields, args.force)
        if status == "downloaded":
            downloaded += 1
        elif status == "quit":
            logger.info("Quitting.")
            break
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    logger.info("\nDone: %d downloaded, %d skipped, %d failed", downloaded, skipped, failed)


if __name__ == "__main__":
    main()
