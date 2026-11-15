# TOFIX

Findings from a full code review on 2026-11-15: every script, test, template,
stylesheet, frontend file, config file and document in the repo (the blog
posts themselves and the vendored libraries were not reviewed). Nothing here
is fixed yet. The previous list (2026-10-04, all resolved on 2026-10-28) is in
the git history of this file.

Each item is marked **[checked]** when the cited code was re-read or run after
the finding was made, and **[reported]** when it rests on one reading and was
not re-checked. "Latent" means the current data does not trigger it.

## 1. Bugs a visitor can hit

- **[checked] The YouTube tab ignores its default filter on first render.**
  `static/data-collection-app.js:312-317` seeds `activeFilters` from
  `defaultValue` ("so the very first render is filtered too"), but the first
  render at `:663` is `renderItems(allItems)`, unfiltered. The dropdown reads
  "Available" while the grid shows every item, the `missing` placeholders
  included, until the visitor touches a control. Render through
  `getFilteredItems()`.
- **[checked] Chess: a search with no match leaves a dead viewer that throws.**
  `content/chess/_index.en.md:326-327` skips `selectGame`/`render` when
  `filtered` is empty, so the buttons stay enabled and "next move" reads
  `games[filtered[currentGame]]` = `games[undefined]`. Disable the controls
  (or render an empty state) when nothing matches.
