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
next one, including the temporary file a killed run can leave behind.

Since it deletes .md files, it only works in a directory it owns: one that
holds its marker file (MARKER). A directory without the marker is adopted,
and the marker written, only when it is empty or holds nothing but files
named like current posts; anything else is refused, so a mistaken --dest
pointing at a folder of someone's notes deletes nothing.

It is part of the build, but only on a machine with the mirror: the
export_posts_for_ai stanza in rsconstruct.toml runs it whenever a post (or
this script) changes, with `enabled_if_dir_exists` naming the destination, so
on CI and on any machine without Insync the processor is skipped. The build
passes --dest from the stanza's args, plus --inputs (only there so the build
reruns it; the posts are read from content/blog/ either way) and
--output-files, a stamp the script writes after a successful mirror. Run by
hand from the repo root it works the same without those.
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent / "content" / "blog"
DEFAULT_DEST = Path.home() / "insync" / "for_ai" / "blog"
MARKER = ".export_posts_for_ai"
# write_atomically names its temporary files .<post>.<random>.tmp
TEMP_GLOB = ".*.md.*.tmp"


def posts():
    return sorted(
        path
        for path in BLOG.glob("*.md")
        if not path.name.startswith("_")
    )


def claim(dest, names):
    """Make sure dest is ours to mirror into, writing the marker when it is
    safe to adopt, and exit otherwise."""
    marker = dest / MARKER
    if marker.is_file():
        return
    foreign = sorted(
        entry.name for entry in dest.iterdir()
        if entry.name not in names and not entry.match(TEMP_GLOB)
    )
    if foreign:
        shown = ", ".join(foreign[:5]) + (", ..." if len(foreign) > 5 else "")
        sys.exit(
            f"{dest} is not a posts mirror (no {MARKER}, and it holds {shown}); "
            f"refusing to delete anything there. If it really is the mirror, "
            f"create {marker} and run again."
        )
    marker.write_text("This directory is a mirror written by scripts/export_posts_for_ai.py "
                      "in veltzer.github.io. Its .md files are deleted when their post goes.\n")


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
    parser.add_argument("--inputs", nargs="*", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--output-files", nargs="*", type=Path, default=[], help=argparse.SUPPRESS)
    args = parser.parse_args()
    dest = args.dest.expanduser()
    if not dest.is_dir():
        sys.exit(f"{dest} does not exist; create it first")

    sources = posts()
    names = {path.name for path in sources}
    claim(dest, names)
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
    for temp in dest.glob(TEMP_GLOB):
        if temp.is_file():
            temp.unlink()

    print(f"{len(sources)} posts in {dest}: {copied} copied, {removed} removed")
    for stamp in args.output_files:
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.write_text(f"{len(sources)} posts mirrored\n")


if __name__ == "__main__":
    main()
