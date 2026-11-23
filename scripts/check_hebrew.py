#!/usr/bin/env python

"""
Check that what a Hebrew reader is handed outside the pages is Hebrew: the
feeds and the share cards.

Run by rsconstruct (processor.checker.script.hebrew_posts, hebrew_strings
and hebrew_feeds) with the files to check as arguments:

  check_hebrew.py <file> [<file> ...]

What is checked depends on the file:

- `content/blog/*.he.md`, a Hebrew post: its `title` and `description`
  contain Hebrew, and so does every tag that is not a technical name
  (LATIN_TAGS). The title and the tags are the text of the post's share
  card (scripts/make_post_cards.py) and of its feed entry.
- `i18n/he.toml`: `home_title`, whose first part is the name at the top of
  every Hebrew share card.
- `_site/he/**/atom.xml`, a built Hebrew feed: every piece of text outside
  the post bodies contains Hebrew, which is the feed's title, each entry's
  title and each author name. This is the half that catches the generator
  or its configuration slipping an English string in (it happened: tag
  feeds carried the English site title and every entry an English author
  name until 2026-11-19).

"Contains Hebrew" means at least one Hebrew letter, so a title such as
"MkDocs עם GitHub Pages" passes and one left untranslated does not. The
bodies of the posts are not this script's job: doc/TRANSLATION.md says how
those were audited.
"""

import re
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

HEBREW = re.compile(r"[֐-׿]")

# Tags that are names of technologies and stay as they are in Hebrew
# (doc/TRANSLATION.md, "Not translated, by decision").
LATIN_TAGS = {"mysql", "php"}

ATOM = "{http://www.w3.org/2005/Atom}"
# Feed elements whose text is a post body or is not prose at all.
NOT_PROSE = {"content", "summary", "id", "updated", "published", "generator"}


def is_hebrew(text: str) -> bool:
    return HEBREW.search(text) is not None


def post_problems(path: Path) -> list[str]:
    parts = path.read_text(encoding="utf-8").split("+++")
    if len(parts) < 3 or parts[0].strip():
        return ["no TOML front matter between +++ lines"]
    front = tomllib.loads(parts[1])
    found = []
    for key in ("title", "description"):
        value = front.get(key)
        if not isinstance(value, str) or not is_hebrew(value):
            found.append(f"{key} has no Hebrew in it: {value!r}")
    found.extend(
        f"tag {tag!r} is not translated (or add it to LATIN_TAGS)"
        for tag in front.get("taxonomies", {}).get("tags", [])
        if tag not in LATIN_TAGS and not is_hebrew(tag)
    )
    return found


def strings_problems(path: Path) -> list[str]:
    strings = tomllib.loads(path.read_text(encoding="utf-8"))
    title = strings.get("home_title")
    if not isinstance(title, str) or not is_hebrew(title.partition(" \u2013 ")[0]):
        return [f"home_title does not start with a Hebrew name: {title!r}"]
    return []


def feed_problems(path: Path) -> list[str]:
    found = []
    for element in ET.parse(path).getroot().iter():
        name = element.tag.removeprefix(ATOM)
        text = (element.text or "").strip()
        if name not in NOT_PROSE and text and not is_hebrew(text):
            found.append(f"<{name}> has no Hebrew in it: {text!r}")
    # One line per distinct problem: an English author name is on every entry.
    return sorted(set(found))


def problems(path: Path) -> list[str]:
    if path.name.endswith(".he.md"):
        return post_problems(path)
    if path.name == "he.toml":
        return strings_problems(path)
    if path.suffix == ".xml":
        return feed_problems(path)
    return ["not a Hebrew post, i18n/he.toml or a feed: nothing here knows how to check it"]


def main() -> int:
    status = 0
    for arg in sys.argv[1:]:
        for problem in problems(Path(arg)):
            print(f"{arg}: {problem}")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
