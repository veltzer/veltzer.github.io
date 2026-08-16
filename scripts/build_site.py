#!/usr/bin/env python

"""
Build the site using Zola.

Zola reads config.toml plus content/, templates/, sass/ and static/, and
writes to _site/ (kept as the output dir so the Pages workflow and the
.gitignore entries do not have to change).

Posts are authored directly in content/blog/. The old blog/posts/ tree and
scripts/mkdocs_to_zola.py were the one-time migration path and have been
retired: the converter rebuilt content/blog from scratch on every run, which
silently destroyed anything added there by hand -- translations included.

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


# The counterapi token is a public, increment-scoped browser credential -- the
# same category as the Calendar browser key (see doc/DECISIONS.md). It still
# lives in pass rather than in git, and is injected into static/keys.js at build
# time so the repo never carries it.
COUNTER_PASS_PATH = "keys/counterapi"
COUNTER_WORKSPACE = "veltzer-org"
COUNTER_NAME = "veltzerorg"
KEYS_JS = REPO_ROOT / "static" / "keys.js"
KEYS_TEMPLATE = REPO_ROOT / "static" / "keys.js.template"


def pass_entry(path):
    """Read a secret out of pass(1). Returns None when unavailable."""
    try:
        result = subprocess.run(
            ["pass", path], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.splitlines()[0].strip() or None


def sync_keys():
    """Inject the counterapi token into static/keys.js.

    Without pass available (CI, a fresh clone) the token line is written empty,
    which makes media-app.js skip the counter and hide the line rather than
    error. The calendar lines already in keys.js are left untouched.
    """
    if not KEYS_TEMPLATE.is_file():
        die(f"{KEYS_TEMPLATE} missing")
    token = pass_entry(COUNTER_PASS_PATH) or ""
    # Always regenerate from the template: keys.js is gitignored, so a fresh
    # clone has no copy of it at all.
    lines = KEYS_TEMPLATE.read_text().splitlines()
    lines += [
        f"const COUNTER_WORKSPACE = '{COUNTER_WORKSPACE}';",
        f"const COUNTER_NAME = '{COUNTER_NAME}';",
        f"const COUNTER_TOKEN = '{token}';",
    ]
    KEYS_JS.write_text("\n".join(lines) + "\n")


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
        sync_keys()
        build(zola)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
