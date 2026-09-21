#!/usr/bin/env python

"""
Compute blog statistics and write them into the blog section front matter, so
templates can render them without computing anything.

Targets:
  content/blog/_index.en.md          the English blog index
  content/blog/_index.he.md          its Hebrew translation
  static/tag_translations.toml       which Hebrew tag is which English tag

Only the [extra.stats] table is generated in the two indexes. Everything above
the marker line is left exactly as it was, so the hand-written section keys
(sort_by, paginate_by, template, ...) survive regeneration.

The tag table is derived from the posts: a post and its translation carry the
same tags in the same order, one list per language, so zipping the two lists
says which tag is which. That alignment is an invariant this script enforces
(a pair whose lists differ in length, or a tag that maps to two different
counterparts, fails the build). templates/base.html reads the table so a tag
page's language switcher and hreflang alternates point at the same tag in the
other language rather than at that language's home page -- zola has no
translation link between taxonomy terms, only between pages and sections.

Why generate rather than compute in Tera
----------------------------------------
Zola exposes the data -- section.pages is there, and page.year with it -- but
Tera has no group_by over a derived key. Counting posts per year in a template
therefore means looping the whole section once per year against a filter, with
the year range known up front. That is both ugly and quadratic in a way that
grows with the archive. The numbers change only when a post is added, so the
build is the right place to compute them once.

Unlike gen_profiles.py this IS part of the build: it reads only content/blog,
which is always present, so there is no sibling-repo problem to work around.
The output is still committed, which keeps `zola serve` and any build that
skips this step showing the right numbers.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = REPO_ROOT / "content" / "blog"

# Languages to report, in display order. Kept here rather than parsed out of
# config.toml: adding a language to the site means touching templates and
# translations anyway, and a stray [languages.*] subtable would otherwise be
# read as a language.
LANGUAGES = ["en", "he"]
TAG_TRANSLATIONS = REPO_ROOT / "static" / "tag_translations.toml"

# Everything from this line to the end of the front matter is replaced.
MARKER = "# BEGIN generated stats -- written by scripts/gen_stats.py"

FRONT_MATTER = re.compile(r"\A\+\+\+\n(.*?)\n\+\+\+\n", re.DOTALL)
DATE_LINE = re.compile(r"^date\s*=\s*(\d{4})-\d{2}-\d{2}\s*$", re.MULTILINE)
# `tags = ["a", "b"]` inside [taxonomies]. DOTALL so a list wrapped over
# several lines still parses; the quoted strings are pulled out afterwards.
TAGS_LINE = re.compile(r"^tags\s*=\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
TAG_NAME = re.compile(r'"([^"]*)"')


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def post_years(lang):
    """Return a Counter of year -> post count for one language.

    _index files are sections, not posts, so they are skipped. A post with no
    parseable date is an error rather than a silent omission: zola would fail
    on it later anyway, and a miscount here is invisible.
    """
    years = Counter()
    for path in sorted(BLOG_DIR.glob(f"*.{lang}.md")):
        if path.name.startswith("_index."):
            continue
        match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
        if not match:
            die(f"{path} has no +++ front matter")
        date = DATE_LINE.search(match.group(1))
        if not date:
            die(f"{path} has no date in its front matter")
        years[int(date.group(1))] += 1
    return years


def check_pairing():
    """Fail if the languages disagree on which posts exist.

    An unpaired post silently loses its language switcher -- page.translations
    comes up empty and the template renders nothing -- so nothing else in the
    build notices. Counting the files is the cheapest place to catch it.
    """
    stems = {}
    for lang in LANGUAGES:
        stems[lang] = {
            path.name[: -len(f".{lang}.md")]
            for path in BLOG_DIR.glob(f"*.{lang}.md")
            if not path.name.startswith("_index.")
        }
    reference = LANGUAGES[0]
    for lang in LANGUAGES[1:]:
        missing = stems[reference] - stems[lang]
        extra = stems[lang] - stems[reference]
        for name in sorted(missing):
            print(
                f"ERROR: content/blog/{name}.{reference}.md has no .{lang}.md "
                "translation",
                file=sys.stderr,
            )
        for name in sorted(extra):
            print(
                f"ERROR: content/blog/{name}.{lang}.md has no .{reference}.md "
                "original",
                file=sys.stderr,
            )
        if missing or extra:
            sys.exit(1)


def post_tags(path):
    """The tag list of one post, in front-matter order. Empty if untagged."""
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        die(f"{path} has no +++ front matter")
    tags = TAGS_LINE.search(match.group(1))
    return TAG_NAME.findall(tags.group(1)) if tags else []


def tag_pairs(blog_dir):
    """Return the (english, hebrew) tag pairs the posts agree on, sorted.

    Every post pair contributes one (en, he) pair per tag position. The
    result must be a bijection: if an English tag ever lines up with two
    different Hebrew tags (or the reverse) the lists of some post are out of
    order, and the build stops and names the posts involved -- a silently
    wrong mapping would send a reader to an unrelated tag page.

    Takes the directory rather than using BLOG_DIR so the tests can point it
    at a fixture.
    """
    en, he = LANGUAGES
    seen = {}  # (en_tag, he_tag) -> first post that produced it
    for en_path in sorted(blog_dir.glob(f"*.{en}.md")):
        if en_path.name.startswith("_index."):
            continue
        he_path = en_path.with_name(en_path.name[: -len(f".{en}.md")] + f".{he}.md")
        if not he_path.is_file():
            continue  # check_pairing() reports these
        en_tags = post_tags(en_path)
        he_tags = post_tags(he_path)
        if len(en_tags) != len(he_tags):
            die(
                f"{en_path.name} has {len(en_tags)} tags but {he_path.name} has "
                f"{len(he_tags)}; the lists must match one to one, in order"
            )
        for pair in zip(en_tags, he_tags):
            seen.setdefault(pair, en_path.name)

    for index, lang in enumerate(LANGUAGES):
        counterparts = {}
        for pair, origin in seen.items():
            counterparts.setdefault(pair[index], {})[pair[1 - index]] = origin
        for tag, others in sorted(counterparts.items()):
            if len(others) > 1:
                detail = ", ".join(f"{other!r} in {origin}" for other, origin in sorted(others.items()))
                die(f"{lang} tag {tag!r} is translated inconsistently: {detail}")
    return sorted(seen)


def render_tag_translations(pairs):
    """Render static/tag_translations.toml: one [[terms]] row per tag pair."""
    lines = [
        "# GENERATED by scripts/gen_stats.py on every build -- do not hand-edit.",
        "#",
        "# One row per tag, derived from the posts: a post and its translation list",
        "# the same tags in the same order, so position N in one is position N in",
        "# the other. templates/base.html reads this to link a tag page to the same",
        "# tag in the other language. Committed, like the archive stats, so a build",
        "# that skips gen_stats.py still has it.",
    ]
    for pair in pairs:
        lines.append("")
        lines.append("[[terms]]")
        for lang, name in zip(LANGUAGES, pair):
            lines.append(f"{lang} = {json.dumps(name, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def render(per_language):
    """Render the [extra.stats] TOML table.

    Written as arrays of tables rather than a year-keyed table because Tera
    cannot iterate a map in a defined order, and the years must come out
    newest-first.
    """
    # "total" is distinct posts, not rendered pages. Every post exists in both
    # languages (check_pairing enforces it), so summing across languages would
    # report 190 for an archive of 95 -- true of the page count, misleading as
    # a description of the writing. "pages" carries the other number for
    # templates that want it.
    total = sum(per_language[LANGUAGES[0]].values())
    pages = sum(sum(years.values()) for years in per_language.values())
    lines = [
        MARKER,
        "#",
        "# Regenerated on every build. Do not hand-edit -- add a post instead.",
        "[extra.stats]",
        f"total = {total}",
        f"pages = {pages}",
    ]

    lines.append("")
    lines.append("# Post count per language.")
    for lang in LANGUAGES:
        count = sum(per_language[lang].values())
        lines.append("[[extra.stats.languages]]")
        lines.append(f'code = "{lang}"')
        lines.append(f"count = {count}")

    all_years = sorted(
        {year for years in per_language.values() for year in years},
        reverse=True,
    )
    lines.append("")
    lines.append("# Post count per year, newest first, broken down by language.")
    for year in all_years:
        lines.append("[[extra.stats.years]]")
        lines.append(f"year = {year}")
        # Distinct posts, matching extra.stats.total above. The per-language
        # counts follow for a template that wants to break the year down.
        lines.append(f"total = {per_language[LANGUAGES[0]][year]}")
        for lang in LANGUAGES:
            lines.append(f"{lang} = {per_language[lang][year]}")
    return "\n".join(lines)


def write_file(path, text):
    """Write a whole generated file; returns whether it changed."""
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def write(path, table):
    """Replace the generated region of one _index file, keeping the rest."""
    if not path.is_file():
        die(f"Missing {path}")
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        die(f"{path} has no +++ front matter")

    front = match.group(1)
    kept = front.split(MARKER)[0].rstrip("\n")
    new_front = f"{kept}\n\n{table}"
    updated = f"+++\n{new_front}\n+++\n{text[match.end():]}"

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main():
    if not BLOG_DIR.is_dir():
        die(f"Missing {BLOG_DIR}")

    per_language = {lang: post_years(lang) for lang in LANGUAGES}
    for lang, years in per_language.items():
        if not years:
            die(f"No {lang} posts found in {BLOG_DIR}")

    check_pairing()
    table = render(per_language)

    for lang in LANGUAGES:
        path = BLOG_DIR / f"_index.{lang}.md"
        changed = write(path, table)
        state = "wrote" if changed else "unchanged"
        print(f"{state} {path.relative_to(REPO_ROOT)}")

    changed = write_file(TAG_TRANSLATIONS, render_tag_translations(tag_pairs(BLOG_DIR)))
    state = "wrote" if changed else "unchanged"
    print(f"{state} {TAG_TRANSLATIONS.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
