#!/usr/bin/env python

"""
Copy media/chess/youtube data from the sibling ../data repo into static/data.

YAML data for the media tracker lives in a separate ../data repository and
is copied in during build. This script validates the sources exist, copies
the plain YAML files, runs the audible import (type fixes + field cleanup)
and the youtube CSV->YAML conversion, converts every YAML file to JSON, then
gzips everything in static/data.

The frontend consumes the JSON, not the YAML: parsing 6.5MB of YAML with
js-yaml in the browser measured ~399ms against ~31ms for JSON.parse on the
same data (12.9x), all of it blocking the main thread. Gzipped JSON is also
marginally smaller than gzipped YAML. The .yaml files remain the build's
intermediate representation.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
DATA_REPO = REPO_ROOT.parent / "data"
DEST = REPO_ROOT / "static" / "data"

# Plain YAML files copied verbatim from ../data/yaml.
PLAIN_YAML = [
    "podcasts.yaml",
    "museums.yaml",
    "video_features.yaml",
    "audio_courses.yaml",
    "video_series.yaml",
]

# Files that need a source check but are processed rather than copied directly.
PROCESSED_YAML = ["audible.yaml"]

CHESS_PGN = DATA_REPO / "raw" / "topics" / "games" / "chess" / "games.pgn"
YOUTUBE_CSV = DATA_REPO / "raw" / "topics" / "video" / "youtube" / "all.list.csv"


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def validate_sources():
    yaml_dir = DATA_REPO / "yaml"
    if not yaml_dir.is_dir():
        die(f"{yaml_dir} directory not found. Clone the data repo first.")
    for name in PLAIN_YAML + PROCESSED_YAML:
        if not (yaml_dir / name).is_file():
            die(f"Missing source file {yaml_dir / name}")
    if not CHESS_PGN.is_file():
        die(f"Missing source file {CHESS_PGN}")
    if not YOUTUBE_CSV.is_file():
        die(f"Missing source file {YOUTUBE_CSV}")


def copy_plain_yaml():
    yaml_dir = DATA_REPO / "yaml"
    for name in PLAIN_YAML:
        shutil.copyfile(yaml_dir / name, DEST / name)


def import_audible():
    # Import audible with type fixes and field cleanup.
    subprocess.run(
        [str(SCRIPTS / "import_audible.py"), str(DATA_REPO / "yaml" / "audible.yaml"), str(DEST / "audible.yaml")],
        check=True,
    )


def copy_chess():
    shutil.copyfile(CHESS_PGN, DEST / "games.pgn")


def convert_youtube():
    # Convert youtube CSV to yaml.
    subprocess.run(
        [str(SCRIPTS / "csv_to_yaml.py"), str(YOUTUBE_CSV), str(DEST / "youtube.yaml")],
        check=True,
    )


def convert_yaml_to_json():
    # The frontend fetches the .json.gz files; YAML is only the intermediate
    # form. separators drops the whitespace json.dump would otherwise emit,
    # and sort_keys keeps output stable across runs so rebuilds stay idempotent.
    for src in sorted(DEST.glob("*.yaml")):
        with open(src, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        dest = src.with_suffix(".json")
        with open(dest, "w", encoding="utf-8") as handle:
            json.dump(data, handle, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
        src.unlink()


def gzip_data_files():
    # gzip all data files. -n omits the name/mtime from the header so output is
    # reproducible across rebuilds; -f overwrites any existing .gz. Shelling out
    # to gzip keeps the output byte-identical to the original build (same OS-field
    # header byte), which matters for idempotent commits of build artifacts.
    targets = sorted(DEST.glob("*.json")) + sorted(DEST.glob("*.pgn"))
    subprocess.run(["gzip", "-nf", *map(str, targets)], check=True)


def main():
    validate_sources()
    copy_plain_yaml()
    import_audible()
    copy_chess()
    convert_youtube()
    convert_yaml_to_json()
    gzip_data_files()


if __name__ == "__main__":
    main()
