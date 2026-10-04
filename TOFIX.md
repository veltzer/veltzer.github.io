# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `rsconstruct.toml:1` - header comment says stylelint and postcss-scss come from `package.json` / `package-lock.json` installed by `npm ci`, but neither file exists and stylelint was removed; delete the comment.
- `CLAUDE.md:16` - the Linting list still names eslint (`.eslint.config.js`), htmlhint and stylelint (`.stylelintrc.json`), none of which exist or are configured in `rsconstruct.toml` (the actual JS/CSS linters are oxlint and biome); update the list to match `rsconstruct.toml`.
- `CLAUDE.md:137` - the CI section describes Node packages in `package.json` pinned by `package-lock.json` and installed into `node_modules/`; there is no `package.json` in the repo, so this paragraph (lines 137-146) is stale and should be rewritten without the npm part. Same for "npm" at `CLAUDE.md:14` and "eslint-clean" at `CLAUDE.md:206`.
- `CLAUDE.md:56` - says `data/logos/` is linted by "xmllint and svglint"; there is no svglint processor in `rsconstruct.toml` (only `[processor.xmllint]`); drop svglint.
- `scripts/audio_courses_check_ids.py:8` - usage line names `scripts/check_audio_courses_ids.py`, which does not exist (the script was renamed); fix the usage text. Same stale names in `scripts/audio_courses_check_lecturers.py:8`, `scripts/great_courses_check_unique.py:8` and `scripts/great_courses_fetch_ids.py:14`.

## Low

- `pyproject.toml:34` - `mypy_path = "src:python:scripts"` lists `src` and `python`, which do not exist in this repo; reduce it to `scripts`.
- `pyproject.toml:30` - comment calls this a "Demo/teaching repo"; it is the personal website - correct the comment.
- `scripts/books_fetch_ids.py:40` - `import bs4  # type: ignore` is unused (`mypy --warn-unused-ignores` reports `unused-ignore`, bs4 4.15 ships its own types); remove the suppression, and drop the obsolete `types-beautifulsoup4` stub package at `pyproject.toml:23`.
- `.rumdl.zola.toml:1` - header claims the file is the fleet `.rumdl.toml` plus MD041 off, but it does not disable MD053 (the fleet file does), and it carries the Marp/teaching-slides MD057/MD014 rationale that does not apply to this site's content; make the comment match the rule list.
- `doc/DONE.md:37` - refers to `scripts/copy_data.sh`, now `scripts/copy_data.py`; similarly `doc/IMPROVEMENTS.md:412` cites a nonexistent `scripts/build_docs.py`; update or mark as historical.
