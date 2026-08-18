#!/usr/bin/env python

"""
Compute blog statistics and write them into the blog section front matter, so
templates can render them without computing anything.

Targets:
  content/blog/_index.en.md          the English blog index
  content/blog/_index.he.md          its Hebrew translation

Only the [extra.stats] table is generated. Everything above the marker line is
left exactly as it was, so the hand-written section keys (sort_by, paginate_by,
template, ...) survive regeneration.

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

# Everything from this line to the end of the front matter is replaced.
MARKER = "# BEGIN generated stats -- written by scripts/gen_stats.py"

FRONT_MATTER = re.compile(r"\A\+\+\+\n(.*?)\n\+\+\+\n", re.DOTALL)
DATE_LINE = re.compile(r"^date\s*=\s*(\d{4})-\d{2}-\d{2}\s*$", re.MULTILINE)


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


if __name__ == "__main__":
    main()
