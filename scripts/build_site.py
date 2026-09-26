#!/usr/bin/env python

"""
Build the site using Zola.

Zola reads config.toml plus content/, templates/, sass/ and static/, and
writes to _site/ (kept as the output dir so the Pages workflow and the
.gitignore entries do not have to change).

Posts are authored directly in content/blog/. The old blog/posts/ tree and
scripts/mkdocs_to_zola.py were the one-time migration path and have been
retired: the converter rebuilt content/blog from scratch on every run, which
silently destroyed anything added there by hand -- translations included.

Zola is a single static binary with no runtime dependencies, so unlike the
MkDocs build there is nothing to pip install and no plugin versions to pin.
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "_site"
IMPORTER = REPO_ROOT / "scripts" / "import_teaching.py"
STATS_GENERATOR = REPO_ROOT / "scripts" / "gen_stats.py"
COMPANIES_IMPORTER = REPO_ROOT / "scripts" / "import_companies.py"
ORGANIZATIONS_YAML = REPO_ROOT / "data" / "yaml" / "organizations.yaml"
LOGOS_SRC = REPO_ROOT / "data" / "logos"
SIBLINGS_PRESENT = all(
    (REPO_ROOT.parent / name / "_site" / "index.html").is_file()
    for name in ("teaching-slides", "teaching-syllabi", "teaching-animations")
)
THEME_SRC = REPO_ROOT / "shared" / "shared-themes"
THEME_DEST = REPO_ROOT / "static" / "shared-themes"
# Files taken from the shared-themes submodule. themes.css carries the palette;
# theme-switcher.js drives the theme <select> that templates/base.html puts in
# the header.
THEME_FILES = ["themes.css", "theme-switcher.js"]
# Build provenance, written fresh on every build and read by templates through
# Zola's load_data(). Not committed: the commit that produces a build cannot be
# known before that commit exists, so a checked-in hash always names the
# previous one. static/ is where Zola looks for load_data() paths.
BUILD_INFO = REPO_ROOT / "static" / "build_info.toml"


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def find_zola():
    """Locate the zola binary, preferring one on PATH."""
    found = shutil.which("zola")
    if found:
        return found
    die("zola not found on PATH. Install it from https://www.getzola.org/")
    return None


def import_teaching():
    """Regenerate the teaching-* pages from the sibling repos' built output.

    Skipped when the siblings are absent (CI, a fresh clone) -- the committed
    content/ pages are used as-is rather than failing the build.
    """
    if not SIBLINGS_PRESENT:
        return
    subprocess.run([sys.executable, str(IMPORTER)], check=True, cwd=REPO_ROOT)


def gen_stats():
    """Recompute the blog statistics written into content/blog/_index.*.md.

    Unconditional, unlike import_teaching: it reads only content/blog, which is
    always present, so there is no sibling repo to be missing. It also verifies
    that every post is paired across languages and fails the build if not --
    an unpaired post silently loses its language switcher and nothing else
    notices.
    """
    subprocess.run([sys.executable, str(STATS_GENERATOR)], check=True, cwd=REPO_ROOT)


def write_build_info():
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

    commit = git("rev-parse", "HEAD")
    if not commit:
        # No git available, or not a repository. Leave whatever is there --
        # or nothing -- and let the template fall back to omitting the line.
        BUILD_INFO.parent.mkdir(parents=True, exist_ok=True)
        BUILD_INFO.write_text("", encoding="utf-8")
        return
    short = git("rev-parse", "--short", "HEAD")
    # Committer date in ISO-8601, so the page can show when the source was
    # committed rather than when the build machine happened to run.
    date = git("log", "-1", "--format=%cs")
    # A dirty tree means the deployed bytes do not match the named commit.
    # Saying so is more useful than quietly naming a commit that is not what
    # was built.
    dirty = "true" if git("status", "--porcelain") else "false"
    BUILD_INFO.parent.mkdir(parents=True, exist_ok=True)
    BUILD_INFO.write_text(
        f'commit = "{commit}"\n'
        f'short = "{short}"\n'
        f'date = "{date}"\n'
        f"dirty = {dirty}\n",
        encoding="utf-8",
    )


def sync_theme():
    """Copy the shared-themes files into static/ so Zola serves them.

    Kept as a copy rather than a symlink or a sass @import: dart-sass leaves a
    plain @import of a .css file as a runtime import, and Zola does not follow
    symlinks out of the project. Copying on every build means the submodule is
    the single source of truth -- editing static/shared-themes/ directly would
    be overwritten, which is the intent.
    """
    if not THEME_SRC.is_dir():
        die(f"{THEME_SRC} missing. Run: git submodule update --init --recursive")
    THEME_DEST.mkdir(parents=True, exist_ok=True)
    for name in THEME_FILES:
        source = THEME_SRC / name
        if not source.is_file():
            die(f"{source} missing from the shared-themes submodule")
        shutil.copy2(source, THEME_DEST / name)


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


ROOT_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mark Veltzer&#39;s personal site</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/shared-themes/themes.css">
<link rel="stylesheet" href="/style.css">
<link rel="alternate" hreflang="en" href="https://veltzer.org/en/">
<link rel="alternate" hreflang="he" href="https://veltzer.org/he/">
<link rel="alternate" hreflang="x-default" href="https://veltzer.org/en/">
<style>
  .lang-choice { max-width: 28rem; margin: 6rem auto; padding: 0 1.25rem; text-align: center; }
  .lang-choice h1 { margin-bottom: 2rem; }
  .lang-choice a {
    display: block; padding: 1rem; margin-bottom: 0.75rem;
    border: 1px solid var(--border); border-radius: var(--radius);
    text-decoration: none; color: var(--text-primary);
    background: var(--bg-surface);
  }
  .lang-choice a:hover { border-color: var(--accent); text-decoration: none; }
</style>
</head>
<body>
<div class="lang-choice">
  <h1>Mark Veltzer</h1>
  <a href="/en/" hreflang="en">English</a>
  <a href="/he/" hreflang="he" lang="he">עברית</a>
</div>
<script>
  // Send returning readers straight to the language they last used, but only
  // when they arrive at the root with no explicit choice -- a link to /en/ or
  // /he/ is always honoured because this page never runs for those.
  try {
    var last = localStorage.getItem("veltzer-site-lang");
    if (last === "en" || last === "he") { location.replace("/" + last + "/"); }
  } catch (e) { /* storage blocked: show the chooser */ }
</script>
</body>
</html>
"""


