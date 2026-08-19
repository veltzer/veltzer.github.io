# CLAUDE.md - Project Guide

## Project Overview

Mark Veltzer's personal website hosted on GitHub Pages at veltzer.org (CNAME). Combines a
bilingual blog (English + Hebrew), media consumption tracker, chess game viewer, and
calendar integration.

## Tech Stack

- **Site generator**: [zola](https://www.getzola.org/) — single Rust binary, pinned to
  v0.23.3. Templates are [Tera](https://keats.github.io/tera/) (Jinja2-like).
- **Build orchestration**: rsconstruct (single binary, configured via `rsconstruct.toml`
  and `config/*.lua`), npm
- **Frontend**: HTML5, SCSS, JavaScript (ES9+)
- **Linting**: eslint (`config/eslint.config.js`), tidy (HTML), pylint (`.pylintrc`),
  mypy (`.mypy.ini`), pytest (`tests/`), shellcheck
- **Data**: YAML/JSON for media content, PGN for chess games, Markdown for blog posts

The site used to be built with MkDocs. It is not any more — see *Migration notes* below,
which records the traps that outlived the migration.

## Directory Structure

- `config.toml` — zola config: `base_url`, taxonomies, the `[languages.he]` block, and
  `[extra.nav]` / `[extra.languages]` which drive the nav and language switcher
- `content/` — all page and post source
  - `content/blog/*.md` — blog posts, flat (no `YYYY/MM/` nesting). TOML front matter
    between `+++` lines: `title`, `date`, and a `[taxonomies]` block with `tags`
  - `content/blog/*.he.md` — Hebrew translations. The `.he` suffix is how zola pairs a
    post with its translation; nothing else is needed
  - `content/<page>/_index.md` — the standalone nav pages (about, media, calendar, …)
- `templates/` — Tera templates (`base.html`, `page.html`, `blog.html`, taxonomy pages)
- `sass/style.scss` — compiled to `/style.css` by zola
- `static/` — copied verbatim to the site root: app HTML, media plugins, images, data,
  and `vendor/` (locally vendored JS libraries)
- `shared/shared-themes/` — git submodule providing the design tokens. **Run
  `git submodule update --init --recursive` on a fresh clone or the build fails.**
- `scripts/` — `build_site.py` (the build), `gen_stats.py` (archive stats),
  image fetchers, data importers, `serve.py`
- `tests/` — pytest suite for the data import scripts
- `_site/` — generated output (gitignored, never edit)
- `doc/` — project notes, decisions and the improvements backlog

## Build Commands

- `rsconstruct build --verbose -j0` — full build (this is what CI runs)
- `rsconstruct status` — show build status
- `scripts/build_site.py` — the zola build on its own
- `scripts/serve.py` — build, then serve `_site/` locally the way Pages will

**Never run `zola build` by hand — always go through the build system.**
Bare `zola build` writes to `public/` (zola's hardcoded default; an
`output_dir` key in config.toml is silently ignored) and skips
`build_site.py`'s post-processing (`relocate_english()`, `fix_sitemap()`).
The result is a second output tree that looks authoritative but is neither
the real build nor post-processed — stale copies of it have produced wrong
page counts and false "missing post" reports. The real output is `_site/`,
and only after a build; cross-check any number you derive from it against
what the build itself reports (zola prints "Creating N pages").

### Prerequisite: zola

`scripts/build_site.py` shells out to zola, which is **not** installed by
`rsconstruct tools install`, so a fresh clone fails with
`ERROR: zola not found on PATH`. Install it by hand:

```bash
ZOLA_VERSION=v0.23.3
gh release download "$ZOLA_VERSION" --repo getzola/zola \
  --pattern '*x86_64-unknown-linux-gnu.tar.gz' --output /tmp/zola.tar.gz
tar xzf /tmp/zola.tar.gz -C ~/.local/bin zola
chmod +x ~/.local/bin/zola
zola --version   # expect: zola 0.23.3
```

Keep the version in step with rsconstruct's tool registry, which is what CI installs from:
`rsconstruct tools list-configured` prints the pinned URL. The pin is deliberate: 0.23
renamed config keys (`highlight_code` → `[markdown.highlighting]`) and swapped the
highlighter, so an unpinned upgrade can fail the build on `config.toml` alone. Distro
packages and `cargo install zola` track other versions — prefer the pinned tarball.
(`cargo install zola` in particular fetches an unrelated yanked crate, not the real zola.)

## CI and the Workflow File

- **`.github/workflows/build.yml` is deliberately minimal and maintained by
  hand — do not edit it.** It only knows how to ask rsconstruct: checkout,
  caches, download rsconstruct, `tools install-deps` + `tools install`,
  build, status, deploy. Every tool and package the build needs is declared
  in `rsconstruct.toml` instead — system packages under `[dependencies]`
  (apt/pip/npm), and tools a wrapper script shells out to via
  `required_tools` on the processor (that is how zola is installed; its
  pinned recipe lives in rsconstruct's tool registry). If something cannot
  be expressed there, the fix belongs in rsconstruct, not in the workflow.
- **Do not add infrastructure workarounds (apt retries, timeouts) to the
  workflow or to rsconstruct.** GitHub's runners occasionally sit behind a
  degraded Ubuntu mirror (observed 2026-08-19: ~60 KB/s — slow but
  progressing, so timeouts kill healthy runs and retries do nothing; a
  5-minute step timeout killed a healthy release build the same day). When
  a run is slow or stuck: cancel it (this finalizes its logs, which show
  what it was doing) and re-run — a fresh runner usually lands on a healthy
  mirror path.

## Blog Posts

- One file per post in `content/blog/`, flat. The filename becomes the URL slug:
  `euthyphro_dilemma.md` → `/blog/euthyphro-dilemma/`. **Zola slugifies the filename, not
  the title** — worth remembering when hunting for a built page.
- Front matter is TOML between `+++` lines:

```toml
+++
title = "The Euthyphro Dilemma: Why Morality Cannot Come From God"
date = 2026-04-28

[taxonomies]
tags = ["religion", "philosophy", "ethics"]
+++
```

- **Translations**: add `content/blog/<same-base-name>.he.md`. Copy `date` verbatim
  from the English file — it is a shared key, and a mismatch splits the pair.
  Translate the `title` value and the `tags` (see below). Do not add a `lang` key;
  zola infers it from the filename. The language switcher renders itself from
  `page.translations`, so never hand-write cross-links between a post and its
  translation.
- **Post slugs are shared between languages, deliberately.** `/en/blog/foo/` and
  `/he/blog/foo/` use the same English slug, because zola derives it from the
  filename and the filename is what pairs the two files. Do not "fix" this by
  renaming the Hebrew file or adding a `slug =` key — see
  `doc/DECISIONS.md` for why. Tag slugs *are* translated; posts are the exception.
- **Tags are translated, and are NOT a shared key.** A Hebrew post carries Hebrew
  tags (`דת`, not `religion`), so `/en/tags/` and `/he/tags/` are disjoint term
  sets. This is safe precisely because the pairing is by filename, not by tag.
- Links between posts use zola's `@/` syntax, resolved against the content root:
  `[text](@/blog/other_post.md)`.
- Every post exists in both English and Hebrew, and the build enforces it:
  `scripts/gen_stats.py` fails if any `.en.md` lacks its `.he.md` (or the
  reverse). An unpaired post would otherwise lose its language switcher
  silently, since `page.translations` just comes up empty.

## Coding Conventions

- JavaScript: camelCase, ES9+, eslint-clean
- Media plugins follow a consistent interface: `file`, `navTitle`, `title`, `subtitle`,
  `searchPlaceholder`, `searchFields`, `renderDetails`, `renderStats`
- Python: pylint- and mypy-clean; both run in CI over `scripts/`

## Style Sheets

- `sass/style.scss` is the site stylesheet, compiled by zola to `/style.css`.
- **Colours, radii, fonts and shadows come from `shared/shared-themes`** (the submodule).
  Nothing in `style.scss` hardcodes a colour — every value is a `var(--token)`. Setting
  `data-theme` on `<html>` switches between the six themes; azure is the default.
- `themes.css` is *copied* into `static/` by `build_site.py` and linked from `base.html`,
  not `@import`-ed from the SCSS: dart-sass leaves a plain `@import` of a `.css` file as a
  runtime import, and the relative path then resolves against `/style.css` and 404s.
- `static/shared.css` — common UI styles for the standalone app pages (`media_app.html`,
  `chess.html`, `calendar_app.html`, `board.html`). These link it directly.
- Prefer external stylesheets over inline `<style>` blocks or `style=` attributes.

## Git Conventions

- Branch: `master` (main)
- Commits are often auto-generated with no message
- GPG signing enabled
- Pull strategy: rebase

## Important Notes

- `_site/` is generated — never edit it. Edit `content/`, `templates/`, `sass/` or
  `static/` and rebuild.
- YAML data for the media tracker lives in a separate `../data/` repository and is copied
  in by `scripts/copy_data.py`, which also converts it to the `.json.gz` the frontend
  loads. **The frontend reads JSON, not YAML** — js-yaml took ~399ms on the 6.5MB youtube
  dataset against ~31ms for `JSON.parse`.
- **The `[extra.stats]` block in `content/blog/_index.{en,he}.md` is generated — do
  not hand-edit it.** `scripts/gen_stats.py` rewrites everything below the
  `# BEGIN generated stats` marker on every build; the hand-written section keys
  above it are preserved. It runs from `build_site.py` before zola, so the
  numbers are always current, and the output is committed so `zola serve` and
  any build that skips the step still show the right figures. `templates/blog.html`
  renders it as the archive sidebar. Computing this in Tera was the alternative
  and was rejected: Tera has no `group_by` over a derived key, so per-year counts
  would mean looping the section once per year.
- **The profile block on the About page is generated — do not hand-edit it.** It
  lives in `../data/yaml/profiles.yaml` and is rendered by `scripts/gen_profiles.py`
  into `content/about/_index.en.md` and `content/about/_index.he.md`. The YAML holds
  the whole shared block, not just links: `contact` (the gitter line), `intro`,
  `groups` (the links), and `extras` (the top-committers line, the GitHub stats
  badge, the view counter). Every one carries `_en` and `_he` text so `/he/about/`
  is a real Hebrew page. Only the region between the
  `<!-- BEGIN generated profiles -->` markers is replaced, so the hand-written prose
  above it survives. Edit the YAML, run the script, commit both
  repos. Like `copy_data.py` it is a manual step, not part of the build: CI has no
  `../data` checkout, and the generated content is committed.
- The same `profiles.yaml` also drives `README.md` in the **`../veltzer`** repository
  (the GitHub profile page), which has its own rsconstruct build — `rsconstruct build`
  there regenerates it from `README.md.in` plus the YAML. Neither repo writes into the
  other; the YAML is the only thing that crosses. Both pages render the same block
  in the same order, so the site's About page and the profile README stay identical.
  Only two things are page-local: this site's `title`/lead-in front matter, and the
  README's own `### Mark Veltzer's Github profile` heading plus its `main profile`
  self-link (`MAIN_PROFILE_URL` in that repo's `gen_readme.py`) — the site does not
  link to itself. Anything meant to appear on both belongs in the YAML.
- Custom domain is `veltzer.org` (see `CNAME`); `base_url` in `config.toml` matches it,
  and `veltzer.github.io` 301-redirects there. Keep every public URL (canonical tags,
  sitemap, RSS, `og:url`, `robots.txt`) on `veltzer.org` — pointing them at the
  redirecting domain splits SEO ranking off the real site.
- Google Calendar API key is public by design in `static/keys.js` — it is referrer- and
  API-restricted (see `doc/DECISIONS.md`). This is not a leak.
- **Google Analytics is wired but switched off**: `config.toml`'s
  `extra.google_analytics_id` is empty, so no `gtag` is emitted. Set it to a
  `G-XXXXXXXXXX` measurement ID to enable tracking site-wide. The ID is public by
  design — it identifies the property, it does not grant access to the data. Note GA4
  sets cookies and there is no consent banner; that trade-off is recorded in
  `doc/ANALYTICS.md` under "Consent".
- Site uses `.nojekyll` to bypass Jekyll processing on GitHub Pages.
- CI checks out submodules recursively; without that the build fails on missing tokens.

## Migration notes (traps that outlived MkDocs)

- **Do not add `mkdocs-static-i18n` or any MkDocs i18n plugin.** They are incompatible
  with the `blog` plugin, and the failure is silent: the build exits 0 while emitting
  *zero* post pages. This is why the site moved to zola. Full write-up in
  `doc/IMPROVEMENTS.md` under "Internationalization".
- Several 2010–2011 posts were imported from WordPress and the import ate `<` characters,
  truncating code listings. One (the grep post) has been reconstructed; if a code block in
  an old post looks impossible, suspect this rather than the author.
- The build cache can restore stale output. If a rebuild seems to ignore your change, run
  `rsconstruct clean all` before rebuilding.
