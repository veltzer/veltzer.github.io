# CLAUDE.md - Project Guide

## Project Overview
Mark Veltzer's personal website hosted on GitHub Pages (veltzer.github.io). Combines a technical blog, media consumption tracker, chess game viewer, and calendar integration.

## Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES9+), Bootstrap 5.3.3, Tailwind CSS (some pages)
- **Build**: Python 3 (pydmt, pymakehelper), MkDocs 1.6.1 (Material theme), Vite (JS bundling), npm
- **Linting/Testing**: pylint, pytest, mypy, ruff (Python); jshint (JavaScript); jsonschema (JSON)
- **Data**: YAML files for media content, PGN for chess games, Markdown for blog posts

## Directory Structure
- `blog/` - Blog source (Markdown posts)
- `config/` - Python config (project.py, personal.py, shared.py, version.py, calendar.py)
- `docs/` - Generated site output (do not edit manually — rebuilt by `scripts/build_docs.sh`)
- `docs/data/` - YAML data files (podcasts, audible, museums, etc.)
- `scripts/` - Build and utility scripts
- `templates/` - Mako templates for pydmt
- `pkg/` - npm package definitions
- `out/` - Build output stamps
- `doc/` - Documentation and TODOs

## Build Commands
- `make` — Run all enabled checks
- `make clean` — Remove `out/` directory
- `make clean_hard` — Git clean (removes all untracked files)
- `scripts/build_docs.sh` — Full site build: MkDocs build → pydmt build → copy YAML data and PGN files from `../data/`
- `scripts/vite.sh` — Bundle npm packages with Vite

## Key Makefile Parameters
- `DO_MKDBG` — Enable debug output
- `DO_ALLDEP` — Enable all dependencies
- `DO_JS_CHECK` — Enable JavaScript checks (jshint)
- `DO_JS_PACKAGE` — Enable JavaScript packaging

## Coding Conventions
- Python: snake_case, type hints, checked by pylint/mypy/ruff
- JavaScript: camelCase, ES9+, checked by jshint (`.jshintrc`)
- Media plugins follow a consistent interface: `file`, `navTitle`, `title`, `subtitle`, `searchPlaceholder`, `searchFields`, `renderDetails`, `renderStats`

## Git Conventions
- Branch: `master` (main branch)
- Commits are often auto-generated with no message
- GPG signing enabled
- Pull strategy: rebase

## Important Notes
- `docs/` is a generated directory — changes go in `blog/`, `templates/`, or source files, then rebuild
- YAML data for the media tracker lives in a separate `../data/` repository and is copied in during build
- Google Calendar API key is hardcoded in `config/calendar.py` (known security TODO)
- Site uses `.nojekyll` to bypass Jekyll processing on GitHub Pages
- Version is tracked in `config/version.py` (currently 0.1.19)