def base_url():
    """The base_url from config.toml, so sitemap rewriting matches the build."""
    for line in (REPO_ROOT / "config.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("base_url"):
            return line.split("=", 1)[1].strip().strip('"\'')
    return "https://veltzer.org"


def drop_redirecting_urls(lines):
    """Drop <url> blocks for paginator page/1/, which is a redirect, not a page.

    Zola gives every paginated section a /page/1/ URL and builds it as a stub
    that bounces to the paginator root -- /en/tags/atheism/page/1/ redirects to
    /en/tags/atheism/. The page is real, but that URL is not the one serving it,
    and zola lists both in the sitemap. With 55 tags per language plus the two
    blog indexes that is 112 of 629 entries pointing at a redirect.

    Search Console reports this as "Page with redirect" against a sitemap URL,
    which is a warning aimed squarely at the sitemap: a sitemap is a statement
    about canonical, indexable URLs, and an entry that redirects contradicts
    that. The redirect itself is correct and stays -- anyone holding a
    /page/1/ link still lands in the right place. It just does not belong in
    the sitemap.

    Only page/1/ is affected. page/2/ upward are real paginated pages and are
    left alone; a filter broad enough to catch them would drop the archive tail
    out of the index.
    """
    out = []
    block = None
    for line in lines:
        stripped = line.strip()
        if stripped == "<url>":
            block = [line]
            continue
        if block is not None:
            block.append(line)
            if stripped == "</url>":
                loc = next(
                    (b.strip() for b in block if b.strip().startswith("<loc>")), None
                )
                if loc is None or not loc.endswith("/page/1/</loc>"):
                    out.extend(block)
                block = None
            continue
        out.append(line)
    if block is not None:
        # Unterminated <url> block: keep it rather than silently dropping URLs.
        out.extend(block)
    return out


def fix_sitemap(root, site_url):
    """Drop the paginator redirect stubs from the sitemap and add the root.

    Zola lists every URL it emits, including /page/1/ under each paginated
    section and tag, which is a stub that bounces to the paginator root
    (see drop_redirecting_urls). It does not list "/" at all: the root section
    belongs to the phantom default language and is render = false, so the
    language chooser that write_root_index() puts there is invisible to zola.
    "/" is the URL people link to and type and it serves a real 200, so it is
    appended here.

    This used to also rewrite unprefixed English URLs to /en/ and dedupe the
    result; both went away with relocate_english() on 2026-09-21, once every
    section carried an explicit language suffix and the top-level taxonomy
    for the phantom language was dropped from config.toml. Zola now emits
    only /en/ and /he/ URLs, verified on a raw build.
    """
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        return
    prefix = site_url.rstrip("/") + "/"
    out = drop_redirecting_urls(sitemap.read_text(encoding="utf-8").splitlines())

    # Guarded so a future zola that emits the root itself does not end up
    # listing it twice.
    root_loc = f"<loc>{prefix}</loc>"
    if not any(line.strip() == root_loc for line in out):
        closing = "</urlset>"
        for index, line in enumerate(out):
            if line.strip() == closing:
                out[index:index] = ["    <url>", f"        {root_loc}", "    </url>"]
                break
        else:
            die("sitemap.xml has no </urlset> -- cannot add the root entry")

    sitemap.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_legacy_redirects(root, site_url):
    """Serve the pre-migration URLs that Google still has indexed.

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

    Pagination is expanded from whatever the build actually produced rather than
    hardcoded: the archive grows, and a list written by hand here would silently
    stop covering the tail of it.
    """
    targets = dict(LEGACY_REDIRECTS)

    # Every /page/N/ that exists under /en/blog/, not just the one Google named.
    paginated = root / "en" / "blog" / "page"
    if paginated.is_dir():
        for entry in paginated.iterdir():
            if entry.is_dir() and entry.name.isdigit():
                targets[f"page/{entry.name}"] = f"/en/blog/page/{entry.name}/"

    prefix = site_url.rstrip("/")
    for source, target in sorted(targets.items()):
        destination = root / source
        # The .asc entry is a file path, not a directory URL; everything else
        # is a directory that needs an index.html inside it.
        if destination.suffix:
            destination.parent.mkdir(parents=True, exist_ok=True)
        else:
            destination.mkdir(parents=True, exist_ok=True)
            destination = destination / "index.html"
        if destination.exists():
            die(f"legacy redirect {source} would overwrite a real page")
        destination.write_text(
            REDIRECT_PAGE.format(target=target, canonical=prefix + target),
            encoding="utf-8",
        )


def write_root_index(root):
    """A language-choice page at /, now that neither language owns the root."""
    (root / "index.html").write_text(ROOT_INDEX, encoding="utf-8")


def build(zola):
    # Zola wipes and recreates the output directory itself.
    subprocess.run(
        [zola, "build", "--output-dir", str(OUTPUT_DIR), "--force"],
        check=True,
        cwd=REPO_ROOT,
    )


def write_companies(root):
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
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(COMPANIES_IMPORTER), str(ORGANIZATIONS_YAML), str(data_dir / "companies.json.gz"),
         "--images-dir", str(REPO_ROOT / "static" / "images")],
        check=True,
        cwd=REPO_ROOT,
    )
    if not LOGOS_SRC.is_dir():
        die(f"{LOGOS_SRC} missing")
    logos_dest = root / "logos"
    logos_dest.mkdir(parents=True, exist_ok=True)
    for source in sorted(LOGOS_SRC.glob("*.svg")):
        shutil.copyfile(source, logos_dest / source.name)


def copy_root_feed(root):
    """Serve the English feed at /atom.xml as well as /en/atom.xml.

    Until 2026-09-21 every page advertised /atom.xml as the site feed, and
    zola generated that file for the phantom default language: valid Atom,
    zero entries. The pages now advertise the per-language feeds and the
    phantom one is no longer generated (no top-level generate_feeds in
    config.toml), but a reader who subscribed to the advertised URL would
    otherwise get a 404 where they used to get an empty feed. GitHub Pages
    cannot redirect, so the English feed is copied there instead.
    """
    shutil.copyfile(root / "en" / "atom.xml", root / "atom.xml")


def main():
    zola = find_zola()
    try:
        import_teaching()
        gen_stats()
        write_build_info()
        sync_theme()
        build(zola)
        write_companies(OUTPUT_DIR)
        copy_root_feed(OUTPUT_DIR)
        write_legacy_redirects(OUTPUT_DIR, base_url())
        fix_sitemap(OUTPUT_DIR, base_url())
        write_root_index(OUTPUT_DIR)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
