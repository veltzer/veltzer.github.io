#!/usr/bin/env python3
"""
Fetch TV series poster images from TMDB (with OMDB fallback) by IMDB ID.

Downloads to blog/images/series-{imdb_id}.jpg. Skips existing unless --force.

Requires pass entries: keys/themoviedb.org.read, keys/omdbapi.com.key
"""

import argparse
from poster_utils import fetch_posters

YAML_PATH = "blog/data/video_series.yaml.gz"
IMAGE_DIR = "blog/images"

parser = argparse.ArgumentParser(description="Fetch TV series posters from TMDB/OMDB")
parser.add_argument("--force", action="store_true", help="Re-download existing images")
args = parser.parse_args()

fetch_posters(YAML_PATH, IMAGE_DIR, "series", "tv_results", force=args.force)
