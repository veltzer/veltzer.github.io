#!/usr/bin/env python

"""Show the share card of a post: what a chat app shows for its link.

    scripts/show_card.py content/blog/2026-04-28-euthyphro-dilemma.he.md
    scripts/show_card.py euthyphro-dilemma
    scripts/show_card.py --lang he euthyphro-dilemma
    scripts/show_card.py https://veltzer.org/en/about/
    scripts/show_card.py --local euthyphro-dilemma

A post is named by its file, by its slug (English unless --lang says
otherwise) or by any URL of the site. The script reads the page the way
WhatsApp does (its user agent, the og: tags in the head), fetches the picture
og:image names, prints what it found and opens a mock-up of the two forms a
preview takes: the large one, the whole 1200x630 card above the title, and
the small one, a square cut from the middle of the card beside the title
(the cards are drawn so that this square holds the portrait and the whole
text, doc/SHARE_CARDS.md).

By default it asks the live site, which is what a link shared now will show.
--local reads the built _site/ instead (run `rsconstruct build` first), to
look at a card before it is pushed.

What it cannot show is a platform's cache. WhatsApp, Telegram and the rest
keep the preview of a link they have already fetched, some for days, so a
link shared before a card changed keeps its old card for a while; this
script always shows the card as it is now. See doc/SHARE_CARDS.md.

Network (unless --local), run by hand, not part of the build.
"""

import argparse
import io
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import override

from PIL import Image, ImageDraw, ImageFont, ImageOps

from make_og_images import LANGUAGES, OUTFIT_LIGHT, REPO_ROOT, RTL, die, fonts, wrap
from make_post_cards import front_matter, language_of

BLOG = REPO_ROOT / "content" / "blog"
SITE = REPO_ROOT / "_site"

# What WhatsApp's link fetcher sends; a server that treats crawlers
# differently answers this the way it answers WhatsApp.
USER_AGENT = "WhatsApp/2.23.20.0"
TIMEOUT = 30

# What the card is declared to be (templates/base.html), and the size above
# which WhatsApp is reported to drop a picture and show the text alone.
CARD_SIZE = (1200, 630)
MAX_BYTES = 600 * 1024

# The mock-up: a chat background with two message bubbles.
CHAT = (230, 221, 212)
BUBBLE = (217, 253, 211)
PANEL = (200, 238, 196)
INK = (17, 27, 33)
FADED = (84, 101, 111)
LARGE_WIDTH = 500
THUMB = 96
ENLARGED = 220
PAD = 10


class MetaTags(HTMLParser):
    """The <meta property=...> and <meta name=...> tags of a page, first one wins."""

    def __init__(self) -> None:
        super().__init__()
        self.tags = {}

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        found = dict(attrs)
        key = found.get("property") or found.get("name")
        content = found.get("content")
        if key and content is not None:
            self.tags.setdefault(key, content)


def meta_tags(html: str):
    parser = MetaTags()
    parser.feed(html)
    return parser.tags


def base_url():
    with (REPO_ROOT / "rssite.toml").open("rb") as stream:
        return tomllib.load(stream)["base_url"].rstrip("/")


def page_url(post: str, lang: str):
    """The URL of what the user named: a URL, a post file or a slug."""
    if post.startswith(("http://", "https://")):
        return post
    path = Path(post)
    if path.is_file():
        return f"{base_url()}/{language_of(path)}/blog/{front_matter(path)['slug']}/"
    # <date>-<slug>.<lang>.md: the date is ten characters.
    matches = [found for found in BLOG.glob(f"*-{post}.{lang}.md") if found.name[11:] == f"{post}.{lang}.md"]
    if not matches:
        die(f"{post}: not a URL, not a file, and no post in {BLOG.relative_to(REPO_ROOT)} has that slug")
    return f"{base_url()}/{lang}/blog/{post}/"


def local_path(url: str):
    """The file under _site/ that the live site serves at url."""
    if not url.startswith(base_url() + "/"):
        die(f"{url}: not under {base_url()}, so _site/ does not have it")
    path = SITE / urllib.parse.urlparse(url).path.lstrip("/")
    return path / "index.html" if url.split("?", maxsplit=1)[0].endswith("/") else path


def read(url: str, *, local: bool):
    """The bytes at url and their content type (None when read from _site/)."""
    if local:
        path = local_path(url)
        if not path.is_file():
            die(f"{path.relative_to(REPO_ROOT)} missing: run `rsconstruct build` first")
        return path.read_bytes(), None
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.read(), response.headers.get_content_type()
    except urllib.error.HTTPError as error:
        die(f"{url}: HTTP {error.code}")
    except urllib.error.URLError as error:
        die(f"{url}: {error.reason}")
    raise AssertionError("unreachable")


def problems(tags: dict[str, str], data: bytes, content_type: str | None, picture: Image.Image) -> list[str]:
    """Everything about the card a platform would trip over."""
    found = []
    if not tags["og:image"].startswith("https://"):
        found.append(f"og:image is not an absolute https URL: {tags['og:image']}")
    if content_type is not None and not content_type.startswith("image/"):
        found.append(f"the picture is served as {content_type}")
    if picture.size != CARD_SIZE:
        found.append(f"the picture is {picture.width}x{picture.height}, not {CARD_SIZE[0]}x{CARD_SIZE[1]}")
    declared = (tags.get("og:image:width"), tags.get("og:image:height"))
    if declared != (str(picture.width), str(picture.height)):
        found.append(f"og:image:width/height say {declared[0]}x{declared[1]}")
    if len(data) > MAX_BYTES:
        found.append(f"the picture is {len(data) // 1024} KB, over the {MAX_BYTES // 1024} KB WhatsApp accepts")
    if tags.get("twitter:card") != "summary_large_image":
        found.append("twitter:card is not summary_large_image")
    found.extend(f"{key} is missing" for key in ("og:title", "og:description", "og:url") if not tags.get(key))
    return found


