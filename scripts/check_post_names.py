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
translation pair consistent: rssite pairs the files by name, so equal names
mean equal `date` and `slug` in every language.

It also checks that the translations exist: every post is in English and in
Hebrew, and a Russian post translates an English one. That is
require_translations' job, but rssite applies it to every language of the
section, and the Russian blog is still partial (content/blog/_index.ru.md).

And, for the same reason, the links of a Russian post: one to a post that
has no Russian translation names the English one (@/blog/<stem>.en.md,
since a plain @/blog/<stem>.md means this language and rssite fails on it),
and once the Russian translation exists the link must say @/blog/<stem>.md.
"""

import re
import sys
import tomllib
from pathlib import Path

MAX_WORDS = 4
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME = re.compile(r"(?P<stem>.+)\.(?P<lang>en|he|ru)\.md")
# The languages every post must exist in; Russian is optional.
REQUIRED = ("en", "he")
ENGLISH_LINK = re.compile(r"@/blog/(?P<stem>[^)#\s]+)\.en\.md")


def problems(path: Path) -> list[str]:
    name = NAME.fullmatch(path.name)
    if name is None:
        return ["the file name does not end in .en.md, .he.md or .ru.md"]
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
    for lang in REQUIRED:
        if not path.with_name(f"{name['stem']}.{lang}.md").is_file():
            found.append(f"no {lang} translation ({name['stem']}.{lang}.md)")
    if name["lang"] == "ru":
        for link in ENGLISH_LINK.finditer(parts[2]):
            if path.with_name(f"{link['stem']}.ru.md").is_file():
                found.append(f"{link[0]} has a Russian translation now: link @/blog/{link['stem']}.md")
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
