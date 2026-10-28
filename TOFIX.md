# TOFIX

Findings from a code scan on 2026-10-04. All resolved on 2026-10-28 (two had
already been fixed in passing):

- `CLAUDE.md` names the linters `rsconstruct.toml` actually runs (oxlint,
  tidy, biome, pyrefly, ...), and its CI paragraph describes the current
  `tool install machine` / `tool install project` steps and the lock file,
  with no npm, eslint, htmlhint, stylelint, svglint or mypy left in it.
- The four renamed scripts print their own names in their usage lines.
- `pyproject.toml` calls the repo the personal website and no longer
  declares `types-beautifulsoup4`; `scripts/books_fetch_ids.py` imports
  `bs4` without a `type: ignore` (pyrefly is clean on it).
- `.rumdl.content.toml`'s header says how it differs from the fleet file
  (MD041 off, MD053 on) and why MD057 and MD014 are off for posts.
- `doc/DONE.md` already marks itself as MkDocs-era history; the
  `build_docs.py` entry in `doc/IMPROVEMENTS.md` now carries a dated note.
- The `rsconstruct.toml` header and `mypy_path` items had been fixed before.
