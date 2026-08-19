#!/usr/bin/env python

"""
Bring every image in static/images/ down to the site standard.

The fetchers normalise on save (scripts/image_standard.py), so this exists for
two cases: files that predate that change, and files added by hand or by a
contributor without ImageMagick installed.

Idempotent. ImageMagick's `>` geometry only shrinks, so an image already inside
the box is rewritten byte-for-byte identically in dimensions -- but re-encoding
still costs a little quality, so images already within the box are skipped
outright rather than passed through.

Usage:
  scripts/normalise_images.py           report what would change
  scripts/normalise_images.py --apply   do it
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

from image_standard import MAX_EDGE, normalise

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = REPO_ROOT / "static" / "images"

# MAX_EDGE is an ImageMagick geometry ("800x384>"); parse the numbers out of it
# rather than repeating them here, so there is still one source of truth.
MAX_W, MAX_H = (int(n) for n in MAX_EDGE.rstrip(">").split("x"))


def oversized(path):
    """True if the image exceeds the standard in either dimension."""
    with Image.open(path) as image:
        width, height = image.size
    return width > MAX_W or height > MAX_H


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="rewrite the files; without it, only report")
    args = parser.parse_args()

    targets = sorted(p for p in IMAGE_DIR.glob("*.jpg") if oversized(p))
    if not targets:
        print(f"All images in {IMAGE_DIR} are within {MAX_EDGE}.")
        return 0

    before = sum(p.stat().st_size for p in targets)
    print(f"{len(targets)} of {len(list(IMAGE_DIR.glob('*.jpg')))} images "
          f"exceed {MAX_EDGE} ({before / 1024 / 1024:.1f} MB):")
    for path in targets:
        with Image.open(path) as image:
            width, height = image.size
        print(f"  {width:5d}x{height:<5d} {path.stat().st_size / 1024:7.0f} KB  {path.name}")

    if not args.apply:
        print("\nRe-run with --apply to rewrite them.")
        return 0

    for path in targets:
        if not normalise(path):
            print("ImageMagick not found; nothing changed.", file=sys.stderr)
            return 1
    after = sum(p.stat().st_size for p in targets)
    print(f"\n{before / 1024 / 1024:.1f} MB -> {after / 1024 / 1024:.1f} MB "
          f"(-{100 * (1 - after / before):.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
