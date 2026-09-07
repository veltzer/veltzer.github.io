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

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "_site"
IMPORTER = REPO_ROOT / "scripts" / "import_teaching.py"
STATS_GENERATOR = REPO_ROOT / "scripts" / "gen_stats.py"
SIBLINGS_PRESENT = all(
    (REPO_ROOT.parent / name / "_site" / "index.html").is_file()
    for name in ("teaching-slides", "teaching-syllabi", "teaching-animations")
)
THEME_SRC = REPO_ROOT / "shared" / "shared-themes"
THEME_DEST = REPO_ROOT / "static" / "shared-themes"
# Files taken from the shared-themes submodule. themes.css carries the palette;
# theme-switcher.js is copied so a theme picker can be added without another
# build change.
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
#   * Root-level zola URLs from before relocate_english() moved English under
#     /en/. These differ from the live URL by that one path segment.
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
    "blog/algo-trading-short-timescales":
        "/en/blog/algo-trading-short-timescales/",
    "calendar": "/en/calendar/",
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


# Files that belong to the site as a whole rather than to one language, so they
# stay at the root when the English pages move under /en/.
SHARED_ROOT = {
    "he", "en", "images", "data", "vendor", "shared-themes", "search_index.en.js",
    "elasticlunr.min.js", "style.css", "custom.css", "shared.css", "keys.js",
    "favicon.svg", "robots.txt", "sitemap.xml", "404.html", ".nojekyll",
}

# Sections that stay at the site root instead of moving under /en/.
#
# Empty, and deliberately kept rather than deleted. The app sections (media,
# calendar, chess, slides, syllabi, animations) used to be listed here because
# they existed only in English, so prefixing them would have claimed a
# translation that did not exist. They now have Hebrew sections -- stubs that
# reuse the English body, see templates/app_body.html -- so /en/chess/ and
# /he/chess/ are both real and the apps are prefixed like everything else. That
# is what stops a Hebrew reader losing their language when they open an app.
#
# The name is still referenced by relocate_english() and fix_sitemap() below,
# which is why the set survives its own contents. Both treat membership as
# "leave this at the site root"; with the set empty, nothing is left there.
APP_SECTIONS: set[str] = set()


def base_url():
    """The base_url from config.toml, so sitemap rewriting matches the build."""
    for line in (REPO_ROOT / "config.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("base_url"):
            return line.split("=", 1)[1].strip().strip('"\'')
    return "https://veltzer.org"


def relocate_english(root):
    """Move the English pages under /en/ so both languages are prefixed.

    Still load-bearing, despite default_language now being the empty "cs" (see
    config.toml). Zola emits the blog and its pages under /en/ and /he/ itself,
    so there is nothing to do for those -- but the six application sections
    (media, calendar, chess, slides, syllabi, animations) are default-language
    files, so zola writes them to the site root. This is what moves them to
    /en/, and without it /en/chess/ and friends do not exist.

    Verified by diffing a build with this step removed: the six app directories
    stay at the root and never appear under /en/.

    The result is symmetrical: /en/blog/x/ and /he/blog/x/ both serve real
    pages, and neither language is privileged by the URL layout. The root then
    gets a small language-choice page (write_root_index below).

    Static assets and the shared JS/CSS stay at the root, because the pages
    reference them with absolute paths.
    """
    english = root / "en"
    english.mkdir(exist_ok=True)
    for entry in list(root.iterdir()):
        if entry.name in SHARED_ROOT or entry.name in APP_SECTIONS:
            continue
        # index.html is the English home page and has to move with the rest of
        # the English site -- without this it stays at the root and is then
        # overwritten by the language chooser, leaving /en/ with no index.
        if entry.name == "index.html":
            shutil.move(str(entry), str(english / entry.name))
            continue
        # Other standalone .html files at the root are redirects or legacy app
        # pages; leave them where they are so old links keep working.
        if entry.is_file() and entry.suffix == ".html":
            continue
        if entry.is_file() and entry.suffix in {".xml", ".json", ".js", ".css", ".txt"}:
            continue
        shutil.move(str(entry), str(english / entry.name))


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


def drop_duplicate_urls(lines):
    """Drop <url> blocks whose <loc> was already emitted.

    Zola lists the taxonomy list page twice -- once as a default-language page
    at /tags/, which the rewrite above turns into /en/tags/, and once as the
    real English /en/tags/. The two collide only after rewriting, so this has to
    run on the rewritten lines rather than being avoided earlier.

    A duplicate <loc> is not an error to a crawler, which dedupes by URL anyway,
    but a sitemap that lists the same page twice misreports the site's size and
    invites the question every time someone counts the entries.

    Blocks are matched structurally: <url> ... </url>, keyed on the <loc> inside.
    Anything outside a <url> block (the XML declaration, <urlset>) is passed
    through untouched.
    """
    seen = set()
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
                if loc is None or loc not in seen:
                    if loc is not None:
                        seen.add(loc)
                    out.extend(block)
                block = None
            continue
        out.append(line)
    if block is not None:
        # Unterminated <url> block: keep it rather than silently dropping URLs.
        out.extend(block)
    return out


def fix_sitemap(root, site_url):
    """Point the sitemap at the relocated English URLs.

    Zola writes the sitemap before relocate_english() runs, so every English
    entry still claims the site root -- URLs that now 404. Rewrite them to
    their /en/ equivalents and add the root itself.

    The root needs adding explicitly because the rewrite consumes it: zola emits
    one bare <loc> for the site root, and the `elif not path` branch below turns
    that entry INTO the /en/ one rather than leaving it behind. Both belong in
    the sitemap -- "/" is the URL people link to and type, and it serves the
    language chooser (write_root_index), so it is a real 200 rather than a
    redirect. Leaving it out means the most-linked URL on the site is the one
    URL the sitemap never mentions.
    """
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        return
    text = sitemap.read_text(encoding="utf-8")
    prefix = site_url.rstrip("/") + "/"
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<loc>") and prefix in stripped:
            path = stripped[len("<loc>"):-len("</loc>")][len(prefix):]
            # Hebrew pages and shared assets already have the right URL.
            first = path.split("/", 1)[0]
            if (path and not path.startswith(("he/", "en/"))
                    and first not in APP_SECTIONS and not path.endswith(".html")):
                line = line.replace(prefix + path, prefix + "en/" + path)
            elif not path:
                line = line.replace(prefix, prefix + "en/")
        out.append(line)

    out = drop_duplicate_urls(out)
    out = drop_redirecting_urls(out)

    # Append the root. Done after the loop rather than by tweaking the rewrite
    # branch, so the /en/ entry keeps zola's own position and metadata and this
    # is a pure addition. Guarded so a future zola that emits the root itself
    # does not end up listing it twice.
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

    Has to run AFTER relocate_english(), not as zola `aliases` in the posts'
    front matter. Zola writes an alias for a default-language page to the site
    root, and relocate_english() then sweeps every root directory into /en/ --
    so an alias for /blog/x/ is built, moved, and ends up serving /en/blog/blog/x/
    while the URL it was written to rescue still 404s. Verified by building with
    one such alias in place. Writing the files here puts them past that move.

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
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )


def main():
    zola = find_zola()
    try:
        import_teaching()
        gen_stats()
        write_build_info()
        sync_theme()
        build(zola)
        relocate_english(OUTPUT_DIR)
        write_legacy_redirects(OUTPUT_DIR, base_url())
        fix_sitemap(OUTPUT_DIR, base_url())
        write_root_index(OUTPUT_DIR)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