- **[checked] Chess: the arrow-key handler steals keys it should not.**
  `content/chess/_index.en.md:436-448` ignores modifiers (Alt+Left, the
  browser's Back, steps a move), does not exclude the focused game `<select>`
  (Up/Down change games instead of moving through its options), blocks
  Up/Down page scrolling everywhere, and keeps ArrowLeft = previous in Hebrew
  although the buttons swap their arrows for RTL.
- **[checked] The movies tab shows "with" names although `showPeople` is
  off.** `templates/data_collection.html:149` sets `showPeople: false`;
  `static/plugin-movies.js` honours it in the stats (`:71`, `:83`) but not in
  the `with_others` filter (`:21`), the "With" toggle (`:29`) or the card
  line (`:49`). 8 of the 65 entries in `static/data/video_features.json.gz`
  carry names. Decide whether the names should be published at all: if not,
  `copy_data.py` should drop `with` from the JSON, since hiding it in the
  plugin still ships it.
- **[checked] Rating dropdowns and the books rating chart sort as text.**
  `static/data-collection-app.js:374` (`sorted.sort()`) and
  `static/data-collection-utils.js:70` (`keys.sort()`) put `10` before `2`.
  Sort numerically when every key is a number.
- **[checked] Focusing the blog search box downloads the word vectors.**
  `static/blog-search.js:297` runs `ready()` on focus, and with
  `search_mode = "semantic"` (`rssite.toml:130`) that fetches ~6 MB (English)
  or ~11 MB (Hebrew) before a key is pressed; tabbing past the box or tapping
  it on a phone is enough. The file header and `CLAUDE.md` both say the
  vectors load "only when the semantic mode is used". Load them on the first
  query instead.
- **[reported] `?data=` is looked up on a plain object.**
  `static/data-collection-app.js:585-598`: `?data=constructor` resolves to an
  inherited property and renders a page titled "undefined"; an unknown key
  returns before the tabs are drawn, leaving an error box with no way out.
  Use `Object.hasOwn` and draw the navigation before bailing.
- **[reported] A rating of 0 renders as "?"**
  (`static/data-collection-app.js:741`, `item.rating || '?'`). Latent.
- **[reported] Typing in the YouTube search re-sorts ~30,000 items per
  keystroke** (`static/data-collection-app.js:818-823`): the list is already
  sorted and filtering keeps the order; there is no debounce. Every tab or
  stats switch also refetches and reparses the dataset (`:615`).

## 2. Build configuration

- **[checked] Share cards are drawn for the two blog index files.**
  `[processor.generator.generic.post_cards]` in `rsconstruct.toml` uses
  `src_exclude_files`, where every other processor uses `src_exclude_paths`;
  the exclusion does nothing, the step has 862 products for 860 posts, and
  `_site/images/og/_index.en.jpg` / `_index.he.jpg` are published.
- **[checked] The pytest `dep_inputs` list is incomplete.** Its comment says
  "Everything the tests import or read", but `tests/test_logo.py` imports
  `scripts/make_logo.py` and reads `templates/base.html` and
  `static/favicon.svg`; none is listed, so editing the logo does not re-run
  the drift test on a warm cache.
- **[checked] No JSON is linted, though two comments say it is.**
  `rsconstruct.toml:195` and `.biome.jsonc:4` both say "ijsonlint covers
  JSON"; no such processor is configured. Unlinted: `static/data/vectors/*.json`,
  `data/rotten_tomatoes_manual.json`, `shelve/*.json`, `.oxlintrc.json`.
- **[checked] `checker.itidy` lints nothing.** `src_dirs = ["static"]` holds
  no `.html` (`rsconstruct status` shows 0 files), so "tidy (HTML)" in
  `CLAUDE.md` describes a check that never runs. Either point it at the
  rendered `_site/` pages, which would have caught the nested `<main>` below,
  or remove it.
- **[reported] `scripts/build_site.py` is not an input of the `companies`
  step**, unlike `check_images` and `export_posts_for_ai`, which list their
  own script. Whether rsconstruct tracks the command file by itself was not
  checked.
- **[checked] Four tracked files match `.gitignore`**:
  `static/vendor/cm-chessboard/assets/**/*.css.map` (rule `*.map`). Untrack
  them; nothing serves a source map for vendored CSS.
- **[checked] `.oxlintrc.json:7` names a schema under `./node_modules/`**,
  which does not exist (the site has no Node packages).
- **[reported] `rumdl.prose` does not lint `TOFIX.md`**, and its
  `src_exclude_dirs = ["content"]` is a no-op since `src_dirs` is `doc`.
- **[reported] `.luacheckrc` and `config/project.lua` have no consumer in
  this repo**: no luacheck processor, `[analyzer.tera]` is empty, nothing
  calls `load_lua`. `project.lua` may be read by fleet tooling; `.luacheckrc`
  describes a renderer the repo does not run.
- **[reported] `scripts/build_collection_css.sh` runs `npx --yes
  tailwindcss@3`**, a floating version fetched at run time, outside the
  build; `CLAUDE.md` says the site has no Node packages and names neither the
  script nor `config/tailwind.collection.*`.

## 3. Python scripts

### Image fetching

- **[checked] A failed normalise aborts the run and leaves a bad image that
  every later run skips.** `image_standard.normalise()` runs ImageMagick with
  `check=True`; the callers catch only `(HTTPError, URLError, OSError)`
  (`fetch_audible_images.py:94`, `fetch_audiocourse_images.py:59,151,169`,
  `fetch_book_covers.py:114`, `poster_utils.py:165`), and `image_picker.py`
  catches nothing. A 200 response carrying an HTML error page stays at
  `dest`, the next run sees the file and skips it, and `check_images.py`
  checks existence only, so it ships. Download to a temporary name, verify it
  opens as an image, then rename.
- **[reported] A timeout mid-download leaves a zero-byte file** for the same
  reason: `fetch_audible_images.py:35` and `fetch_audiocourse_images.py:45`
  open `dest` before reading the response, and `poster_utils.py:110` uses
  `urlretrieve` straight to `dest`.
- **[checked] `image_standard.py:64` strips EXIF without `-auto-orient`.**
  A phone photo with Orientation=6 comes out sideways for good (the reviewer
  reproduced it with the same ImageMagick command). `capture_output=True`
  also hides ImageMagick's stderr when it fails.
- **[checked] `poster_utils.py` has no timeouts and sends the OMDb key over
  plain HTTP** (`:19` `http://www.omdbapi.com/...apikey=`, `:68`, `:93`,
  `:110`). `JSONDecodeError` is not caught at `:69` / `:94`.
- **[reported] `fetch_book_covers.py:50` matches `og:image` with a regex**
  that needs one exact attribute order, the pattern
  `fetch_audiocourse_images.py:62` says was replaced elsewhere for failing
  silently; the matched URL is not entity-unescaped.
- **[reported] `organizations_fetch_maps.py:333` caches a tile response
  without checking it is an image**, so an error body is cached for good.

### YAML maintenance

- **[checked] Every ruamel script reformats the whole file on save.** The six
  that use `YAML(typ="rt")` (`podcasts_add_chapters.py`,
  `podcasts_add_podcast.py`, `podcasts_backfill_rss.py`,
  `podcasts_backfill_rss_data.py`, `podcasts_fill_chapter_names.py`,
  `youtube_add_names.py`) set neither `indent` nor `width`. A load and dump
  of `data/yaml/podcasts.yaml` with no edit changes 648 diff lines (measured
  in memory by the reviewer), burying the one real change.
- **[checked] `podcasts_backfill_rss_data.py:104-113` drops chapter keys.**
  `_rebuild_chapter_from_name` copies six named keys and clears the rest, so
  any other key on a legacy chapter is lost.
- **[reported] The same script matches chapters to feed episodes by
  position**, not by title as its docstring and `doc/SCRIPTS.md` say
  (`:162-167`); a feed that gains or loses an episode puts metadata on the
  wrong chapters, and a chapter that has a guid is never re-matched.
  `podcasts_fill_chapter_names.py:346` reads the numeric title as a 0-based
  index, which disagrees with it.
- **[reported] The podcast scripts save once at the end**, so one network
  error or one odd duration (`duration_to_seconds` raises on `3600.0`) loses
  the whole run; `podcasts_backfill_rss.py:393` writes the first search hit
  as the feed without comparing names.
- **[checked] `duration_to_seconds`, `parse_rss_episodes` and the RSS field
  helpers are copied into three podcast scripts**; `download()` is copied
  into three fetchers. Move them to a shared module.
- **[checked] `organizations_geocode.py:139` consults the cache before
  `OVERRIDES`.** The unresolved report says "add an OVERRIDES entry", but a
  cached `null` (`shelve/nominatim_geocode.json` has one: "Airport City, Lod,
  Israel") is returned and the override never runs.
- **[reported] `great_courses_fetch_ids.py:269` writes an `<h1>` title into
  a double-quoted YAML scalar** with no `html.unescape` and no escaping of
  `"` or `\`; `show_image` (`:139`) leaks its temporary files.
- **[reported] `youtube_add_names.py:259` can record a consent page's title
  as a video name**, and strips "- YouTube" anywhere in a title.
- **[reported] Latent parsing gaps**:
  `audio_courses_check_lecturers.py:55` reads `lecturers` only from the same
  line (a block-style list gives a false mismatch) and `:94` matches
  surnames by substring; `organizations_pick_geo.py:347` writes nothing for
  an item without `sources` while counting it as decided;
  `import_books.py:98` sorts dates against a `""` default and raises if a
  date is ever unquoted; several scripts scan YAML line by line where
  `yaml.safe_load` is already used elsewhere.

### Other scripts

- **[checked] `manage_api_key.py rotate` never updates `static/keys.js`.**
  The key is committed there verbatim, so following the prompt at `:192`
  ("Rebuild and deploy the site now") redeploys the old key and the script
  then deletes it. `create_key` (`:116`) also overwrites the old value in
  pass before the old key is deleted, so an interrupted rotation orphans it.
- **[checked] `make_word_vectors.py:120` divides by zero on an all-zero
  vector**, producing NaN in the scale file; no test covers the case.
- **[checked] `serve.py:60` is a single-threaded `TCPServer`**, which one
  idle browser connection can stall, and it serves Python's own 404 page
  rather than the site's `404.html` although the docstring calls it the
  closest approximation to Pages. `ThreadingHTTPServer` fixes the first.
- **[checked] `build_he_dict.sh` has no cleanup trap**; `build_en_dict.sh:41`
  has one. A failed build leaves a temporary file in `out/aspell/`.
- **[reported] `import_teaching.py:162-235` scopes CSS by splitting on
  commas**, so `:is(a,b) .x`, `html[data-theme=dark]` and
  `:root[data-theme=dark]` come out wrong. Latent.
- **[reported] `check_redirects.py`** hardcodes `veltzer.org` beside a
  `base_url` it reads from `rssite.toml` (`:34-38`, `:69`), and the second
  sitemap fetch (`:79`) does not catch `URLError`.
- **[reported] `spellcheck_en.sh:38`** filters non-Latin words with
  `grep -P`, which removes nothing under a C locale.
- **[reported] `check_wikidata_ids.py:30`** uses cwd-relative paths where its
  siblings use `REPO_ROOT`.

### Tests

- **[reported] `tests/test_logo.py` checks less than its docstring says**:
  only `viewBox`, `rx` and `d=`, so a changed stroke passes, and its regex
  has no DOTALL.
- **[reported] The `main()` paths are untested** in `csv_to_yaml.py`
  (including the METADATA_NOT_FOUND handling the test file names as the
  risk), `import_books.py` and `import_companies.py`.

## 4. Templates, HTML and accessibility

- **[checked] `<main>` is nested in `<main>` on the collection pages**:
  `templates/base.html:272` plus `templates/data_collection.html`
  (`_site/en/media/index.html:119` and `:227`).
- **[checked] `templates/404.html` is English only and describes URLs the
  site decided not to rescue**: "the blog and the applications are now under
  a language prefix" contradicts the no-legacy-redirects decision, and the
  heading and labels bypass `trans()`.
- **[checked] Arrows are not mirrored in Hebrew**: `&larr;` / `&rarr;` are
  hardcoded in `blog.html:70,72`, `taxonomy_single.html:15,17`,
  `page.html:95,96` and `index.html:27`, so "newer" points toward "older" on
  `/he/`. The chess page already swaps its arrows.
- **[checked] `sameAs` carries an image URL**: `static/identity.toml:19`,
  `https://projecteuler.net/profile/veltzer.png`, comes from
  `profiles.yaml` and reaches the Person JSON-LD on every page. Fix it in
  the YAML or filter it in `gen_profiles.py`.
- **[reported] The Person and BlogPosting JSON-LD blocks are not linked**
  (`templates/base.html:106-133`: no `@id`, the post's `author` is a second
  bare Person) and `BlogPosting` has no `image` although a card exists.
- **[reported] Year archive pages all inherit the blog's meta description**
  (`templates/archive.html` has no `description` block).
- **[reported] JavaScript URLs carry no `?v=`** while CSS and icons do
  (`base.html:135-159` against `blog.html:9` and the dynamically inserted
  plugins), so a deploy can pair new HTML with a cached old script.
- **[reported] Accessibility**: `aria-label` on the sort and filter buttons
  hides their visible state text; tabs and pager are rebuilt with
  `innerHTML` so focus drops to `<body>` after every click
  (`data-collection-app.js:524,765,770`); `#status-message`, the chess
  `#status` and `#calendar-error` are not live regions; card titles are
  `<h5>` under an `<h1>`; several `<nav>` have no label and the current item
  no `aria-current`; there is no skip link; `.blog-search-status:empty
  { display: none }` (`sass/style.scss:412`) hides a `role="status"` region
  until the moment it is filled.
- **[reported] `hreflang` on `<option>` is invalid** (`base.html:254`), and
  the language select navigates on `change`.
- **[reported] `<style>` blocks sit in the body** of
  `data_collection.html` and `root.html`, against the external-stylesheet
  rule in `CLAUDE.md`.
- **[reported] Hardcoded units and labels**: `'h'` in
  `plugin-youtube.js:120`, `'51+'` in `plugin-podcasts.js:40`, `' MB'` in
  the chess page; `sass/style.scss:487-496` uses physical `text-align`.

## 5. Dead code and duplication

- **[reported] `plugin-concerts.js` and `plugin-museums.js` are registered
  but appear on no page** and their data files are not built, yet about 72
  `app_concerts_*` / `app_museums_*` strings are inlined into every
  collection page (all 442 `app_` keys are, on every such page).
- **[checked] `static/keys.js:1` has an `eslint-disable` directive**; the
  repo uses oxlint. `bg-info` and `bg-warning` in `COLOR_CLASS_MAP` and
  `CONTENT_NS` in `podcasts_backfill_rss_data.py:20` are unused
  **[reported]**.
- **[reported] Plugin boilerplate belongs in `data-collection-utils.js`**:
  the count tally (40+ copies), year bucketing, device distribution, the
  `has_review` field (7 plugins), the IMDb / Wikidata / Rotten Tomatoes link
  block (movies and series), and the `<li data-toggle>` builder.
- **[reported] `.mypy_cache/` is a leftover directory** (ignored, mypy is
  gone); `youtube_add_names.py:339` still says `pip install`.

## 6. Stale documentation

All **[checked]** unless marked.

- `CLAUDE.md:234` and `doc/javascript_toolkits.md:56-58`: `themes.css` is
  published by rssite's `[[publish]]`, not copied by `build_site.py
  shared-themes` (that subcommand is gone); the second file also says
  "compiled by zola".
- `doc/DECISIONS.md:365,377`: `i18n/tags.toml` and `out/build_info.toml` do
  not exist.
- Zola named as the current generator: `doc/BACKEND_SERVICES.md:109,125`,
  `doc/MKDOCS_VS_ALTERNATIVES.md:6`, `doc/IMAGES.md:3`, `doc/problems.txt`,
  `scripts/import_teaching.py:4,9`, and **[reported]** `doc/SEO.md:242`,
  `doc/DECISIONS.md:159,277,293`.
- Counts that have drifted: `doc/TRANSLATION.md:10` (436 pages; there are
  443), `doc/javascript_toolkits.md:18` (nine plugins; there are 11),
  **[reported]** `doc/BACKEND_SERVICES.md` (~165 posts per language; there
  are 431) and `doc/DECISIONS.md` (88 companies on 24 points; there are 45
  map images).
- `doc/IMPROVEMENTS.md:402,536` name `tests/test_template_determinism.py`,
  which no longer exists.
- `doc/ANALYTICS.md` **[reported]**: the coverage table still lists the
  `static/*.html` redirect stubs removed on 2026-10-28.
- The `companies` step is described as writing one file; it writes seven
  (`doc/SCRIPTS.md`, `doc/PLUGIN_GUIDE.md`; the `build_site.py` docstring
  omits `certifiers.json.gz`) **[reported]**.
- `doc/PLUGIN_GUIDE.md` **[reported]**: the plugin table omits providers,
  consulting, publishers, education, certifiers and certifications; it names
  two host pages of four; `prepareItem` and the `sortFields` / `filters`
  overrides are undocumented; `type` is listed as required but defaulted.
- `doc/SCRIPTS.md` has no entry for `videos_fetch_wikidata.py`,
  `check_wikidata_ids.py`, `import_certifications.py` or
  `build_collection_css.sh`, and does not say the poster fetchers read the
  built `static/data/*.json.gz`, so a new video is skipped until
  `copy_data.py` has run **[reported]**.
- `CLAUDE.md` **[reported]**: the scripts list omits `check_images.py`,
  `check_profile_links.py`, `make_og_images.py`, `import_certifications.py`
  and `manage_api_key.py`; `tests/` is more than "the data import scripts";
  "the Python linters come from rsconstruct's tool registry" while ruff,
  pyrefly and pytest are in the `pyproject.toml` dev group.
- Script comments: `make_og_images.py:18` ("the build needs neither Pillow
  nor the fonts"; the post cards import it), `gen_profiles.py:24` (names the
  retired `gen_stats.py`), and **[reported]** `make_logo.py:18`,
  `export_posts_for_ai.py:32`, `image_standard.py:25`.

## Checked and found clean

No `python3` shebangs; no version pins in `pyproject.toml`; every third-party
import is declared and nothing declared is unused; `yaml.safe_load`
throughout and no shell-built commands; no secrets in the scripts; no XSS
path from `?q=`, `?mode=` or the data into `innerHTML`; `i18n/en.toml` and
`i18n/he.toml` have the same keys; no duplicate HTML ids in `_site/`; no
hardcoded colours in `sass/style.scss` beyond the chessboard exception;
`rssite check` passes on all 2166 files.
