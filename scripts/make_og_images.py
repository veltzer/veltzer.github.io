#!/usr/bin/env python

"""
Draw the share cards: the 1200x630 image Slack, WhatsApp, X, LinkedIn and
the rest show beside a shared link (og:image), one per language.

Targets:
  static/images/og/card-en.jpg
  static/images/og/card-he.jpg
  static/images/og/card-ru.jpg

Each card is the site's logo (make_logo.py), the name and the line under it, taken
from home_title in i18n/<lang>.toml so the card says what the home page
says, and the author's portrait in a circle on the far side from the text,
as on the per-post cards (doc/SHARE_CARDS.md has the decisions behind them). English is set in Outfit, the site's heading font from the
shared-themes submodule; Hebrew and Russian in Liberation Sans, which has the
Hebrew and Cyrillic letters Outfit lacks and the comma Noto Sans Hebrew lacks
(Pillow does no font fallback). Hebrew is laid out right to left (Pillow
needs libraqm).

Run it by hand after changing home_title, the colours or the portrait; the JPEGs are
committed, so building the site needs neither Pillow nor the fonts for them.
The per-post cards (make_post_cards.py) are build output and do import this
module's drawing code, so they need Pillow, libraqm and the fonts.
"""

import sys
import tomllib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, features

from make_logo import mark

REPO_ROOT = Path(__file__).resolve().parent.parent
I18N = REPO_ROOT / "i18n"
OUT_DIR = REPO_ROOT / "static" / "images" / "og"
OUTFIT = REPO_ROOT / "shared" / "shared-themes" / "fonts" / "Outfit-Bold.ttf"
OUTFIT_LIGHT = REPO_ROOT / "shared" / "shared-themes" / "fonts" / "Outfit-Light.ttf"
LIBERATION = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
LIBERATION_LIGHT = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
# The drawing on the About page, on every card.
PORTRAIT = REPO_ROOT / "static" / "images" / "mark-veltzer.jpg"

# The languages of the site, and the ones written right to left.
LANGUAGES = ("en", "he", "ru")
RTL = ("he",)

WIDTH, HEIGHT = 1200, 630
# The default light theme's accent (shared-themes/themes.yaml), which is
# also the logo's tile.
BACKGROUND = (255, 255, 255)
ACCENT = (64, 81, 181)
TEXT = (33, 33, 33)
MUTED = (96, 96, 96)

MARGIN = 90
# The portrait: a circle on the far side from the text, the text column
# ending PORTRAIT_GAP short of it.
PORTRAIT_SIZE = 300
PORTRAIT_TOP = 165
PORTRAIT_GAP = 50
COLUMN = WIDTH - 2 * MARGIN - PORTRAIT_SIZE - PORTRAIT_GAP
# The circle is drawn this many times larger and scaled down, for a smooth edge.
SUPERSAMPLE = 4


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def home_title(lang):
    with (I18N / f"{lang}.toml").open("rb") as stream:
        return tomllib.load(stream)["home_title"]


def fonts(lang):
    """The bold and light faces a language's text is set in."""
    if lang == "en":
        return OUTFIT, OUTFIT_LIGHT
    return LIBERATION, LIBERATION_LIGHT


def draw_mark(image, left, top, size):
    """The logo, size x size, with its top left corner at (left, top)."""
    logo = mark(size)
    image.paste(logo, (left, top), logo)


def portrait():
    """The portrait cropped to a circle with a thin accent ring, as RGBA."""
    if not PORTRAIT.is_file():
        die(f"{PORTRAIT} missing")
    size = PORTRAIT_SIZE
    big = size * SUPERSAMPLE
    face = ImageOps.fit(Image.open(PORTRAIT).convert("RGB"), (big, big), Image.Resampling.LANCZOS)
    ring = 3 * SUPERSAMPLE
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, big - 1, big - 1), fill=ACCENT)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((ring, ring, big - 1 - ring, big - 1 - ring), fill=255)
    out.paste(face, (0, 0), mask)
    return out.resize((size, size), Image.Resampling.LANCZOS)


def draw_portrait(image, face, rtl):
    """The portrait on the far side from the text: right, or left for RTL."""
    left = MARGIN if rtl else WIDTH - MARGIN - PORTRAIT_SIZE
    image.paste(face, (left, PORTRAIT_TOP), face)


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


def card(lang, face):
    rtl = lang in RTL
    name, _, line = home_title(lang).partition(" \u2013 ")
    bold_path, light_path = fonts(lang)
    direction = "rtl" if rtl else "ltr"
    light = ImageFont.truetype(str(light_path), 48)
    small = ImageFont.truetype(str(OUTFIT_LIGHT), 34)

    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, HEIGHT - 18, WIDTH, HEIGHT), fill=ACCENT)
    draw_portrait(image, face, rtl)

    # Logo, name and line stacked at the start of the reading direction,
    # in the column beside the portrait. The name takes the largest size
    # that fits the column on one line.
    edge = WIDTH - MARGIN if rtl else MARGIN
    anchor = "ra" if rtl else "la"
    logo = 110
    draw_mark(image, edge - logo if rtl else edge, 110, logo)
    size = 96
    bold = ImageFont.truetype(str(bold_path), size)
    while draw.textlength(name, font=bold, direction=direction) > COLUMN:
        size -= 4
        bold = ImageFont.truetype(str(bold_path), size)
    draw.text((edge, 260), name, font=bold, fill=TEXT, anchor=anchor, direction=direction)
    y = 380
    for text in wrap(draw, line, light, COLUMN, direction):
        draw.text((edge, y), text, font=light, fill=MUTED, anchor=anchor, direction=direction)
        y += 60
    draw.text((WIDTH - edge if rtl else WIDTH - MARGIN, 548), "veltzer.org", font=small,
              fill=ACCENT, anchor="la" if rtl else "ra")
    return image


def main():
    if not features.check("raqm"):
        die("Pillow was built without libraqm; Hebrew would be laid out left to right")
    for font in (OUTFIT, OUTFIT_LIGHT, LIBERATION, LIBERATION_LIGHT):
        if not font.is_file():
            die(f"{font} missing")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    face = portrait()
    for lang in LANGUAGES:
        target = OUT_DIR / f"card-{lang}.jpg"
        card(lang, face).save(target, quality=88, optimize=True, progressive=True)
        print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
