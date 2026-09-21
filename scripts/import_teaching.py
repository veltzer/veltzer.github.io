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

Three things are dropped on the way in:
  - the embedded <header>, which duplicates this site's header
  - the page's own theme <select>, which duplicates the one in our top bar
  - the inlined copy of shared-themes/theme-switcher.js and the call that
    wires it up: base.html loads the same file and calls initThemeSwitcher()
    itself. Left in, the copy's top-level `const THEME_STORAGE_KEY` collides
    with the shared file's and the browser rejects the second script with a
    SyntaxError, so the header select ended up wired twice by the inline copy.
Both sites persist the theme under the same `veltzer-site-theme` localStorage
key, so the shared switcher serves the imported page unchanged.

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

# (section name, sibling repo, page title, meta description); nav order comes
# from config.toml. The description feeds <meta name="description"> and
# og:description via base.html; without one the page falls back to the
# whole-site blurb. The Hebrew stub _index.he.md carries its own.
SITES = [
    ("slides", "teaching-slides", "Teaching Slides",
     "Browse Mark Veltzer's teaching slides by course and lecture, with a PDF of every deck."),
    ("syllabi", "teaching-syllabi", "Teaching Syllabi",
     "Syllabi for the courses Mark Veltzer teaches, browsable by track and course, with PDF and Word versions to download."),
    ("animations", "teaching-animations", "Teaching Animations",
     "Interactive animations Mark Veltzer uses in teaching: mutexes, race conditions, pipes, fork, Diffie-Hellman, buffer overflows and more."),
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
description = "{description}"
template = "app.html"
+++

'''


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def strip_theme_switcher(code):
    """Remove the inlined shared-themes/theme-switcher.js from a script.

    The sibling builds paste the file verbatim into their classic <script>:
    a header comment naming the file, `const THEME_STORAGE_KEY`, and
    `function initThemeSwitcher(options) {...}`; the syllabi build also
    exports it as `window.initThemeSwitcher`. Somewhere later the page calls
    `initThemeSwitcher();`. All of that is provided by base.html on this
    site, so every piece goes. The function body is found by brace counting
    rather than a regex so a newer upstream copy still strips cleanly.
    """
    start = code.find("const THEME_STORAGE_KEY")
    if start == -1:
        return code
    # The header comment mentions "veltzer.org/*", so searching backwards for
    # the nearest "/*" lands inside it; anchor on the file name line instead.
    header = re.search(r"/\*\s*\n \* shared-themes/theme-switcher\.js\b", code)
    if header and header.start() < start:
        start = header.start()
    func = code.find("function initThemeSwitcher", start)
    if func == -1:
        die("theme-switcher constant found without its function")
    depth = 0
    end = None
    for i in range(code.index("{", func), len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        die("unbalanced braces in the inlined theme switcher")
    code = code[:start] + code[end:]
    code = re.sub(r"^[ \t]*window\.initThemeSwitcher = initThemeSwitcher;[ \t]*\n?",
                  "", code, flags=re.MULTILINE)
    code = re.sub(r"^[ \t]*initThemeSwitcher\([^)]*\);[ \t]*\n?", "", code,
                  flags=re.MULTILINE)
    # Collapse the blank run the removal leaves behind.
    return re.sub(r"\n{3,}", "\n\n", code)


def extract(html, wrapper):
    """Pull the style, body markup and scripts out of a standalone document."""
    styles = re.findall(r"<style>(.*?)</style>", html, re.DOTALL)
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL)
    if not body:
        return None
    body = body.group(1)

    # The embedded header duplicates this site's own.
    body = re.sub(r"<header\b.*?</header>", "", body, flags=re.DOTALL)
    # app.html already emits the page's <h1> from the section title, so the
    # app's own top heading becomes an <h2>: two h1s on one page is the thing
    # search engines and screen readers both complain about. The stylesheets
    # are rewritten to match below.
    body = re.sub(r"<h1\b", "<h2", body)
    body = body.replace("</h1>", "</h2>")
    # So does its theme picker. It also carries id="theme-select", the same id
    # our own header control uses, so leaving it in means initThemeSwitcher()
    # can bind to the wrong element. Both sites write the same
    # `veltzer-site-theme` key, so dropping this one loses nothing.
    body = re.sub(r"<md-outlined-select[^>]*id=\"theme-select\".*?</md-outlined-select>",
                  "", body, flags=re.DOTALL)
    body = re.sub(r'<select[^>]*id="theme-select".*?</select>', "", body, flags=re.DOTALL)

    # Scripts from <head> too, not just <body>: these sites load Material Web
    # Components with a module import in the head, and without it the custom
    # elements never upgrade and render as raw inline text.
    head = re.search(r"<head[^>]*>(.*?)</head>", html, re.DOTALL)
    head_scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>",
                              head.group(1) if head else "", re.DOTALL)
    body_scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", body, re.DOTALL)
    scripts = [(attrs, strip_theme_switcher(code))
               for attrs, code in head_scripts + body_scripts]
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.DOTALL)

    # Scope the imported CSS so it cannot style the rest of the site. Rules that
    # target the document itself become rules on the wrapper.
    scoped = []
    for sheet in styles:
        # Strip comments first: a /* ... */ containing a brace would otherwise
        # be split as if it were a rule and end up with a selector glued on.
        sheet = re.sub(r"/\*.*?\*/", "", sheet, flags=re.DOTALL)
        # Follow the h1 -> h2 demotion of the markup. Only stylesheets: the
        # scripts' inline SVG paths contain "h1" as a path command.
        sheet = re.sub(r"\bh1\b", "h2", sheet)
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

    for section, repo, title, description in SITES:
        source = SIBLINGS / repo / "_site" / "index.html"
        if not source.is_file():
            die(f"{source} not found. Build {repo} first.")
        wrapper = f"app-{section}"
        page = build_page(source.read_text(encoding="utf-8"), wrapper)
        if page is None:
            die(f"{source}: no <body> found")
        page = rewrite_assets(page, repo)

        # _index.en.md, like every other section: the default language is the
        # phantom "cs" (see config.toml), so the English body carries an
        # explicit suffix and zola files it under /en/ itself. The Hebrew
        # _index.he.md stub is hand-written and pulls this body in through
        # templates/app_body.html, so it is not regenerated here.
        dest = REPO_ROOT / "content" / section / "_index.en.md"
        text = FRONT_MATTER.format(title=title, description=description) + page
        if args.check:
            print(f"would write {dest} ({len(text):,} bytes)")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"wrote {dest} ({len(text):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
