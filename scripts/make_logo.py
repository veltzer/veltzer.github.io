#!/usr/bin/env python

"""
The site's logo, and the icon files drawn from it.

The mark is a shell prompt: the "V" of Veltzer turned on its side into a
">" with a cursor after it, in white on a rounded accent-coloured tile.
Its geometry is defined once, here, on a 64x64 grid, and every rendering
comes from that:

  static/favicon.svg           the browser-tab icon (vector; a lighter
                               tile when the reader's system is dark)
  static/favicon.ico           16, 32 and 48 px, for browsers and tools
                               that ask for /favicon.ico or ignore SVG
  static/apple-touch-icon.png  180 px, full-bleed (iOS rounds the corners
                               itself and ignores SVG icons)

The site header draws the same paths inline in templates/base.html, so its
colours follow the theme; tests/test_logo.py fails if that copy drifts from
the geometry here. The share cards (make_og_images.py, make_post_cards.py)
paste mark() into their JPEGs.

Run by hand after changing the mark, then run make_og_images.py; the icon
files and the site-wide cards are committed, the post cards are build
output and redraw themselves.
"""

from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = REPO_ROOT / "static"

GRID = 64
RADIUS = 14
STROKE = 7
# The ">" and the cursor "_", as SVG path data on the 64x64 grid.
CHEVRON = ((15, 19), (31, 32), (15, 45))
CURSOR = ((35, 45), (50, 45))
PATH = "M15 19 L31 32 L15 45 M35 45 H50"

# The default light theme's accent and background (shared-themes), and the
# pair a dark system gets in the SVG favicon.
TILE = (64, 81, 181)
INK = (255, 255, 255)
DARK_TILE = (140, 158, 255)
DARK_INK = (27, 29, 38)

SUPERSAMPLE = 4


def hex_of(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def svg():
    """The favicon as SVG text."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}">
  <style>
    rect {{ fill: {hex_of(TILE)}; }}
    path {{ stroke: {hex_of(INK)}; }}
    @media (prefers-color-scheme: dark) {{
      rect {{ fill: {hex_of(DARK_TILE)}; }}
      path {{ stroke: {hex_of(DARK_INK)}; }}
    }}
  </style>
  <rect width="{GRID}" height="{GRID}" rx="{RADIUS}"/>
  <path d="{PATH}" fill="none" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def _stroke(draw, points, scale, fill):
    """A polyline with round joins and round caps, as SVG draws it."""
    scaled = [(x * scale, y * scale) for x, y in points]
    width = round(STROKE * scale)
    draw.line(scaled, fill=fill, width=width, joint="curve")
    r = STROKE * scale / 2
    for x, y in scaled:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def mark(size, rounded=True, tile=TILE, ink=INK):
    """The mark as a size x size RGBA image, antialiased by supersampling."""
    big = size * SUPERSAMPLE
    scale = big / GRID
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = round(RADIUS * scale) if rounded else 0
    draw.rounded_rectangle((0, 0, big - 1, big - 1), radius=radius, fill=tile)
    _stroke(draw, CHEVRON, scale, ink)
    _stroke(draw, CURSOR, scale, ink)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main():
    targets = {
        "favicon.svg": lambda path: path.write_text(svg(), encoding="utf-8"),
        "favicon.ico": lambda path: mark(256).save(path, sizes=[(16, 16), (32, 32), (48, 48)]),
        "apple-touch-icon.png": lambda path: mark(180, rounded=False).convert("RGB").save(
            path, optimize=True),
    }
    for name, write in targets.items():
        path = STATIC / name
        write(path)
        print(f"wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
