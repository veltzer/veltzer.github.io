#!/usr/bin/env python3
"""
Fetch movie poster images from TMDB (with OMDB fallback) by IMDB ID.

Downloads to static/images/movie-{imdb_id}.jpg. Skips existing unless --force.

Requires pass entries: keys/themoviedb.org.read, keys/omdbapi.com.key
"""

import argparse
from pathlib import Path

from poster_utils import fetch_posters

# Resolved from this file rather than the cwd, so the script works from anywhere
# instead of only from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = str(REPO_ROOT / "static" / "data" / "video_features.json.gz")
IMAGE_DIR = str(REPO_ROOT / "static" / "images")

parser = argparse.ArgumentParser(description="Fetch movie posters from TMDB/OMDB")
parser.add_argument("--force", action="store_true", help="Re-download existing images")
args = parser.parse_args()

fetch_posters(DATA_PATH, IMAGE_DIR, "movie", "movie_results", force=args.force)
