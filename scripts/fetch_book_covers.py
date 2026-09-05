#!/usr/bin/env python

"""
Fetch cover images for the books in ../data/yaml/books_read.yaml.

Each book carries a goodreads id or a simania id on one of its names (the
data repo's check_books insists on one). Both sites publish the cover as the
page's `og:image`, so no API key is needed: the book page is fetched, the
meta tag read, and the image downloaded and shrunk to the site standard.

Images saved as static/images/book-{cover}.jpg, where {cover} is the key
scripts/import_books.py puts on the item: `goodreads-<id>` or `simania-<id>`
(simania preferred when both exist -- that is the hebrew edition read).

goodreads answers /book/show/<id> for non-browser clients with an empty 202
(an AWS WAF challenge); the /en/ prefixed url serves the same page.

Incremental: skips books that already have an image.

Usage:
  scripts/fetch_book_covers.py [--force] [--delay SECONDS]
"""

import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml
from image_standard import normalise
from import_books import convert_item

# Resolved from this file rather than the cwd, so the script works from anywhere
# instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = REPO_ROOT / "static" / "images"
YAML_PATH = REPO_ROOT.parent / "data" / "yaml" / "books_read.yaml"
PAGE_URLS = {
    "goodreads": "https://www.goodreads.com/en/book/show/{book_id}",
    "simania": "https://simania.co.il/bookdetails.php?item_id={book_id}",
}
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) fetch_book_covers"
# A regex rather than BeautifulSoup: a goodreads book page is ~800 KB and
# html.parser took several seconds on each, which dominated the run.
OG_IMAGE_RE = re.compile(rb'<meta\s+property="og:image"\s+content="([^"]+)"')


def fetch(url, timeout=30):
    """GET a url as bytes, with a browser-like user agent."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cover_url(cover):
    """The og:image url of the book page behind a cover key, or None."""
    source, _, book_id = cover.partition("-")
    page = fetch(PAGE_URLS[source].format(book_id=book_id))
    match = OG_IMAGE_RE.search(page)
    return match.group(1).decode("utf-8") if match else None


def download(url, dest):
    """Download an image, shrunk to the site standard (see image_standard.py)."""
    data = fetch(url)
    with open(dest, "wb") as handle:
        handle.write(data)
    normalise(dest)


def load_books():
    """(name, cover) for every book that has a cover key."""
    with open(YAML_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    books = []
    for item in data.get("items") or []:
        flat = convert_item(item)
        if flat.get("cover"):
            books.append((flat["name"], flat["cover"]))
    return books


def main():
    parser = argparse.ArgumentParser(description="Fetch book cover images from goodreads and simania")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds to sleep between requests")
    args = parser.parse_args()

    os.makedirs(IMAGE_DIR, exist_ok=True)
    books = load_books()
    print(f"Found {len(books)} books with a cover key\n")

    downloaded = skipped = failed = 0
    for name, cover in books:
        dest = IMAGE_DIR / f"book-{cover}.jpg"
        if dest.exists() and not args.force:
            skipped += 1
            continue
        try:
            url = cover_url(cover)
            if not url:
                print(f"  No cover on the page for {name} ({cover})")
                failed += 1
                continue
            download(url, dest)
            downloaded += 1
            print(f"  Downloaded: {name} -> {dest}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            print(f"  Failed {name} ({cover}): {e}", file=sys.stderr)
            failed += 1
        time.sleep(args.delay)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
