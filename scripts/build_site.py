#!/usr/bin/env python

"""
Build the site using Zola.

Zola reads config.toml plus content/, templates/, sass/ and static/, and
writes to _site/ (kept as the output dir so the Pages workflow and the
.gitignore entries do not have to change).

The blog posts under content/blog/ are generated from blog/posts/ by
scripts/mkdocs_to_zola.py, which is run first so an edit to a MkDocs-format
post still reaches the built site. That indirection is temporary: once the
MkDocs tree is retired, posts will be authored directly in content/.

Zola is a single static binary with no runtime dependencies, so unlike the
MkDocs build there is nothing to pip install and no plugin versions to pin.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "_site"
CONVERTER = REPO_ROOT / "scripts" / "mkdocs_to_zola.py"
THEME_SRC = REPO_ROOT / "shared" / "shared-themes"
THEME_DEST = REPO_ROOT / "static" / "shared-themes"
# Files taken from the shared-themes submodule. themes.css carries the palette;
# theme-switcher.js is copied so a theme picker can be added without another
# build change.
THEME_FILES = ["themes.css", "theme-switcher.js"]


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def find_zola():
    """Locate the zola binary, preferring one on PATH."""
    found = shutil.which("zola")
    if found:
        return found
    die("zola not found on PATH. Install it from https://www.getzola.org/")
    return None


def sync_theme():
    """Copy the shared-themes files into static/ so Zola serves them.

    Kept as a copy rather than a symlink or a sass @import: dart-sass leaves a
    plain @import of a .css file as a runtime import, and Zola does not follow
    symlinks out of the project. Copying on every build means the submodule is
    the single source of truth -- editing static/shared-themes/ directly would
    be overwritten, which is the intent.
    """
    if not THEME_SRC.is_dir():
        die(f"{THEME_SRC} missing. Run: git submodule update --init --recursive")
    THEME_DEST.mkdir(parents=True, exist_ok=True)
    for name in THEME_FILES:
        source = THEME_SRC / name
        if not source.is_file():
            die(f"{source} missing from the shared-themes submodule")
        shutil.copy2(source, THEME_DEST / name)


def convert_posts():
    """Regenerate content/blog from the MkDocs-format posts."""
    subprocess.run([sys.executable, str(CONVERTER)], check=True, cwd=REPO_ROOT)


def build(zola):
    # Zola wipes and recreates the output directory itself.
    subprocess.run(
        [zola, "build", "--output-dir", str(OUTPUT_DIR), "--force"],
        check=True,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )


def main():
    zola = find_zola()
    try:
        sync_theme()
        convert_posts()
        build(zola)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
