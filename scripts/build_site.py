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


def base_url():
    """The base_url from config.toml, so sitemap rewriting matches the build."""
    for line in (REPO_ROOT / "config.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("base_url"):
            return line.split("=", 1)[1].strip().strip('"\'')
    return "https://veltzer.org"


def relocate_english(root):
    """Move the English pages under /en/ so both languages are prefixed.

    Zola always serves its default language at the site root and offers no way
    to prefix it -- verified: making another language the default just hands the
    root to that one instead. So the move happens after the build.

    The result is symmetrical: /en/blog/x/ and /he/blog/x/ both serve real
    pages, and neither language is privileged by the URL layout. The root then
    gets a small language-choice page (write_root_index below).

    Static assets and the shared JS/CSS stay at the root, because the pages
    reference them with absolute paths.
    """
    english = root / "en"
    english.mkdir(exist_ok=True)
    for entry in list(root.iterdir()):
        if entry.name in SHARED_ROOT:
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
            if path and not path.startswith(("he/", "en/")) and not path.endswith(".html"):
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
        sync_theme()
        build(zola)
        relocate_english(OUTPUT_DIR)
        fix_sitemap(OUTPUT_DIR, base_url())
        write_root_index(OUTPUT_DIR)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
