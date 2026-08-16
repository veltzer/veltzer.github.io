#!/usr/bin/env python

"""
Convert the MkDocs blog posts under blog/posts/ into Zola content/blog/.

MkDocs uses YAML front matter delimited by ---, an H1 in the body as the title,
and nested YYYY/MM directories. Zola wants TOML front matter delimited by +++,
the title as a front-matter key, and a flat directory where a translation is a
sibling file named <base>.<lang>.md.

Idempotent: safe to re-run, it rewrites content/blog from blog/posts each time.

Usage:
  scripts/mkdocs_to_zola.py [--check]

  --check  report what would change without writing anything
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "blog" / "posts"
DEST = REPO_ROOT / "content" / "blog"

SECTION_INDEX = """+++
title = "Blog"
sort_by = "date"
paginate_by = 10
template = "blog.html"
page_template = "page.html"
generate_feeds = true
+++
"""


SECTION_INDEX_HE = """+++
title = "בלוג"
sort_by = "date"
paginate_by = 10
template = "blog.html"
page_template = "page.html"
generate_feeds = true
+++
"""


def toml_string(value):
    """Quote a value as a TOML basic string."""
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def toml_array(values):
    return "[" + ", ".join(toml_string(v) for v in values) + "]"


def split_front_matter(text):
    """Return (metadata dict, body) for a MkDocs post."""
    if not text.startswith("---\n"):
        raise ValueError("no YAML front matter")
    end = text.index("\n---\n", 3)
    meta = yaml.safe_load(text[4:end]) or {}
    return meta, text[end + 5:].lstrip("\n")


def extract_title(body, fallback):
    """Pull the H1 out of the body; Zola takes the title from front matter."""
    match = re.search(r"^# (.+)$", body, re.M)
    if not match:
        return fallback, body
    title = match.group(1).strip()
    body = body[:match.start()] + body[match.end():]
    return title, body.lstrip("\n")


# The Euthyphro pair carried hand-written "also available in ..." lines from
# before the language switcher existed. page.translations renders that now, so
# these would be a duplicate -- strip them on conversion.
REDUNDANT_TRANSLATION_LINK = re.compile(
    r"^\*(?:Also available in Hebrew|תרגום לעברית של).*$\n\n?", re.M)


def strip_redundant_links(body):
    """Drop manual translation links now handled by the language switcher."""
    return REDUNDANT_TRANSLATION_LINK.sub("", body)


def rewrite_links(body):
    """Rewrite inter-post links to Zola's @/ syntax.

    MkDocs links look like (../04/some_post.md) and resolve against the source
    tree. Zola resolves @/path/from/content/root.md, and the flat layout means
    the month directories disappear.
    """
    def repl(match):
        target = Path(match.group(1)).name
        base = target[:-3] if target.endswith(".md") else target
        base = base[:-3] if base.endswith(".he") else base
        return f"(@/blog/{base}.md)"

    return re.sub(r"\((?:\.\./)*(?:\d{4}/\d{2}/)?([\w./-]+\.md)\)", repl, body)


def target_name(stem, lang):
    """Flat filename, using Zola's <base>.<lang>.md translation convention."""
    if lang and lang != "en":
        # our Hebrew posts are named *_he; drop that in favour of the suffix
        base = stem[:-3] if stem.endswith("_he") else stem
        return f"{base}.{lang}.md"
    return f"{stem}.md"


def convert(path):
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    title, body = extract_title(body, path.stem)
    body = strip_redundant_links(rewrite_links(body))

    date = meta.get("date")
    if date is None:
        raise ValueError(f"{path}: no date")

    lines = ["+++", f"title = {toml_string(title)}", f"date = {date}"]
    tags = [str(t) for t in (meta.get("tags") or [])]
    if tags:
        lines += ["", "[taxonomies]", f"tags = {toml_array(tags)}"]
    lines += ["+++", "", body]
    return meta.get("lang", "en"), target_name(path.stem, meta.get("lang")), "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Convert MkDocs posts to Zola")
    parser.add_argument("--check", action="store_true",
                        help="report without writing")
    args = parser.parse_args()

    posts = sorted(SRC.rglob("*.md"))
    if not posts:
        print(f"ERROR: no posts under {SRC}", file=sys.stderr)
        return 1

    converted = {}
    for path in posts:
        try:
            lang, name, text = convert(path)
        except (ValueError, KeyError) as error:
            print(f"ERROR: {path}: {error}", file=sys.stderr)
            return 1
        if name in converted:
            print(f"ERROR: {name} written twice (from {path})", file=sys.stderr)
            return 1
        converted[name] = (lang, text)

    langs = {}
    for lang, _ in converted.values():
        langs[lang] = langs.get(lang, 0) + 1

    if args.check:
        print(f"would write {len(converted)} posts to {DEST}")
        for lang, count in sorted(langs.items()):
            print(f"  {lang}: {count}")
        return 0

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    (DEST / "_index.md").write_text(SECTION_INDEX, encoding="utf-8")
    # Zola has no language fallback for section indexes: without this the /he/
    # build fails with "Section `blog/_index.md` not found for language `he`".
    (DEST / "_index.he.md").write_text(SECTION_INDEX_HE, encoding="utf-8")
    for name, (_, text) in converted.items():
        (DEST / name).write_text(text, encoding="utf-8")

    print(f"wrote {len(converted)} posts to {DEST}")
    for lang, count in sorted(langs.items()):
        print(f"  {lang}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