def clipped(lines: list[str], count: int):
    """The first count lines, the last ending in an ellipsis when some were cut."""
    if len(lines) <= count:
        return lines
    return [*lines[: count - 1], lines[count - 1].rstrip(".,;: ") + "…"]


def draw_text(draw: ImageDraw.ImageDraw, left: int, top: int, width: int, tags: dict[str, str], lang: str, title_lines: int, description_lines: int):
    """Title, description and host in a column; returns the y below them."""
    bold, light = fonts(lang)
    rtl = lang in RTL
    direction = "rtl" if rtl else None
    edge = left + width if rtl else left
    anchor = "ra" if rtl else "la"
    host = urllib.parse.urlparse(tags.get("og:url", "")).hostname or ""
    blocks = (
        (tags.get("og:title", ""), ImageFont.truetype(str(bold), 19), INK, title_lines, 25, direction),
        (tags.get("og:description", ""), ImageFont.truetype(str(light), 15), FADED, description_lines, 20, direction),
        (host, ImageFont.truetype(str(OUTFIT_LIGHT), 14), FADED, 1, 20, None),
    )
    for text, font, colour, count, leading, text_direction in blocks:
        for line in clipped(wrap(draw, text, font, width, text_direction), count):
            draw.text((edge, top), line, font=font, fill=colour, anchor=anchor, direction=text_direction)
            top += leading
        top += 3
    return top


def mockup(tags: dict[str, str], picture: Image.Image, lang: str):
    """Both forms of the preview, side by side, as one image."""
    picture = picture.convert("RGB")
    canvas = Image.new("RGB", (1010, 470), CHAT)
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype(str(OUTFIT_LIGHT), 16)

    # The large form: the whole card, the text under it.
    left, top = 30, 60
    draw.text((left, top - 30), "Large preview: the whole card", font=label, fill=FADED)
    large = picture.resize((LARGE_WIDTH, LARGE_WIDTH * picture.height // picture.width), Image.Resampling.LANCZOS)
    bottom = top + PAD + large.height
    draw.rounded_rectangle((left, top, left + LARGE_WIDTH + 2 * PAD, bottom + 105), 10, fill=BUBBLE)
    draw.rectangle((left + PAD, bottom, left + PAD + LARGE_WIDTH, bottom + 95), fill=PANEL)
    canvas.paste(large, (left + PAD, top + PAD))
    draw_text(draw, left + 2 * PAD, bottom + 8, LARGE_WIDTH - 2 * PAD, tags, lang, 1, 2)

    # The small form: a square cut from the middle of the card, the text beside it.
    left, width = 580, 400
    draw.text((left, top - 30), "Small preview: the middle square", font=label, fill=FADED)
    draw.rounded_rectangle((left, top, left + width, top + THUMB + 2 * PAD), 10, fill=BUBBLE)
    draw.rectangle((left + PAD, top + PAD, left + width - PAD, top + PAD + THUMB), fill=PANEL)
    canvas.paste(ImageOps.fit(picture, (THUMB, THUMB), Image.Resampling.LANCZOS), (left + PAD, top + PAD))
    draw_text(draw, left + THUMB + 2 * PAD, top + PAD + 4, width - THUMB - 4 * PAD, tags, lang, 2, 1)

    # The same square enlarged, to judge what the thumbnail is made of.
    top += THUMB + 2 * PAD + 50
    draw.text((left, top - 30), "The middle square, enlarged", font=label, fill=FADED)
    canvas.paste(ImageOps.fit(picture, (ENLARGED, ENLARGED), Image.Resampling.LANCZOS), (left, top))
    return canvas


def main():
    parser = argparse.ArgumentParser(description="Show the share card of a post: what a chat app shows for its link.")
    parser.add_argument("post", help="a post file, a slug, or a URL of the site")
    parser.add_argument("--lang", choices=LANGUAGES, default="en", help="the language of a post named by slug (default: en)")
    parser.add_argument("--local", action="store_true", help="read the built _site/ instead of the live site")
    parser.add_argument("--no-open", action="store_true", help="write the mock-up but do not open it")
    args = parser.parse_args()

    url = page_url(args.post, args.lang)
    html, _ = read(url, local=args.local)
    tags = meta_tags(html.decode("utf-8", errors="replace"))
    print(f"page   {url}" + ("  (from _site/)" if args.local else ""))
    for key in ("og:title", "og:description", "og:url", "og:image", "og:image:width", "og:image:height", "twitter:card"):
        print(f"{key:<16} {tags.get(key, '(missing)')}")
    if "og:image" not in tags:
        die("the page names no og:image, so a shared link gets no picture")

    data, content_type = read(tags["og:image"], local=args.local)
    picture = Image.open(io.BytesIO(data))
    print(f"picture          {picture.width}x{picture.height} {picture.format}, {len(data) // 1024} KB")

    locale = tags.get("og:locale", "")[:2]
    lang = locale if locale in LANGUAGES else "en"
    with tempfile.NamedTemporaryFile(prefix="share-card-", suffix=".png", delete=False) as out:
        mockup(tags, picture, lang).save(out, "PNG")
    print(f"mock-up          {out.name}")
    if not args.no_open:
        subprocess.run(["xdg-open", out.name], check=False)

    found = problems(tags, data, content_type, picture)
    for problem in found:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
