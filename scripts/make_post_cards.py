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

The look matches the site-wide card: the logo and the author's
name at the top, the title large, the tags under it, veltzer.org and the
accent band at the bottom. The author's portrait (the drawing on the About
page) sits in a circle on the far side from the text, so every shared link
shows a picture. Hebrew is laid out right to left (Pillow needs
libraqm, which its wheels bundle).
"""

import sys
import tomllib
from pathlib import Path

from make_og_images import (
    ACCENT,
    BACKGROUND,
    HEIGHT,
    LANGUAGES,
    LIBERATION,
    LIBERATION_LIGHT,
    MUTED,
    OUTFIT,
    OUTFIT_LIGHT,
    RTL,
    TEXT,
    WIDTH,
    die,
    draw_mark,
    fonts,
    home_title,
)
from PIL import Image, ImageDraw, ImageFont, ImageOps, features

MARGIN = 90
# The title gets the largest size at which it fits in MAX_LINES lines.
TITLE_SIZES = (76, 68, 60, 54, 48, 44)
MAX_LINES = 4
TITLE_TOP = 190
TITLE_BOTTOM = 470
PORTRAIT = Path(__file__).resolve().parent.parent / "static" / "images" / "mark-veltzer.jpg"
PORTRAIT_SIZE = 300
PORTRAIT_TOP = 165
# Space between the title column and the portrait.
PORTRAIT_GAP = 50
# The circle is drawn this many times larger and scaled down, for a smooth edge.
SUPERSAMPLE = 4


def front_matter(path):
    """The TOML between the +++ lines."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("+++", 2)
    if len(parts) < 3:
        die(f"{path}: no +++ front matter")
    return tomllib.loads(parts[1])


def wrap(draw, text, font, width, direction):
    """Greedy word wrap of text into lines no wider than width."""
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if draw.textlength(candidate, font=font, direction=direction) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_title(draw, title, bold_path, width, direction):
    """The biggest font, and its lines, that fit the title box."""
    for size in TITLE_SIZES:
        font = ImageFont.truetype(str(bold_path), size)
        lines = wrap(draw, title, font, width, direction)
        line_height = round(size * 1.18)
        if len(lines) <= MAX_LINES and len(lines) * line_height <= TITLE_BOTTOM - TITLE_TOP:
            return font, lines, line_height
    # Longer than every size allows: the smallest size, cut at MAX_LINES.
    size = TITLE_SIZES[-1]
    font = ImageFont.truetype(str(bold_path), size)
    lines = wrap(draw, title, font, width, direction)
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
        lines[-1] = f"{lines[-1]}…"
    return font, lines, round(size * 1.18)


def portrait():
    """The portrait cropped to a circle with a thin accent ring, as RGBA."""
    size = PORTRAIT_SIZE
    big = size * SUPERSAMPLE
    face = ImageOps.fit(Image.open(PORTRAIT).convert("RGB"), (big, big), Image.Resampling.LANCZOS)
    ring = 3 * SUPERSAMPLE
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    disc = ImageDraw.Draw(out)
    disc.ellipse((0, 0, big - 1, big - 1), fill=ACCENT)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((ring, ring, big - 1 - ring, big - 1 - ring), fill=255)
    out.paste(face, (0, 0), mask)
    return out.resize((size, size), Image.Resampling.LANCZOS)


def card(lang, title, tags, face):
    rtl = lang in RTL
    direction = "rtl" if rtl else "ltr"
    bold_path, light_path = fonts(lang)
    name = home_title(lang).partition(" – ")[0]
    name_font = ImageFont.truetype(str(bold_path), 40)
    tag_font = ImageFont.truetype(str(light_path), 32)
    site_font = ImageFont.truetype(str(OUTFIT_LIGHT), 34)

    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, HEIGHT - 18, WIDTH, HEIGHT), fill=ACCENT)

    # The reading direction decides which edge everything hangs from.
    edge = WIDTH - MARGIN if rtl else MARGIN
    anchor = "ra" if rtl else "la"
    mark = 64
    if rtl:
        draw_mark(image, edge - mark, 70, mark)
        name_x = edge - mark - 24
    else:
        draw_mark(image, edge, 70, mark)
        name_x = edge + mark + 24
    draw.text((name_x, 80), name, font=name_font, fill=TEXT, anchor=anchor, direction=direction)

    # The portrait on the far side from the text; the title column ends
    # PORTRAIT_GAP short of it.
    left = MARGIN if rtl else WIDTH - MARGIN - PORTRAIT_SIZE
    image.paste(face, (left, PORTRAIT_TOP), face)
    column = WIDTH - 2 * MARGIN - PORTRAIT_SIZE - PORTRAIT_GAP

    font, lines, line_height = fit_title(draw, title, bold_path, column, direction)
    y = TITLE_TOP
    for line in lines:
        draw.text((edge, y), line, font=font, fill=TEXT, anchor=anchor, direction=direction)
        y += line_height

    if tags:
        draw.text((edge, 500), " · ".join(tags), font=tag_font, fill=MUTED, anchor=anchor,
                  direction=direction)
    draw.text((WIDTH - edge if rtl else WIDTH - MARGIN, 548), "veltzer.org", font=site_font,
              fill=ACCENT, anchor="la" if rtl else "ra")
    return image


def language_of(path):
    """post.en.md -> en: the suffix rssite reads the language from."""
    suffixes = Path(path).suffixes
    if len(suffixes) < 2 or suffixes[-2][1:] not in LANGUAGES:
        die(f"{path}: no language suffix ({', '.join(LANGUAGES)})")
    return suffixes[-2][1:]


def main():
    pairs = sys.argv[1:]
    if not pairs or len(pairs) % 2:
        die("usage: make_post_cards.py <post.md> <card.jpg> [...]")
    if not features.check("raqm"):
        die("Pillow was built without libraqm; Hebrew would be laid out left to right")
    for font in (OUTFIT, OUTFIT_LIGHT, LIBERATION, LIBERATION_LIGHT):
        if not font.is_file():
            die(f"{font} missing")
    if not PORTRAIT.is_file():
        die(f"{PORTRAIT} missing")
    face = portrait()
    for source, target in zip(pairs[0::2], pairs[1::2]):
        meta = front_matter(source)
        tags = meta.get("taxonomies", {}).get("tags", [])
        image = card(language_of(source), meta["title"], tags, face)
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        image.save(target, quality=85, optimize=True, progressive=True)


if __name__ == "__main__":
    main()
