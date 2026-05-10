# CLAUDE.md - Project Guide

## Project Overview
Mark Veltzer's personal website hosted on GitHub Pages at veltzer.org (CNAME). Combines a blog, media consumption tracker, chess game viewer, and calendar integration.

## Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES9+)
- **Build**: rsconstruct (single binary, configured via `.rsconstruct/` and `config/*.lua`), MkDocs 1.6+ (Material theme) with the blog/tags/rss/glightbox plugins, npm
- **Linting**: jshint (JavaScript via `.jshintrc`), htmllint (`.htmllintrc`), yamllint (`.yamllint.yaml`), aspell (`.aspell.en.pws`, `.spellcheck-words`)
- **Data**: YAML for media content, PGN for chess games, Markdown for blog posts

## Directory Structure
- `blog/` - MkDocs `docs_dir`. Source for the entire site (Markdown posts, app HTML, media plugins, images)
- `blog/posts/YYYY/MM/*.md` - Blog posts. Front matter requires `date:` (ISO) and optional `tags:`
- `_site/` - Generated MkDocs output (gitignored, do not edit)
- `config/` - rsconstruct config: `project.lua`, `personal.lua`, plus `eslint.config.js`
- `scripts/` - Utility scripts (`build_docs.sh`, image fetchers, data importers, `serve.py` for local preview)
- `.rsconstruct/` - rsconstruct cache/state (gitignored content; the dir itself is checked in)
- `.github/workflows/build.yml` - CI: installs rsconstruct, runs `rsconstruct build`, uploads pages artifact, deploys
- `doc/` - Project notes / TODOs
- `mkdocs.yml` - MkDocs config (`site_dir: "_site"`, blog plugin paginates the home into `page/N`)

## Build Commands
- `rsconstruct build --verbose -j0` — Full build (this is what CI runs)
- `rsconstruct status` — Show build status
- `scripts/build_docs.sh` — Convenience wrapper for the docs build
- `scripts/serve.py` — Local preview server

## Coding Conventions
- JavaScript: camelCase, ES9+, jshint-clean
- Media plugins follow a consistent interface: `file`, `navTitle`, `title`, `subtitle`, `searchPlaceholder`, `searchFields`, `renderDetails`, `renderStats`

## Git Conventions
- Branch: `master` (main)
- Commits are often auto-generated with no message
- GPG signing enabled
- Pull strategy: rebase

## Important Notes
- `_site/` is the generated output — never edit it directly. Edit `blog/` (or templates/config) and rebuild.
- The blog plugin paginates: most recent posts appear on `index.html`; older ones on `page/2/`, `page/3/`, etc. A "missing" post is usually just on a later page — check `_site/page/*/index.html` and the archive before assuming a build failure.
- **Never date a blog post in the future.** The `date:` front-matter value must be today or earlier. The mkdocs blog plugin publishes future-dated posts immediately rather than holding them, which pushes genuinely-recent posts off page 1 and makes them look "missing."
- YAML data for the media tracker lives in a separate `../data/` repository and is copied in during build.
- Google Calendar API key is hardcoded in calendar code (known security TODO).
- Site uses `.nojekyll` to bypass Jekyll processing on GitHub Pages.
- Custom domain is `veltzer.org` (see `CNAME`); the canonical mkdocs `site_url` is still `veltzer.github.io`.
