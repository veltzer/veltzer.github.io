#!/usr/bin/env python

"""Copy every blog post to ~/insync/for_ai/blog, for AI agents that read Google Drive.

Insync syncs ~/insync to Google Drive, so the posts become readable there by
any agent with access to the Drive. Only the posts are copied: the English and
Hebrew sources from content/blog/, as they are, front matter included (the
title, date and tags are useful context for a reader that is not a browser).
The section's own _index files are not posts and are left out.

The destination is a mirror of the posts and nothing else: a post whose
source changed is copied again, an unchanged one is left alone (so Insync
uploads only what changed), and a .md file there with no post behind it,
a post since renamed or deleted, is removed. Files of any other kind are
never touched. So the script is idempotent: a second run right after the
first writes and removes nothing, and an interrupted run is finished by the
next one.

Not part of the build. Run it from the repo root after adding posts.
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent / "content" / "blog"
DEFAULT_DEST = Path.home() / "insync" / "for_ai" / "blog"


def posts():
    return sorted(
        path
        for path in BLOG.glob("*.md")
        if not path.name.startswith("_")
    )


def write_atomically(source, target, data):
    """Write through a temporary file and a rename, so an interrupted run
    never leaves a half-written post for Insync to upload. The copy takes
    the source's permissions rather than mkstemp's owner-only ones."""
    fd, temp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
        shutil.copymode(source, temp)
        os.replace(temp, target)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--dest", type=Path, default=DEFAULT_DEST,
        help=f"directory to mirror the posts into (default: {DEFAULT_DEST})",
    )
    args = parser.parse_args()
    dest = args.dest.expanduser()
    if not dest.is_dir():
        sys.exit(f"{dest} does not exist; create it first")

    sources = posts()
    names = {path.name for path in sources}
    copied = 0
    for source in sources:
        data = source.read_bytes()
        target = dest / source.name
        if target.is_file() and target.read_bytes() == data:
            continue
        write_atomically(source, target, data)
        copied += 1

    removed = 0
    for stale in sorted(dest.glob("*.md")):
        if stale.name not in names and stale.is_file():
            stale.unlink()
            removed += 1

    print(f"{len(sources)} posts in {dest}: {copied} copied, {removed} removed")


if __name__ == "__main__":
    main()
