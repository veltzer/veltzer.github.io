#!/usr/bin/env python

"""
Build static/data from the media YAML in data/yaml.

The YAML data for the media tracker lives in this repo under data/yaml. This
script validates the sources exist, copies the plain YAML files, runs the
books import (nested names, authors and readings flattened to one item per
book), converts every YAML file to JSON, then gzips everything in
static/data. (The YouTube watch history, built here from a CSV in ../data,
lives in My World now, myworld.stream.)

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
YAML_DIR = REPO_ROOT / "data" / "yaml"
DEST = REPO_ROOT / "static" / "data"

# Plain YAML files copied verbatim from data/yaml. Only published data goes
# here: concerts.yaml and museums.yaml are private for now (doc/DECISIONS.md
# lists every private data file).
PLAIN_YAML = [
    "video_features.yaml",
    "audio_courses.yaml",
    "video_series.yaml",
]

# Files that need a source check but are processed rather than copied directly.
PROCESSED_YAML = ["books_read.yaml"]


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def report(path, what):
    # One line per file shipped in static/data, printed here rather than by the
    # helper scripts so every output is reported the same way. It names the
    # final .gz, which gzip_data_files() writes once all reports are out.
    print(f"{path.relative_to(REPO_ROOT)}: {what}")


def validate_sources():
    for name in PLAIN_YAML + PROCESSED_YAML:
        if not (YAML_DIR / name).is_file():
            die(f"Missing source file {YAML_DIR / name}")


def copy_plain_yaml():
    for name in PLAIN_YAML:
        shutil.copyfile(YAML_DIR / name, DEST / name)


def import_books():
    # Flatten the nested books_read.yaml (names/authors per language, readings)
    # into the one-item-per-book shape the media page searches and filters on.
    subprocess.run(
        [str(SCRIPTS / "import_books.py"), str(YAML_DIR / "books_read.yaml"), str(DEST / "books.yaml")],
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
        report(dest.with_name(dest.name + ".gz"), f"{len(data['items'])} items")


def gzip_data_files():
    # gzip all data files. -n omits the name/mtime from the header so output is
    # reproducible across rebuilds; -f overwrites any existing .gz. Shelling out
    # to gzip keeps the output byte-identical to the original build (same OS-field
    # header byte), which matters for idempotent commits of build artifacts.
    targets = sorted(DEST.glob("*.json"))
    subprocess.run(["gzip", "-nf", *map(str, targets)], check=True)


def main():
    validate_sources()
    copy_plain_yaml()
    import_books()
    convert_yaml_to_json()
    gzip_data_files()


if __name__ == "__main__":
    main()
