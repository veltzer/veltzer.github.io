#!/usr/bin/env python3
"""
Fetch movie poster images from TMDB (with OMDB fallback) by IMDB ID.

Downloads to blog/images/movie-{imdb_id}.jpg. Skips existing unless --force.

Requires pass entries: keys/themoviedb.org.read, keys/omdbapi.com.key
"""

import argparse
from poster_utils import fetch_posters

YAML_PATH = "blog/data/video_features.yaml.gz"
IMAGE_DIR = "blog/images"

parser = argparse.ArgumentParser(description="Fetch movie posters from TMDB/OMDB")
parser.add_argument("--force", action="store_true", help="Re-download existing images")
args = parser.parse_args()

fetch_posters(YAML_PATH, IMAGE_DIR, "movie", "movie_results", force=args.force)
