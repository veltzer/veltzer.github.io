#!/usr/bin/env python

"""
Draw one share card per blog post: the 1200x630 image a shared link to that
post shows (og:image), carrying the post's own title and tags rather than
the site-wide card that scripts/make_og_images.py draws.

Run by rsconstruct (processor.generator.generic.post_cards) in batch mode:

  make_post_cards.py <post.md> <card.jpg> [<post.md> <card.jpg> ...]

Unlike the site-wide cards these are build output, never committed:
there is one per post and language, and a card drawn by hand goes stale the moment a
title changes. Each card is a product of its post, so editing a post
redraws its card and nothing else.

The look matches the site-wide card: the author's portrait (the drawing on
the About page) in a circle, the author's name under it, then the title
large and the tags, all centred inside the middle square of the card, which
is the whole of what a small preview shows. The logo and veltzer.org stand
in the corners, the accent band along the bottom. Hebrew is laid out right to left (Pillow needs libraqm,
which its wheels bundle). doc/SHARE_CARDS.md has the decisions behind the
cards.
"""

import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import ImageFont, features

from make_og_images import (
    ACCENT,
    COLUMN,
    LANGUAGES,
    LIBERATION,
    LIBERATION_LIGHT,
    MUTED,
    OUTFIT,
    OUTFIT_LIGHT,
    RTL,
    TEXT,
    balanced,
    blank,
    centred,
    die,
    fonts,
    home_title,
    portrait,
    wrap,
)

if TYPE_CHECKING:
    from PIL.Image import Image
    from PIL.ImageDraw import ImageDraw
    from PIL.ImageFont import FreeTypeFont

# The author's name stands under the portrait, the title in the box under
# that, at the largest size at which it fits the box in MAX_LINES lines, and
# the tags under the box.
NAME_TOP = 256
TITLE_SIZES = (72, 64, 56, 50, 44, 40, 36, 32)
MAX_LINES = 5
TITLE_TOP = 306
TITLE_BOTTOM = 524
TAGS_TOP = 540


def front_matter(path: Path | str):
    """The TOML between the +++ lines."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("+++", 2)
    if len(parts) < 3:
        die(f"{path}: no +++ front matter")
    return tomllib.loads(parts[1])


def fit_title(draw: ImageDraw, title: str, bold_path: Path, width: int, direction: str):
    """The biggest font, and its lines, that fit the title box."""
    for size in TITLE_SIZES:
        font = ImageFont.truetype(str(bold_path), size)
        lines = wrap(draw, title, font, width, direction)
        line_height = round(size * 1.18)
        if len(lines) <= MAX_LINES and len(lines) * line_height <= TITLE_BOTTOM - TITLE_TOP:
            return font, balanced(draw, title, font, width, direction), line_height
    # Longer than every size allows: the smallest size, cut at MAX_LINES.
    size = TITLE_SIZES[-1]
    font = ImageFont.truetype(str(bold_path), size)
    lines = wrap(draw, title, font, width, direction)
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
        lines[-1] = f"{lines[-1]}…"
    return font, lines, round(size * 1.18)


def fit_tags(draw: ImageDraw, tags: list[str], font: FreeTypeFont, width: int, direction: str):
    """The tags joined by a dot, as many of the first ones as fit the width."""
    kept = list(tags)
    while len(kept) > 1 and draw.textlength(" · ".join(kept), font=font, direction=direction) > width:
        kept.pop()
    return " · ".join(kept)


def card(lang: str, title: str, tags: list[str], face: Image) -> Image:
    rtl = lang in RTL
    direction = "rtl" if rtl else "ltr"
    bold_path, light_path = fonts(lang)
    name = home_title(lang).partition(" \u2013 ")[0]
    name_font = ImageFont.truetype(str(bold_path), 32)
    tag_font = ImageFont.truetype(str(light_path), 28)

    image, draw = blank(face, rtl=rtl)
    centred(draw, NAME_TOP, name, name_font, ACCENT, direction)

    # The title, its lines centred in the box between the name and the tags.
    font, lines, line_height = fit_title(draw, title, bold_path, COLUMN, direction)
    y = TITLE_TOP + (TITLE_BOTTOM - TITLE_TOP - len(lines) * line_height) // 2
    for line in lines:
        centred(draw, y, line, font, TEXT, direction)
        y += line_height

    if tags:
        centred(draw, TAGS_TOP, fit_tags(draw, tags, tag_font, COLUMN, direction), tag_font, MUTED, direction)
    return image


def language_of(path: Path | str) -> str:
    """post.en.md -> en: the suffix rssite reads the language from."""
    suffixes = Path(path).suffixes
    if len(suffixes) < 2 or suffixes[-2][1:] not in LANGUAGES:
        die(f"{path}: no language suffix ({', '.join(LANGUAGES)})")
    return suffixes[-2][1:]


def main() -> None:
    pairs = sys.argv[1:]
    if not pairs or len(pairs) % 2:
        die("usage: make_post_cards.py <post.md> <card.jpg> [...]")
    if not features.check("raqm"):
        die("Pillow was built without libraqm; Hebrew would be laid out left to right")
    for font in (OUTFIT, OUTFIT_LIGHT, LIBERATION, LIBERATION_LIGHT):
        if not font.is_file():
            die(f"{font} missing")
    face = portrait()
    for source, target in zip(pairs[0::2], pairs[1::2], strict=False):
        meta = front_matter(source)
        tags = meta.get("taxonomies", {}).get("tags", [])
        image = card(language_of(source), meta["title"], tags, face)
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        image.save(target, quality=85, optimize=True, progressive=True)


if __name__ == "__main__":
    main()
