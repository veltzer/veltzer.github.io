#!/usr/bin/env python

"""
Import the teaching-* sites into content/ as native Zola pages.

Each of the sibling repos (../teaching-slides, ../teaching-syllabi,
../teaching-animations) builds a single self-contained `_site/index.html`:
inline <style>, one or two <script> blocks, and its data inline as `const DATA`.
That shape ports directly into a Zola page -- strip the document wrapper and
keep the style, markup and script -- so the browsers become part of this site
rather than being framed inside it.

Why not an iframe: a nested document brings its own scroll container and its
own chrome, which is what produced the double scrollbars and the squeezed
column. A fragment has neither.

Two things are dropped on the way in:
  - the embedded <header>, which duplicates this site's header
  - the page's own theme <select>, which duplicates the one in our top bar
Both sites already persist the theme under the same `veltzer-site-theme`
localStorage key, so the remaining theme code stays in sync with ours.

Everything is scoped under a wrapper div and the page's CSS is prefixed with
that wrapper, so the imported styles cannot leak into the rest of the site.

Usage:
  scripts/import_teaching.py [--check]
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIBLINGS = REPO_ROOT.parent

# (section name, sibling repo, page title, weight in the nav)
SITES = [
    ("slides", "teaching-slides", "Teaching Slides"),
    ("syllabi", "teaching-syllabi", "Teaching Syllabi"),
    ("animations", "teaching-animations", "Teaching Animations"),
]

# Top-level directories of each sibling's _site that hold the assets its page
# links to (PDFs, Word files, syllabus fragments, videos).
#
# Only the imported markup and data move into this site -- the assets stay in
# the sibling repo, which publishes them on its own GitHub Pages site. Those
# land under veltzer.org/<repo>/ because veltzer.github.io/<repo>/ 301s to the
# CNAME, so the rewritten links are same-origin: no CORS problem for the
# syllabi page, which fetch()es its HTML fragments rather than linking them.
#
# Without this rewrite the paths stay relative and resolve against
# veltzer.org/, where nothing serves them -- every download 404s. Copying the
# ~950MB of PDFs and video into this repo instead would blow past what a Pages
# build can carry, and CI has no access to the siblings anyway: it builds from
# a fresh checkout, so import_teaching.py does not even run there.
ASSET_ROOTS = {
    "teaching-slides": ["pdfunite", "marp"],
    "teaching-syllabi": ["courses", "tracks"],
    "teaching-animations": ["animations"],
}

FRONT_MATTER = '''+++
title = "{title}"
template = "app.html"
+++

'''


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def extract(html, wrapper):
    """Pull the style, body markup and scripts out of a standalone document."""
    styles = re.findall(r"<style>(.*?)</style>", html, re.S)
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S)
    if not body:
        return None
    body = body.group(1)

    # The embedded header duplicates this site's own.
    body = re.sub(r"<header\b.*?</header>", "", body, flags=re.S)
    # So does its theme picker. It also carries id="theme-select", the same id
    # our own header control uses, so leaving it in means initThemeSwitcher()
    # can bind to the wrong element. Both sites write the same
    # `veltzer-site-theme` key, so dropping this one loses nothing.
    body = re.sub(r"<md-outlined-select[^>]*id=\"theme-select\".*?</md-outlined-select>",
                  "", body, flags=re.S)
    body = re.sub(r'<select[^>]*id="theme-select".*?</select>', "", body, flags=re.S)

    # Scripts from <head> too, not just <body>: these sites load Material Web
    # Components with a module import in the head, and without it the custom
    # elements never upgrade and render as raw inline text.
    head = re.search(r"<head[^>]*>(.*?)</head>", html, re.S)
    head_scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>",
                              head.group(1) if head else "", re.S)
    body_scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", body, re.S)
    scripts = head_scripts + body_scripts
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S)

    # Scope the imported CSS so it cannot style the rest of the site. Rules that
    # target the document itself become rules on the wrapper.
    scoped = []
    for sheet in styles:
        # Strip comments first: a /* ... */ containing a brace would otherwise
        # be split as if it were a rule and end up with a selector glued on.
        sheet = re.sub(r"/\*.*?\*/", "", sheet, flags=re.S)
        out = []
        for rule in re.split(r"(?<=\})", sheet):
            if not rule.strip():
                continue
            if rule.lstrip().startswith("@"):
                out.append(rule)          # media/keyframes/font-face: leave alone
                continue
            head, sep, tail = rule.partition("{")
            if not sep:
                out.append(rule)
                continue
            selectors = []
            for selector in head.split(","):
                selector = selector.strip()
                if not selector:
                    continue
                if selector in (":root", "html", "body", "html, body"):
                    selectors.append(f"#{wrapper}")
                elif selector.startswith("[data-theme="):
                    # data-theme lives on <html>, an ANCESTOR of the wrapper, so
                    # this must stay a descendant combinator in that direction --
                    # scoping it as `#wrapper [data-theme=...]` would look for the
                    # attribute *inside* the app and never match, leaving the
                    # imported page on its default palette while the rest of the
                    # site changed theme.
                    rest = selector[selector.index("]") + 1:].strip()
                    attr = selector[: selector.index("]") + 1]
                    selectors.append(f"{attr} #{wrapper} {rest}".strip())
                else:
                    selectors.append(f"#{wrapper} {selector}")
            out.append(", ".join(selectors) + " {" + tail)
        scoped.append("\n".join(out))

    return scoped, body.strip(), scripts


def rewrite_assets(text, repo):
    """Point relative asset paths at the sibling site that actually serves them.

    Matches only complete double-quoted string values, so a path is rewritten
    where it is used as a URL ("pdf": "pdfunite/x.pdf") and nowhere else. That
    matters for the slides page: its `folder` values start with the same
    "courses/" segment but are grouping keys, compared against each other and
    split on "/" to build the folder tree -- prefixing those would break the
    filter rather than fix a link. They are excluded by not being under any of
    this repo's ASSET_ROOTS.
    """
    roots = ASSET_ROOTS.get(repo)
    if not roots:
        return text
    pattern = re.compile(
        r'"((?:' + "|".join(re.escape(root) for root in roots) + r')/[^"\s]*)"'
    )
    return pattern.sub(lambda m: f'"/{repo}/{m.group(1)}"', text)


def build_page(html, wrapper):
    parts = extract(html, wrapper)
    if parts is None:
        return None
    styles, body, scripts = parts
    chunks = []
    for sheet in styles:
        chunks.append(f"<style>\n{sheet}\n</style>")
    chunks.append(f'<div id="{wrapper}" class="app-root">\n{body}\n</div>')
    for attrs, code in scripts:
        chunks.append(f"<script{attrs}>{code}</script>")
    return "\n\n".join(chunks) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Import teaching-* sites")
    parser.add_argument("--check", action="store_true",
                        help="report without writing")
    args = parser.parse_args()

    for section, repo, title in SITES:
        source = SIBLINGS / repo / "_site" / "index.html"
        if not source.is_file():
            die(f"{source} not found. Build {repo} first.")
        wrapper = f"app-{section}"
        page = build_page(source.read_text(encoding="utf-8"), wrapper)
        if page is None:
            die(f"{source}: no <body> found")
        page = rewrite_assets(page, repo)

        dest = REPO_ROOT / "content" / section / "_index.md"
        text = FRONT_MATTER.format(title=title) + page
        if args.check:
            print(f"would write {dest} ({len(text):,} bytes)")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"wrote {dest} ({len(text):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
