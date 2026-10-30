#!/usr/bin/env python

"""Copy every blog post to ~/insync/for_ai, for AI agents that read Google Drive.

Insync syncs ~/insync to Google Drive, so the posts become readable there by
any agent with access to the Drive. Only the posts are copied: the English and
Hebrew sources from content/blog/, as they are, front matter included (the
title, date and tags are useful context for a reader that is not a browser).
The section's own _index files are not posts and are left out.

The destination is a mirror of the posts and nothing else: a post whose
source changed is copied again, an unchanged one is left alone (so Insync
uploads only what changed), and a .md file there with no post behind it,
a post since renamed or deleted, is removed. Files of any other kind are
never touched.

Not part of the build. Run it from the repo root after adding posts.
"""

import argparse
import sys
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent / "content" / "blog"
DEFAULT_DEST = Path.home() / "insync" / "for_ai"


def posts():
    return sorted(
        path
        for path in BLOG.glob("*.md")
        if not path.name.startswith("_")
    )


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
        target.write_bytes(data)
        copied += 1

    removed = 0
    for stale in sorted(dest.glob("*.md")):
        if stale.name not in names:
            stale.unlink()
            removed += 1

    print(f"{len(sources)} posts in {dest}: {copied} copied, {removed} removed")


if __name__ == "__main__":
    main()
