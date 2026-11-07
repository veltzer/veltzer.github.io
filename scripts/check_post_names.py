#!/usr/bin/env python

"""
Check that every blog post is named after its date and its slug.

Run by rsconstruct (processor.checker.script.post_names) with the posts as
arguments:

  check_post_names.py <post.md> [<post.md> ...]

The rule (CLAUDE.md, "Blog Posts"): a post's front matter carries a short
`slug` of at most four lowercase ASCII words joined by `-`, and the file is
named `<date>-<slug>.<lang>.md`, so content/blog/ sorts by date and the URL
is the short name. The title is free to change without touching either.

Checking each file against its own front matter is enough to keep a
translation pair consistent: rssite pairs the two files by name, so equal
names mean equal `date` and `slug` in both languages.
"""

import re
import sys
import tomllib
from pathlib import Path

MAX_WORDS = 4
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME = re.compile(r"(?P<stem>.+)\.(?P<lang>en|he)\.md")


def problems(path: Path) -> list[str]:
    name = NAME.fullmatch(path.name)
    if name is None:
        return ["the file name does not end in .en.md or .he.md"]
    parts = path.read_text(encoding="utf-8").split("+++")
    if len(parts) < 3 or parts[0].strip():
        return ["no TOML front matter between +++ lines"]
    front = tomllib.loads(parts[1])
    slug = front.get("slug")
    date = front.get("date")
    found = []
    if not isinstance(slug, str):
        found.append("no `slug` in the front matter")
    elif not SLUG.fullmatch(slug):
        found.append(f"slug {slug!r} is not lowercase ASCII words joined by '-'")
    elif len(slug.split("-")) > MAX_WORDS:
        found.append(f"slug {slug!r} has more than {MAX_WORDS} words")
    if date is None:
        found.append("no `date` in the front matter")
    if not found:
        expected = f"{date}-{slug}"
        if name["stem"] != expected:
            found.append(f"the file should be named {expected}.{name['lang']}.md")
    return found


def main() -> int:
    status = 0
    for arg in sys.argv[1:]:
        for problem in problems(Path(arg)):
            print(f"{arg}: {problem}")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
