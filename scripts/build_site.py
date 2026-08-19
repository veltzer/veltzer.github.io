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


def fix_sitemap(root, site_url):
    """Point the sitemap at the relocated English URLs.

    Zola writes the sitemap before relocate_english() runs, so every English
    entry still claims the site root -- URLs that now 404. Rewrite them to
    their /en/ equivalents and add the root itself.
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
    sitemap.write_text("\n".join(out) + "\n", encoding="utf-8")


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
        fix_sitemap(OUTPUT_DIR, base_url())
        write_root_index(OUTPUT_DIR)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
