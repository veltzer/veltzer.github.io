"""
Shared utilities for fetching poster images from TMDB with OMDB fallback.
"""

import gzip
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

TMDB_FIND_URL = "https://api.themoviedb.org/3/find/tt{imdb_id}?external_source=imdb_id"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w300{poster_path}"
OMDB_URL = "http://www.omdbapi.com/?i=tt{imdb_id}&apikey={api_key}"
TMDB_PASS_ENTRY = "keys/themoviedb.org.read"
OMDB_PASS_ENTRY = "keys/omdbapi.com.key"


def get_pass_entry(entry):
    try:
        return subprocess.check_output(
            ["pass", "show", entry], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"ERROR: Could not read from pass at '{entry}'", file=sys.stderr)
        sys.exit(1)


def load_imdb_ids(yaml_path):
    """Extract imdb_id values from a gzipped YAML file."""
    ids = []
    with gzip.open(yaml_path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("imdb_id:"):
                value = line.split(":", 1)[1].strip().strip("'\"")
                if value:
                    ids.append(value)
    return ids


def fetch_poster_tmdb(imdb_id, token, result_key="movie_results"):
    """Fetch poster path from TMDB. Returns image URL or None."""
    url = TMDB_FIND_URL.format(imdb_id=imdb_id)
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  TMDB API error for tt{imdb_id}: {e.code}", file=sys.stderr)
        return None

    results = data.get(result_key, [])
    if not results:
        # Try alternate key
        alt_key = "tv_results" if result_key == "movie_results" else "movie_results"
        results = data.get(alt_key, [])
    if results and results[0].get("poster_path"):
        return TMDB_IMAGE_URL.format(poster_path=results[0]["poster_path"])
    return None


def fetch_poster_omdb(imdb_id, api_key):
    """Fetch poster URL from OMDB as fallback. Returns image URL or None."""
    url = OMDB_URL.format(imdb_id=imdb_id, api_key=api_key)
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  OMDB API error for tt{imdb_id}: {e.code}", file=sys.stderr)
        return None

    poster = data.get("Poster")
    if poster and poster != "N/A":
        return poster
    return None


def download_image(url, dest):
    """Download an image from a URL."""
    urllib.request.urlretrieve(url, dest)


def fetch_posters(yaml_path, image_dir, prefix, tmdb_result_key, force=False):
    """
    Main fetch loop. Downloads posters for all IMDB IDs in the YAML file.

    Args:
        yaml_path: Path to gzipped YAML data file
        image_dir: Directory to save images
        prefix: Filename prefix (e.g. 'movie' or 'series')
        tmdb_result_key: TMDB result key ('movie_results' or 'tv_results')
        force: Re-download existing images
    """
    tmdb_token = get_pass_entry(TMDB_PASS_ENTRY)
    omdb_key = get_pass_entry(OMDB_PASS_ENTRY)
    os.makedirs(image_dir, exist_ok=True)

    imdb_ids = load_imdb_ids(yaml_path)
    print(f"Found {len(imdb_ids)} items with IMDB IDs")

    downloaded = 0
    skipped = 0
    failed = 0

    for imdb_id in imdb_ids:
        dest = os.path.join(image_dir, f"{prefix}-{imdb_id}.jpg")
        if os.path.exists(dest) and not force:
            skipped += 1
            continue

        # Try TMDB first
        image_url = fetch_poster_tmdb(imdb_id, tmdb_token, tmdb_result_key)

        # Fallback to OMDB
        if not image_url:
            image_url = fetch_poster_omdb(imdb_id, omdb_key)
            if image_url:
                print(f"  Found via OMDB fallback for tt{imdb_id}")

        if not image_url:
            print(f"  No poster found for tt{imdb_id}")
            failed += 1
            time.sleep(0.3)
            continue

        try:
            download_image(image_url, dest)
            downloaded += 1
            print(f"  Downloaded poster for tt{imdb_id}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            print(f"  Failed to download poster for tt{imdb_id}: {e}", file=sys.stderr)
            failed += 1

        time.sleep(0.3)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")
