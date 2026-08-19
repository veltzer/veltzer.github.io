#!/usr/bin/env python

"""
One place that decides how large an image in static/images/ may be.

Every fetcher saves through normalise() so nothing oversized can arrive again.
Before this existed the three save paths -- image_picker.download/pick_image,
fetch_audiocourse_images.download and poster_utils.download_image -- each wrote
whatever the source served, and a 3264x2448 phone photo (2.4 MB) sat in the
repo for a museum card that renders at 192 pixels tall.

The numbers come from the markup, not from taste
------------------------------------------------
media-app.js renders every card as `w-full h-48 object-cover` inside
`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3` (content/media/_index.md).

  h-48 is 12rem = 192 CSS pixels tall.
  Three columns in a ~1280px content area, minus gaps, is ~400 CSS pixels wide.

object-cover crops to fill, so the binding dimension depends on the shape:
landscape photos are limited by width, portrait posters by height. Doubling
both for 2x displays gives 800x384, which is MAX_EDGE below.

The `>` in the geometry means "only shrink" -- an image already smaller than
the box passes through untouched rather than being upscaled into blur. Most of
the collection is 300x450 posters and is unaffected.

-strip is not only about bytes. Museum images come from a phone via
image_picker's search, and phone JPEGs carry EXIF that can include GPS
coordinates. Publishing those with a picture of a museum you visited is a
privacy leak, not a weight problem.

Deliberately still JPEG. WebP was measured on this collection and saves ~28%,
which does not pay for the `<picture>` fallbacks or the misleading `.jpg`
filenames it would need -- five plugins build paths by string concatenation
with the extension hardcoded. See doc/IMPROVEMENTS.md, "Asset weight".
"""

import shutil
import subprocess

# Max width x height in device pixels: 2x the rendered card, see above.
MAX_EDGE = "800x384>"
# 85 is where the resized museum photos stop showing artefacts at card size.
QUALITY = "85"


def _magick():
    """The ImageMagick binary, preferring v7's `magick` over the v6 `convert`."""
    return shutil.which("magick") or shutil.which("convert")


def normalise(path):
    """Shrink `path` in place to the site standard. Returns True if it ran.

    Silently does nothing when ImageMagick is absent: a contributor without it
    still gets a working fetch, just a heavier image, and the one-off pass in
    `scripts/normalise_images.py` will catch it later. Failing the fetch here
    would be a worse trade -- the image is already downloaded by this point.
    """
    binary = _magick()
    if binary is None:
        return False
    subprocess.run(
        [binary, str(path), "-resize", MAX_EDGE, "-quality", QUALITY,
         "-strip", "-interlace", "Plane", str(path)],
        check=True,
        capture_output=True,
    )
    return True
