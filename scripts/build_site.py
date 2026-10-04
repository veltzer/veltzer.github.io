#!/usr/bin/env python

"""
The site build steps around zola, one subcommand per rsconstruct product.

Zola itself is run by rsconstruct's processor.mass_generator.zola, which
plans every file zola writes and caches each one. What zola cannot produce
is done here, each step declaring exactly what it reads and writes in
rsconstruct.toml so rsconstruct can order, cache and restore it:

  build-info     out/build_info.toml, the commit the About page names
  shared-themes  _site/shared-themes/*, copied from the shared-themes submodule
  companies      _site/data/companies.json.gz and _site/logos/
  root-feed      _site/atom.xml, a copy of the English feed
  redirects      the legacy-URL redirect stubs (a mass generator: --plan
                 prints the files it will write)

build-info, shared-themes, companies and root-feed are explicit processors:
rsconstruct appends `--inputs ... --output-files ... [--output-dirs ...]`.

What used to be done here and no longer is:
  - the language chooser at "/" and the sitemap clean-up are zola's job now
    (templates/lang_choice.html, templates/sitemap.xml);
  - gen_stats.py is a checker (`rsconstruct fix` regenerates the stats);
  - import_teaching.py reads the sibling teaching-* repos and rewrites
    committed content, so it is run by hand, not by the build.

Posts are authored directly in content/blog/. The old blog/posts/ tree and
scripts/mkdocs_to_zola.py were the one-time migration path and have been
retired: the converter rebuilt content/blog from scratch on every run, which
silently destroyed anything added there by hand -- translations included.
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "_site"
COMPANIES_IMPORTER = REPO_ROOT / "scripts" / "import_companies.py"
ORGANIZATIONS_YAML = REPO_ROOT / "data" / "yaml" / "organizations.yaml"
LOGOS_SRC = REPO_ROOT / "data" / "logos"
IMAGES_DIR = REPO_ROOT / "static" / "images"
BLOG_DIR = REPO_ROOT / "content" / "blog"


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def write_build_info(path):
    """Record the commit this build came from, for the About page to display.

    Deliberately not committed, and deliberately not produced by gen_stats.py
    alongside the archive counts: a hash written into content before committing
    can only ever name the previous commit. Reading it from git at build time is
    the only way the number on the page matches the build that produced it.

    A missing or dirty git tree is not an error. A reader cloning this repo and
    running `zola serve` still gets a site; the About page simply omits the
    provenance line, which is what the template's `if` guards.
    """
    def git(*args):
        try:
            result = subprocess.run(
                ["git", *args], check=True, cwd=REPO_ROOT,
                capture_output=True, text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
        return result.stdout.strip()

    path.parent.mkdir(parents=True, exist_ok=True)
    commit = git("rev-parse", "HEAD")
    if not commit:
        # No git available, or not a repository: the template omits the line.
        path.write_text("", encoding="utf-8")
        return
    short = git("rev-parse", "--short", "HEAD")
    # Committer date in ISO-8601, so the page can show when the source was
    # committed rather than when the build machine happened to run.
    date = git("log", "-1", "--format=%cs")
    # A dirty tree means the deployed bytes do not match the named commit.
    # Saying so is more useful than quietly naming a commit that is not what
    # was built.
    dirty = "true" if git("status", "--porcelain") else "false"
    path.write_text(
        f'commit = "{commit}"\n'
        f'short = "{short}"\n'
        f'date = "{date}"\n'
        f"dirty = {dirty}\n",
        encoding="utf-8",
    )


def copy_theme_files(sources, destinations):
    """Copy the shared-themes files into the site, next to zola's output.

    Kept as a copy rather than a symlink or a sass @import: dart-sass leaves a
    plain @import of a .css file as a runtime import, and Zola does not follow
    symlinks out of the project. The submodule is the single source of truth;
    the copy is build output.
    """
    for source, destination in zip(sources, destinations, strict=True):
        if not source.is_file():
            die(f"{source} missing. Run: git submodule update --init --recursive")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


# Legacy URLs that Google still holds, mapped to the page that serves the same
# content today. Every one of these was reported as "Not found (404)" in Search
# Console; each target was verified to return 200 before being listed here.
#
# Two generations of URL are represented:
#
#   * MkDocs-era permalinks, /YYYY/MM/DD/<slug-from-title>/. The slug came from
#     the post title, so a later retitling stranded the old URL even though the
#     post never went anywhere -- which is why divine_command_theory_problems is
#     reachable here under "what-divine-command-theory-actually-implies".
#   * Root-level zola URLs from before English moved under /en/ (2026-08).
#     These differ from the live URL by that one path segment.
#
# Redirects rather than resurrected pages: the content exists and is indexed at
# its current URL, so what the old URL owes a visitor is the way there, and what
# it owes Google is the 301-equivalent signal that consolidates the two into one
# ranking rather than leaving a dead end pointing at nothing.
LEGACY_REDIRECTS = {
    "2026/03/29/linux-io_uring-vs-windows-io-a-technical-comparison":
        "/en/blog/linux-io-uring-vs-windows-io/",
    "2026/04/14/why-wont-god-heal-amputees":
        "/en/blog/amputees-never-regrow/",
    "2026/05/06/vicarious-atonement-punishing-the-innocent-to-forgive-the-guilty":
        "/en/blog/vicarious-atonement/",
    "2026/05/13/what-divine-command-theory-actually-implies":
        "/en/blog/divine-command-theory-problems/",
    "2026/05/18/what-brain-damage-tells-us-about-the-soul":
        "/en/blog/brain-damage-disproves-the-soul/",
    # Reported 2026-09-16 as Not found (404). A retitling stranded each of
    # these the same way the five above were stranded: the MkDocs permalink
    # carried the old title's slug, and the date in the URL is the publication
    # date of the time, not the one in the post's current front matter.
    "2026/04/18/what-brain-damage-tells-us-about-the-soul":
        "/en/blog/brain-damage-disproves-the-soul/",
    "2026/04/07/religions-behave-like-memes-not-revelations":
        "/en/blog/religions-as-memes/",
    "2026/04/26/the-equivocation-of-god-one-word-many-gods":
        "/en/blog/the-equivocation-of-god/",
    # The one Hebrew MkDocs permalink Google still requests. The slug is the
    # post's Hebrew title, percent-encoded in the wild; the directory is
    # written with the literal characters and the server matches either.
    "2010/07/21/חוץ-וביטחון-יותר-ביצים-משכל":
        "/he/blog/hebrew-security-policy/",
    "blog/algo-trading-short-timescales":
        "/en/blog/algo-trading-short-timescales/",
    # Root-level post URLs from before English moved to /en/. Reported
    # 2026-09-16 as "Duplicate without user-selected canonical": Google had
    # both the old root URL and the /en/ one, neither pointed at the other,
    # so it picked its own canonical and dropped the rest. The redirect stub
    # supplies the missing signal.
    "blog/engineers-pay-for-everyones-fantasies":
        "/en/blog/engineers-pay-for-everyones-fantasies/",
    "blog/imagination-of-science-vs-fiction":
        "/en/blog/imagination-of-science-vs-fiction/",
    "blog/kant-misread-game-theory":
        "/en/blog/kant-misread-game-theory/",
    "blog/moral-progress-against-scripture":
        "/en/blog/moral-progress-against-scripture/",
    "blog/the-argument-that-convicts-itself":
        "/en/blog/the-argument-that-convicts-itself/",
    "blog/two-kinds-of-believers":
        "/en/blog/two-kinds-of-believers/",
    "blog/vicarious-atonement":
        "/en/blog/vicarious-atonement/",
    # Section roots. Every one was a real URL before English moved under /en/,
    # and they are still linked from elsewhere -- doc/IMPROVEMENTS.md recorded
    # "/blog/ is a bare 404" as an open item. The English section is the
    # target: these URLs only ever served English.
    "blog": "/en/blog/",
    "tags": "/en/tags/",
    "about": "/en/about/",
    "media": "/en/media/",
    "chess": "/en/chess/",
    "slides": "/en/slides/",
    "syllabi": "/en/syllabi/",
    "animations": "/en/animations/",
    "training": "/en/training/",
    "calendar": "/en/calendar/",
    # The chess viewer's first home, from before it was a site page at all.
    # Predates /chess.html, which is its own redirect stub in static/.
    "jschess": "/en/chess/",
    # Pagination moved under /en/ with the rest of the English site. Page 5 is
    # the only one Google reported, but the whole run was equally stranded, so
    # the loop below covers every page the archive currently has.
    "page/5": "/en/blog/page/5/",
    # An address from the pre-MkDocs site, still linked from old signatures and
    # mailing-list archives. The key itself is long gone from this repo; the
    # about page is where a reader now finds how to reach Mark.
    "ascx/public_key.asc": "/en/about/",
}

REDIRECT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="noindex, follow">
<title>Redirecting&hellip;</title>
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""



def base_url():
    for line in (REPO_ROOT / "config.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("base_url"):
            return line.split("=", 1)[1].strip().strip('"\'')
    return "https://veltzer.org"


def english_blog_pages():
    """How many pages zola paginates the English blog into.

    The redirect stubs are planned before zola runs, so the count comes from
    the sources rather than from the built tree: one page per `paginate_by`
    English posts (every post in content/blog is dated and listed).
    """
    index = (BLOG_DIR / "_index.en.md").read_text(encoding="utf-8")
    match = re.search(r"^paginate_by\s*=\s*(\d+)\s*$", index, re.MULTILINE)
    if match is None:
        die("content/blog/_index.en.md has no paginate_by")
    posts = [p for p in BLOG_DIR.glob("*.en.md") if not p.name.startswith("_index.")]
    return max(1, math.ceil(len(posts) / int(match.group(1))))


def legacy_redirect_targets():
    targets = dict(LEGACY_REDIRECTS)
    # Every /page/N/ the English blog has, not just the one Google named.
    for page in range(1, english_blog_pages() + 1):
        targets[f"page/{page}"] = f"/en/blog/page/{page}/"
    return targets


def redirect_stub_path(source):
    """The file a redirect source is written to. The .asc entry is a file
    path, not a directory URL; everything else is a directory with an
    index.html inside it."""
    return source if Path(source).suffix else f"{source}/index.html"


def write_legacy_redirects(root, site_url):
    """Write a meta-refresh stub for every retired URL.

    Written here rather than as zola `aliases` in the posts' front matter.
    Until 2026-09-21 an alias could not work at all: zola wrote it to the site
    root and relocate_english() then swept it into /en/, so it served
    /en/blog/blog/x/ while the URL it was meant to rescue still 404ed (verified
    by building with one in place; see doc/SEO.md). That sweep is gone, but
    this step stays: aliases only exist for pages, and half of what is rescued
    here is not one -- the paginator URLs expanded below, /ascx/public_key.asc,
    a section. One mechanism for every legacy URL beats two.

    GitHub Pages serves static files only, so there is no way to emit a real 301;
    a meta-refresh page with rel=canonical is the standard substitute and is what
    Google's own documentation recommends for exactly this case. `noindex, follow`
    keeps the redirect stub itself out of the index while still passing the link
    on -- without it these pages would be indexed as thin duplicates and the site
    would trade nine 404s for nine near-empty pages.

    Pagination is expanded from the number of English blog pages
    (english_blog_pages) rather than hardcoded: the archive grows, and a list
    written by hand here would silently stop covering the tail of it.
    """
    prefix = site_url.rstrip("/")
    for source, target in sorted(legacy_redirect_targets().items()):
        destination = root / redirect_stub_path(source)
        if destination.exists():
            die(f"legacy redirect {source} would overwrite a real page")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            REDIRECT_PAGE.format(target=target, canonical=prefix + target),
            encoding="utf-8",
        )


def plan_legacy_redirects(root):
    """The rsconstruct mass-generator manifest for write_legacy_redirects:
    every stub it writes, each depending on this script (the map and the
    page template) and config.toml (the base URL)."""
    sources = ["scripts/build_site.py", "config.toml"]
    outputs = [
        {"path": f"{root}/{redirect_stub_path(source)}", "sources": sources}
        for source in sorted(legacy_redirect_targets())
    ]
    print(json.dumps({"version": 1, "outputs": outputs}, indent=1))


def write_companies(output_file, logos_dir):
    """Build the companies tab's data and logos straight into the output.

    The other media tabs read committed static/data/*.json.gz files that
    scripts/copy_data.py produces by hand, because half of their sources
    live in the private ../data repo that CI cannot see. organizations.yaml
    and the logos it names live in this repo, so there is nothing to commit:
    the JSON is generated and the SVGs copied into _site/ on every build,
    after zola has populated it. The logo paths inside the YAML are relative
    to data/ (logos/<slug>.svg), and data/logos/ lands at /logos/, so the
    plugin can use them as they are.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(COMPANIES_IMPORTER), str(ORGANIZATIONS_YAML), str(output_file),
         "--images-dir", str(IMAGES_DIR)],
        check=True,
        cwd=REPO_ROOT,
    )
    if not LOGOS_SRC.is_dir():
        die(f"{LOGOS_SRC} missing")
    logos_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(LOGOS_SRC.glob("*.svg")):
        shutil.copyfile(source, logos_dir / source.name)


def copy_root_feed(feed, destination):
    """Serve the English feed at /atom.xml as well as /en/atom.xml.

    Until 2026-09-21 every page advertised /atom.xml as the site feed, and
    zola generated that file for the phantom default language: valid Atom,
    zero entries. The pages now advertise the per-language feeds and the
    phantom one is no longer generated (no top-level generate_feeds in
    config.toml), but a reader who subscribed to the advertised URL would
    otherwise get a 404 where they used to get an empty feed. GitHub Pages
    cannot redirect, so the English feed is copied there instead.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(feed, destination)


# The steps, in the order the bare command lists them, each with its line.
STEPS = {
    "build-info": "write out/build_info.toml (commit hash, dirty flag)",
    "companies": "write _site/data/companies.json.gz and _site/logos/",
    "redirects": "write the legacy-URL redirect stubs (--plan lists them)",
    "root-feed": "copy the English feed to _site/atom.xml",
    "shared-themes": "copy the shared-themes tokens into _site/shared-themes/",
}


def list_steps(prog):
    """What a bare invocation prints: the steps, nothing else."""
    width = max(len(name) for name in STEPS)
    print(f"{prog} needs a step:")
    for name, line in STEPS.items():
        print(f"  {name:<{width}}  {line}")
    print(f"Run '{prog} --help' for the options.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    sub = parser.add_subparsers(dest="step")
    for name in ("build-info", "companies", "root-feed", "shared-themes"):
        step = sub.add_parser(name, help=STEPS[name])
        # The arguments rsconstruct's explicit processor appends.
        step.add_argument("--inputs", nargs="*", type=Path, default=[])
        step.add_argument("--output-files", nargs="*", type=Path, default=[])
        step.add_argument("--output-dirs", nargs="*", type=Path, default=[])
    redirects = sub.add_parser("redirects", help=STEPS["redirects"])
    redirects.add_argument("--plan", action="store_true",
                           help="print the files the step writes, write nothing")
    args = parser.parse_args()
    if args.step is None:
        list_steps(parser.prog)
        sys.exit(2)

    try:
        if args.step == "build-info":
            write_build_info(*args.output_files)
        elif args.step == "shared-themes":
            copy_theme_files(args.inputs, args.output_files)
        elif args.step == "companies":
            write_companies(*args.output_files, *args.output_dirs)
        elif args.step == "root-feed":
            copy_root_feed(*args.inputs, *args.output_files)
        elif args.plan:
            plan_legacy_redirects(OUTPUT_DIR.relative_to(REPO_ROOT))
        else:
            write_legacy_redirects(OUTPUT_DIR, base_url())
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
