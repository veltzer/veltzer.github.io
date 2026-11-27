#!/usr/bin/env python

"""
Draw the share cards: the 1200x630 image Slack, WhatsApp, X, LinkedIn and
the rest show beside a shared link (og:image), one per language.

Targets:
  static/images/og/card-en.jpg
  static/images/og/card-he.jpg
  static/images/og/card-ru.jpg

Each card is the author's portrait in a circle, the name and the line under
it, taken from home_title in i18n/<lang>.toml so the card says what the home
page says, all centred inside the middle square of the card: a small preview
shows only that square, so it has to be a whole picture by itself. The site's
logo (make_logo.py) and veltzer.org stand in the corners outside it, as on
the per-post cards (doc/SHARE_CARDS.md has the decisions behind them). English is set in Outfit, the site's heading font from the
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
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont, ImageOps, features

from make_logo import mark

if TYPE_CHECKING:
    from PIL.ImageFont import FreeTypeFont

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

# The small form of a preview (a thumbnail beside the title) shows only the
# square cut from the middle of the card, so the portrait and all the text
# are centred inside that square, in a column SQUARE_PAD short of its sides.
# Only the logo and veltzer.org stand outside it, in the corners.
SQUARE = HEIGHT
SQUARE_LEFT = (WIDTH - SQUARE) // 2
SQUARE_PAD = 30
COLUMN = SQUARE - 2 * SQUARE_PAD
CENTRE = WIDTH // 2
# The bottom band, and the distance of the corner items from the edges.
BAND = 18
MARGIN = 48
LOGO = 72
# The portrait: a circle at the top of the middle square. The site-wide
# card has less to say than a post's, so its portrait is larger.
PORTRAIT_SIZE = 210
SITE_PORTRAIT_SIZE = 270
PORTRAIT_TOP = 34
# The circle is drawn this many times larger and scaled down, for a smooth edge.
SUPERSAMPLE = 4


def die(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def home_title(lang: str):
    with (I18N / f"{lang}.toml").open("rb") as stream:
        return tomllib.load(stream)["home_title"]


def fonts(lang: str) -> tuple[Path, Path]:
    """The bold and light faces a language's text is set in."""
    if lang == "en":
        return OUTFIT, OUTFIT_LIGHT
    return LIBERATION, LIBERATION_LIGHT


def draw_mark(image: Image.Image, left: int, top: int, size: int) -> None:
    """The logo, size x size, with its top left corner at (left, top)."""
    logo = mark(size)
    image.paste(logo, (left, top), logo)


def portrait(size: int = PORTRAIT_SIZE):
    """The portrait cropped to a circle with a thin accent ring, as RGBA."""
    if not PORTRAIT.is_file():
        die(f"{PORTRAIT} missing")
    big = size * SUPERSAMPLE
    face = ImageOps.fit(Image.open(PORTRAIT).convert("RGB"), (big, big), Image.Resampling.LANCZOS)
    ring = 3 * SUPERSAMPLE
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, big - 1, big - 1), fill=ACCENT)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((ring, ring, big - 1 - ring, big - 1 - ring), fill=255)
    out.paste(face, (0, 0), mask)
    return out.resize((size, size), Image.Resampling.LANCZOS)


def blank(face: Image.Image, *, rtl: bool):
    """What every card starts from: the band, the portrait and the corners.

    The logo stands in the top corner where reading starts and veltzer.org
    in the bottom corner where it ends, both outside the middle square.
    """
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, HEIGHT - BAND, WIDTH, HEIGHT), fill=ACCENT)
    image.paste(face, (CENTRE - face.width // 2, PORTRAIT_TOP), face)
    draw_mark(image, WIDTH - MARGIN - LOGO if rtl else MARGIN, MARGIN, LOGO)
    site = ImageFont.truetype(str(OUTFIT_LIGHT), 32)
    draw.text((MARGIN if rtl else WIDTH - MARGIN, HEIGHT - BAND - 28), "veltzer.org", font=site,
              fill=ACCENT, anchor="ls" if rtl else "rs")
    return image, draw


def centred(draw: ImageDraw.ImageDraw, top: int, text: str, font: FreeTypeFont, fill: tuple[int, int, int], direction: str | None) -> None:
    """One line of text, centred in the middle square, its top at top."""
    draw.text((CENTRE, top), text, font=font, fill=fill, anchor="ma", direction=direction)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: FreeTypeFont, width: int, direction: str | None):
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


def balanced(draw: ImageDraw.ImageDraw, text: str, font: FreeTypeFont, width: int, direction: str | None):
    """wrap(), then the same number of lines at the narrowest width that
    keeps it: lines of about one length, not full ones and a stray word."""
    lines = wrap(draw, text, font, width, direction)
    low, high = 0, width
    while high - low > 4:
        middle = (low + high) // 2
        if len(wrap(draw, text, font, middle, direction)) <= len(lines):
            high = middle
        else:
            low = middle
    narrow = wrap(draw, text, font, high, direction)
    # A word wider than the narrow width overflows it; keep the plain wrap then.
    if max(draw.textlength(line, font=font, direction=direction) for line in narrow) > width:
        return lines
    return narrow


def card(lang: str, face: Image.Image):
    rtl = lang in RTL
    name, _, line = home_title(lang).partition(" \u2013 ")
    bold_path, light_path = fonts(lang)
    direction = "rtl" if rtl else "ltr"
    light = ImageFont.truetype(str(light_path), 38)

    image, draw = blank(face, rtl=rtl)

    # The name under the portrait, at the largest size that fits the column
    # on one line, then the line under it, wrapped.
    size = 84
    bold = ImageFont.truetype(str(bold_path), size)
    while draw.textlength(name, font=bold, direction=direction) > COLUMN:
        size -= 4
        bold = ImageFont.truetype(str(bold_path), size)
    centred(draw, 328, name, bold, TEXT, direction)
    y = 444
    for text in balanced(draw, line, light, COLUMN, direction):
        centred(draw, y, text, light, MUTED, direction)
        y += 50
    return image


def main() -> None:
    if not features.check("raqm"):
        die("Pillow was built without libraqm; Hebrew would be laid out left to right")
    for font in (OUTFIT, OUTFIT_LIGHT, LIBERATION, LIBERATION_LIGHT):
        if not font.is_file():
            die(f"{font} missing")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    face = portrait(SITE_PORTRAIT_SIZE)
    for lang in LANGUAGES:
        target = OUT_DIR / f"card-{lang}.jpg"
        card(lang, face).save(target, quality=88, optimize=True, progressive=True)
        print(f"wrote {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
