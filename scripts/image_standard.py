#!/usr/bin/env python

"""
One place that decides how large an image in static/images/ may be.

Every fetcher saves through normalise() so nothing oversized can arrive again.
Network fetchers go through download_image(), which also verifies the bytes
are an image before they reach their final name. Before this existed each save
path wrote whatever the source served, and a 3264x2448 phone photo (2.4 MB)
sat in the repo for a museum card that renders at 192 pixels tall.

The numbers come from the markup, not from taste
------------------------------------------------
The data collection app (removed 2026-11-23) rendered every card as
`w-full h-48 object-cover` inside `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3`.

  h-48 is 12rem = 192 CSS pixels tall.
  Three columns in a ~1280px content area, minus gaps, is ~400 CSS pixels wide.

object-cover crops to fill, so the binding dimension depends on the shape:
landscape photos are limited by width, portrait posters by height. Doubling
both for 2x displays gives 800x384, which is MAX_EDGE below.

The `>` in the geometry means "only shrink" -- an image already smaller than
the box passes through untouched rather than being upscaled into blur. The
TMDB posters (w300, 300x450) are taller than the 384 box, so they are shrunk
to 256x384; the height is the binding edge for portrait images.

-strip is not only about bytes. The museum images (in My World since 2026-11-23)
came from a phone, and phone JPEGs carry EXIF that can include GPS
coordinates. Publishing those with a picture of a museum you visited is a
privacy leak, not a weight problem.

Deliberately still JPEG. WebP was measured on this collection and saves ~28%,
which does not pay for the `<picture>` fallbacks or the misleading `.jpg`
filenames it would need -- five plugins build paths by string concatenation
with the extension hardcoded. See doc/IMPROVEMENTS.md, "Asset weight".
"""

import contextlib
import os
import shutil
import subprocess
import tempfile
import urllib.request
from typing import TYPE_CHECKING

from PIL import Image, UnidentifiedImageError

if TYPE_CHECKING:
    from pathlib import Path

# Max width x height in device pixels: 2x the rendered card, see above.
MAX_EDGE = "800x384>"
# 85 is where the resized museum photos stop showing artefacts at card size.
QUALITY = "85"


def _magick() -> str | None:
    """The ImageMagick binary, preferring v7's `magick` over the v6 `convert`."""
    return shutil.which("magick") or shutil.which("convert")


class ImageError(OSError):
    """An image could not be fetched, verified or normalised.

    Subclasses OSError so callers that already catch network errors keep
    working; callers report it per item and carry on with the run.
    """


def normalise(path: Path | str) -> bool:
    """Shrink `path` in place to the site standard. Returns True if it ran.

    Silently does nothing when ImageMagick is absent: a contributor without it
    still gets a working fetch, just a heavier image, and the one-off pass in
    `scripts/normalise_images.py` will catch it later. Failing the fetch here
    would be a worse trade -- the image is already downloaded by this point.

    Raises ImageError, carrying ImageMagick's stderr, when the conversion fails.
    """
    binary = _magick()
    if binary is None:
        return False
    # -auto-orient before -strip: strip drops the EXIF Orientation tag, so a
    # phone photo that relied on it would otherwise come out sideways for good.
    result = subprocess.run(
        [binary, str(path), "-auto-orient", "-resize", MAX_EDGE,
         "-quality", QUALITY, "-strip", "-interlace", "Plane", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ImageError(f"ImageMagick failed on {path}: {result.stderr.strip()}")
    return True


def download_image(url: str, dest: Path | str, timeout: int = 15, user_agent: str = "Mozilla/5.0") -> None:
    """Download `url` to `dest` as a verified, normalised image.

    The bytes go to a temporary name next to `dest`, are checked to open as an
    image with Pillow, normalised, and only then renamed over `dest`. A
    timeout, an HTML error page or a failed conversion therefore never leaves
    a file at `dest` for a later run to skip. On any failure the temporary
    file is removed and ImageError is raised (network errors included).
    """
    dest = os.fspath(dest)
    fd, tmp = tempfile.mkstemp(
        prefix=".download-", suffix=".jpg", dir=os.path.dirname(dest) or ".")
    try:
        with os.fdopen(fd, "wb") as handle:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                handle.write(resp.read())
        try:
            with Image.open(tmp) as image:
                image.verify()
        except (UnidentifiedImageError, OSError, SyntaxError) as exc:
            raise ImageError(f"{url} did not return an image: {exc}") from exc
        normalise(tmp)
        os.replace(tmp, dest)
    except ImageError:
        _remove(tmp)
        raise
    except Exception as exc:
        _remove(tmp)
        raise ImageError(f"{url}: {exc}") from exc
    except BaseException:
        _remove(tmp)  # Ctrl-C mid-download
        raise


def _remove(path: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.unlink(path)
