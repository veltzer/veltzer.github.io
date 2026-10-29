#!/usr/bin/env python

"""
Draw the share cards: the 1200x630 image Slack, WhatsApp, X, LinkedIn and
the rest show beside a shared link (og:image), one per language.

Targets:
  static/images/og/card-en.jpg
  static/images/og/card-he.jpg

Each card is the favicon's "V" mark, the name and the line under it, taken
from home_title in i18n/<lang>.toml so the card says what the home page
says. Latin text is set in Outfit, the site's heading font from the
shared-themes submodule; Hebrew in Liberation Sans, which has both the
Hebrew letters Outfit lacks and the comma Noto Sans Hebrew lacks (Pillow
does no font fallback), laid out right to left (Pillow needs libraqm).

Run it by hand after changing home_title or the colours; the JPEGs are
committed, so the build needs neither Pillow nor the fonts.
"""

import sys
import tomllib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

REPO_ROOT = Path(__file__).resolve().parent.parent
I18N = REPO_ROOT / "i18n"
OUT_DIR = REPO_ROOT / "static" / "images" / "og"
OUTFIT = REPO_ROOT / "shared" / "shared-themes" / "fonts" / "Outfit-Bold.ttf"
OUTFIT_LIGHT = REPO_ROOT / "shared" / "shared-themes" / "fonts" / "Outfit-Light.ttf"
HEBREW = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
HEBREW_LIGHT = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")

WIDTH, HEIGHT = 1200, 630
# The default light theme's accent (shared-themes/themes.yaml) and the
# favicon's indigo.
BACKGROUND = (255, 255, 255)
ACCENT = (64, 81, 181)
MARK = (79, 70, 229)
TEXT = (33, 33, 33)
MUTED = (96, 96, 96)


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def home_title(lang):
    with (I18N / f"{lang}.toml").open("rb") as stream:
        return tomllib.load(stream)["home_title"]


def draw_mark(draw, left, top, size):
    """The favicon: a "V" of one round-capped stroke, in a size x size box."""
    points = [(0.10, 0.10), (0.50, 0.90), (0.90, 0.10)]
    scaled = [(left + x * size, top + y * size) for x, y in points]
    width = round(0.18 * size)
    draw.line(scaled, fill=MARK, width=width, joint="curve")
    for x, y in (scaled[0], scaled[-1]):
        r = width / 2
        draw.ellipse((x - r, y - r, x + r, y + r), fill=MARK)


def card(lang):
    rtl = lang == "he"
    name, _, line = home_title(lang).partition(" – ")
    bold = ImageFont.truetype(str(HEBREW if rtl else OUTFIT), 96)
    light = ImageFont.truetype(str(HEBREW_LIGHT if rtl else OUTFIT_LIGHT), 48)
    small = ImageFont.truetype(str(OUTFIT_LIGHT), 34)
    direction = "rtl" if rtl else "ltr"

    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, HEIGHT - 18, WIDTH, HEIGHT), fill=ACCENT)

    margin, mark = 90, 170
    # The mark sits at the start of the reading direction, the text after it.
    if rtl:
        draw_mark(draw, WIDTH - margin - mark, 150, mark)
        anchor_x, anchor = WIDTH - margin - mark - 60, "ra"
    else:
        draw_mark(draw, margin, 150, mark)
        anchor_x, anchor = margin + mark + 60, "la"
    draw.text((anchor_x, 160), name, font=bold, fill=TEXT, anchor=anchor, direction=direction)
    draw.text((anchor_x, 290), line, font=light, fill=MUTED, anchor=anchor, direction=direction)
    draw.text((margin if not rtl else WIDTH - margin, 520), "veltzer.org", font=small,
              fill=ACCENT, anchor="la" if not rtl else "ra")
    return image


def main():
    if not features.check("raqm"):
        die("Pillow was built without libraqm; Hebrew would be laid out left to right")
    for font in (OUTFIT, OUTFIT_LIGHT, HEBREW, HEBREW_LIGHT):
        if not font.is_file():
            die(f"{font} missing")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "he"):
        target = OUT_DIR / f"card-{lang}.jpg"
        card(lang).save(target, quality=88, optimize=True, progressive=True)
        print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
