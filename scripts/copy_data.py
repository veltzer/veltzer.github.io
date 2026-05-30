#!/usr/bin/env python

"""
Copy media/chess/youtube data from the sibling ../data repo into blog/data.

YAML data for the media tracker lives in a separate ../data repository and
is copied in during build. This script validates the sources exist, copies
the plain YAML files, runs the audible import (type fixes + field cleanup)
and the youtube CSV->YAML conversion, then gzips everything in blog/data.
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
DATA_REPO = REPO_ROOT.parent / "data"
DEST = REPO_ROOT / "blog" / "data"

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


def gzip_data_files():
    # gzip all data files. -n omits the name/mtime from the header so output is
    # reproducible across rebuilds; -f overwrites any existing .gz. Shelling out
    # to gzip keeps the output byte-identical to the original build (same OS-field
    # header byte), which matters for idempotent commits of build artifacts.
    targets = sorted(DEST.glob("*.yaml")) + sorted(DEST.glob("*.pgn"))
    subprocess.run(["gzip", "-nf", *map(str, targets)], check=True)


def main():
    validate_sources()
    copy_plain_yaml()
    import_audible()
    copy_chess()
    convert_youtube()
    gzip_data_files()


if __name__ == "__main__":
    main()
