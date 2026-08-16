# Suggested Improvements

## Media Collection UX

- Add a clear title/subtitle explaining what the media collection contains.
- Show thumbnails or cards instead of only a plain list.
- Include richer metadata like type, date, tags, and file size.
- Add search plus filters for category/date to make browsing easier.
- Improve loading/error state for the visits counter to feel more polished.
- If the content is personal data, add a short note on what is public vs private to build trust.
- Add more structure and discoverability to make it easier to use and contribute to.

## Overall Stats Page

- Create an overall stats page across all topics: total listening time, average rating by lecturer, most-used device, etc.
- Currently there is a statistics page per topic but not an aggregated one.

## YAML Data Structural Issues

### High Severity

- ~~**Audible: Numeric fields stored as strings.** — DONE.~~
  Created `scripts/import_audible.py` that converts types and drops empty optional fields.
  Frontend updated to use numeric values directly.

- ~~**YouTube: 2,964 broken records (10.6% of 27,997).** — DONE.~~
  `csv_to_yaml.py` now tags these with `status: "missing"` and the frontend filters them out.

### Medium Severity

- ~~**Museums: Mixed date format for date-only entries.** — DONE.~~
  Renamed `date_dmy` to `date_ymd` with `YYYY-MM-DD` format across schemas and data.

### Low Severity

- ~~**Audible: `series_title` / `series_sequence` are 95% empty.** — DONE.~~
  `import_audible.py` now omits these when empty.

- **NOT A PROBLEM: cross-file naming inconsistency (`name` vs `title`).**
  Some datasets use `name` (podcasts, museums, video_features, video_series,
  audio_courses), others use `title` (audible, youtube). The frontend already handles it:
  `media-app.js` copies `title` onto `name` at load time when `name` is absent, so
  everything downstream sees one field. Verified across all seven datasets — 29,346 items,
  every one resolves to a label, no gaps.

  Not worth a coordinated data + plugin migration for a difference nothing can observe.
  The `url` / `webpage_url` / `cover_url` variation is likewise handled per-plugin.

- ~~**YouTube: `upload_date` uses `YYYYMMDD` format.** — DONE.~~
  `csv_to_yaml.py` now converts to `YYYY-MM-DD` and the frontend `formatDate` was simplified.

## SEO / Domain

- ~~**Canonical URLs point at a domain that redirects away.** — DONE.~~
  `mkdocs.yml` had `site_url: "https://veltzer.github.io"` while `CNAME` serves the site
  at `veltzer.org`, so every page declared its canonical to be a URL that immediately
  301s back — splitting ranking off the real domain. Set `site_url` to
  `https://veltzer.org`, which fixed the canonical tags, all 105 sitemap `<loc>` entries,
  and the RSS channel/`<guid>`/item links in one change. Also updated the hardcoded RSS
  links (`mkdocs.yml` social, `blog/index.md`), the `Sitemap:` line in `blog/robots.txt`,
  and the `og:url` in all 7 standalone HTML pages. Verified: zero `veltzer.github.io`
  references remain anywhere in the built site, and the sitemap still has 105 URLs.

  Two `og:url` values were also pointing at paths that do not exist — `media_app.html`
  claimed `/media.html` and `calendar_app.html` claimed `/calendar.html`. The build
  produces `media/` and `calendar/` directories, not those `.html` files. Both now point
  at themselves.

  **`veltzer.github.io` still works and is unaffected by this change.** The redirect is
  enforced by GitHub Pages infrastructure from the repo's Pages `cname` setting
  (confirmed via the API: `cname: veltzer.org`, `https_enforced: true`), not by anything
  in the built output — note `_site/` contains no `CNAME` file at all and never has.
  `site_url` only controls URL strings inside the generated HTML/XML. Verified after the
  change: `https://veltzer.github.io/<any-path>` still returns 301 preserving the path,
  and following it lands on a 200 at `veltzer.org`.

  Note for anyone re-treading this: search engines need to re-crawl to move ranking
  signals onto `veltzer.org`, and RSS readers keyed on the old `<guid>` values may show
  existing posts once more as new. That one-time churn is the cost of the correction.

- ~~**`blog/sitemap.xml` is dead weight.** — DONE.~~
  Was a hand-written 9-URL sitemap, 2 of whose URLs (`/media.html`, `/calendar.html`)
  did not exist in the build. It never broke anything — MkDocs overwrites it — but it was
  a stale hand-maintained copy with no effect. Deleted; the generated 105-URL sitemap is
  unaffected (verified post-deletion).

## Security

- ~~**Restrict Google Calendar API key.** — DONE (already in place).~~
  `blog/keys.js` ships the API key to every visitor, which is by design for a browser
  key (see `doc/DECISIONS.md`). The referrer restriction this item asked for is already
  configured. Verified empirically against the live key: a request with no referrer, and
  one from an unrelated domain, both return
  `403 PERMISSION_DENIED "Requests from referer ... are blocked"`, while
  `https://veltzer.org/` and `https://veltzer.github.io/` both succeed. Nothing to do.

## Python Code Quality

- ~~**Deduplicate image picker GUI in `fetch_audiocourse_images.py`.** — DONE.~~
  Five duplicated functions removed (`_build_browser_ui`, `show_image_browser`,
  `download_candidates`, `get_cache_dir_for`, `fetch_image_urls`); `handle_image_search`
  now calls `image_picker.pick_image()`. The file went from 393 to ~200 lines. The copy
  was also strictly worse than the shared version: it lacked the window-close and SIGINT
  handlers, so quitting the picker left it hanging.

- ~~**Replace fragile YAML parsing in `check_images.py`.** — DONE.~~
  Now uses `yaml.safe_load`. Output is byte-identical to the previous version on the real
  data (diffed against a captured baseline). The same hand-rolled pattern in
  `fetch_audiocourse_images.load_entries` was replaced too, and there it was **actively
  losing data**: it returned 51 of 52 courses, silently dropping *"Foundations of Western
  Civilization II: A History of the Modern Western World"* because the colon in the title
  broke the split. `poster_utils.load_imdb_ids` was likewise line-scanning for `imdb_id:`.

- ~~**Use BeautifulSoup instead of regex for HTML scraping.** — DONE.~~
  The regex required exactly one space and `property` before `content`. Verified against
  the new parser: reversed attribute order, single-quoted attributes and extra attributes
  all returned `None` under the regex and parse correctly now; identical on the canonical
  case and still `None` when the tag is absent.

- ~~**Standardize logging across scripts.** — PARTIALLY DONE.~~
  `fetch_audiocourse_images.py` converted to `logging` with a bare `%(message)s` format
  (it is an interactive tool read by a person, so level/timestamp prefixes would be
  noise). `check_images.py` already used logging. The remaining `print`-based scripts
  (`manage_api_key.py`, `poster_utils.py`, `image_picker.py`, `serve.py`, and the small
  `copy_data.py` / `csv_to_yaml.py` / `import_audible.py` summaries) were left alone —
  they are all short interactive tools where `print` is fine, and churning them would be
  change for its own sake.

- ~~**Use script-relative paths instead of hardcoded relative paths.** — DONE.~~
  `check_images.py`, `fetch_audiocourse_images.py` and the five `fetch_*` scripts now
  derive their paths from `Path(__file__).resolve().parent.parent`. Verified
  `check_images.py` produces identical output when run from `/tmp`, which the old version
  could not do at all.

  This also caught a live breakage: `fetch_movie_posters.py` and `fetch_series_posters.py`
  still pointed at `blog/data/*.yaml.gz`, which stopped existing when the build switched
  to shipping `.json.gz`. Both now point at the JSON, and `poster_utils.load_imdb_ids`
  handles either format — confirmed extracting 65 and 70 IMDB ids from the real files.

- ~~**Split `fetch_audiocourse_images.py` into smaller pieces.** — DONE (by deletion).~~
  The file is now ~200 lines rather than 387, because the DuckDuckGo search and picker
  half moved to `image_picker.py` where it already existed. What remains is one function
  per source (`fetch_gc_image`, `fetch_audible_image`, `handle_image_search`), which was
  the point of the proposed split — no strategy pattern needed at this size.

## JavaScript

- ~~**Two media plugins are registered under keys they never use.** — DONE.~~
  `media-app.js` registered `'audio_courses'` and `'series'` while the plugins register
  themselves as `'audio'` and `'videos'`. Renamed the two registry keys to match the
  plugins, since `getDataSources()` returns `window.mediaPlugins` — the plugin-side names
  are what drive live `?data=...` URLs, so changing those instead would have broken
  existing links. All seven keys now match (verified programmatically). Added a comment
  above the registry recording the constraint.

- ~~**`loadAllPlugins().then(loadData)` has no `.catch()`.** — DONE.~~
  `loadAllPlugins` uses `Promise.all`, so one failing plugin rejected the whole chain,
  `loadData` never ran, and the page stayed blank with only an uncaught rejection in the
  console. Added a `.catch()` that logs and renders the same red error banner `loadData`
  uses, so the failure is now visible to the user.

- ~~**Convert YAML data to JSON at build time for performance.** — DONE.~~
  The youtube dataset is 6.5MB uncompressed / 29,034 records, and js-yaml parsed it on the
  main thread on every load. Measured on the real data before changing anything:
  **js-yaml 399ms vs JSON.parse 31ms (12.9x)**; re-measured in-browser after the change,
  JSON.parse is 28ms. `scripts/copy_data.py` now converts every YAML file to JSON
  (`convert_yaml_to_json`) before gzipping, and the frontend uses `JSON.parse`. YAML
  remains the build's intermediate form; the `.json.gz` files are what ship.

  Side benefits: gzipped JSON is slightly *smaller* than gzipped YAML for every dataset
  (youtube 1.81MB -> 1.72MB), and the js-yaml CDN `<script>` is gone from `media.md` and
  `media_app.html`, dropping a third-party dependency from the critical path.

  Verified: all 7 datasets round-trip byte-identical YAML->JSON (29,034 youtube records
  included), and the app was driven in a real browser — cards render, all 7 sources load,
  the stats view works, and no console errors beyond a pre-existing unrelated 410 from the
  visitor-counter API.

- ~~**`plugin-museums.js` reads a field name nothing else uses.** — DONE.~~
  `getYear` branched on `item.date_dmy`, a leftover from the project-wide `date_dmy` ->
  `date_ymd` rename recorded under Medium Severity above. The data has 14 `date_ymd`
  records and zero `date_dmy`. Two bugs in one line: the field name, and the year index —
  `date_ymd` is `YYYY-MM-DD`, so the year is `parts[0]`, not the `parts[2]` the old
  `date_dmy` code used. Fixed both. The museums year chart counted 9 of 23 visits before;
  it now counts all 23 (verified against the real data).

- ~~**Dead `formatDate` in `media-app.js`.** — DONE.~~
  A private `formatDate` that was never called — the plugins all use `mediaFormatDate`
  from `media-utils.js` instead. Removed.

- ~~**`calendar_list_view.html` double-fires `init()`.** — DONE.~~
  The `visibilitychange` handler called `init()` on every return to visibility, on top of
  the interval already running — so briefly switching tabs fired an extra quota-limited
  Calendar API call. Now tracks `lastFetch` and only refetches on return if a full
  `REFRESH_MS` has actually elapsed.

- ~~**`calendar_list_view.html:126-135` has a `catch` that only rethrows.** — DONE.~~
  Dead code — the `catch` only rethrew unchanged. Removed the wrapper; the `!response.ok`
  check and the caller's own error handling are unaffected.

- **NOT A PROBLEM: absent `rating` on audio courses is meaningful, not missing data.**
  This item warned that plugins assume `item.rating` always exists and would produce
  `NaN` in stats. Investigated: neither half holds.

  The 11 of 52 audio courses without a `rating` are **exactly** the 11 that have a
  `progress` field (4/24, 3/36, 9/24, ...) — i.e. the ones not yet finished. All 41 rated
  courses have no `progress` field. The correlation is perfect across all 52. Ratings are
  assigned on completion, so an absent rating means "not yet rated", not lost data.

  The frontend already handles it: `media-app.js` renders `item.rating || '?'`, so an
  unfinished course shows "? / 10". And no plugin computes an average anywhere — no
  `toFixed`, no `reduce`, no division by `items.length` — so the `NaN` this item warns
  about cannot occur. Worth revisiting only if averages are ever added, at which point
  unrated items must be excluded from the denominator rather than counted as zero.

  Same for `date_utcz`: the museums plugin's two date shapes are handled by the
  `museumDate()` helper (see the museum date entry above).

- ~~**Standardize date format in museum data.** — DONE (fixed in the plugin, not the data).~~
  Filed as a code-simplification cleanup, but it was really two user-visible bugs. The 23
  museums split cleanly: 9 carry a full `date_utcz` timestamp, 14 carry a date-only
  `date_ymd`, none carry both. `plugin-museums.js` registered the "Date Visited" field on
  `date_utcz` alone, so for those 14 items:
  - **The year filter hid three years entirely.** The dropdown was built only from
    `date_utcz`, offering 2017/2016/2011/2006/1998 — 1999, 2008 and 2010 were absent, so
    8 of the 23 museums (all of 2010) could not be filtered to at all. Those years *did*
    appear in the stats chart, so the two views of the same data disagreed.
  - **Sorting by Date Visited was broken.** The sort key was `undefined` for 14 of 23
    items, producing visibly unordered output (2010, 2010, 2016, 2008, 2010, ...).

  `renderDetails` already had its own fallback, which is why the date shown on each card
  looked right and masked both bugs.

  Fixed in the plugin rather than by migrating the data: a single `museumDate(item)`
  helper returns `date_utcz || date_ymd`, and it now backs the detail line, the stats year
  buckets, and the field's `value` function — which `deriveFieldsConfig` copies into both
  the sort and filter configs, so one accessor fixes both paths. Both formats lead with
  `YYYY-MM-DD`, so a string compare sorts correctly. This keeps the time-of-day
  information that normalizing everything to `date_ymd` would have discarded.

  Verified in a browser: the year filter now offers all 8 years, filtering on the
  previously-unreachable 1999/2008/2010 returns 3/2/8 correctly-dated museums, sorting by
  Date Visited is monotonic across all 23 cards, the stats chart still totals 23, and
  there are no console errors.

## Accessibility

- ~~**`calendar_google_embed.html` iframe had no `title`.** — DONE.~~
  An unlabeled `<iframe>` is a WCAG failure — screen readers announce it with no name.
  Every other iframe in the project (`slides.md`, `syllabi.md`, `animations.md`) already
  had one. Added `title="My public Google Calendar"`.

  Note: `loading="lazy"` was NOT added, even though those three iframes use it. The
  `tidy` in CI (older than a local 5.8.0) rejects `loading` as a proprietary attribute
  and fails the build. Those three live in `.md` files, which `tidy` never processes —
  only `.html` files do — so they get away with it. If `loading="lazy"` is wanted here,
  the fix is a newer `tidy` in CI, not an exception in the workflow.

## Visitor Counter

- ~~**Visitor counter was permanently broken (counterapi.dev v1 retired).** — PARTIALLY DONE.~~
  `media-app.js` called `https://api.counterapi.dev/v1/...`, which the service has
  retired. It returns `410 {"deprecated":true,"message":"...migrate to v2"}` for every
  request, so both media pages showed visitors a permanent `Page Visits: N/A` and logged
  an error on every page load.

  Fixed the user-visible half: the counter now hides its whole line instead of displaying
  a broken "N/A", and no longer errors on load (verified in a browser — zero console
  errors). The fetch/render wiring is intact behind two constants, `COUNTER_ENDPOINT`
  (currently `null`) and `COUNTER_COUNT_FIELD`.

  **Still needs a decision — this is why it is not fully DONE.** Restoring an actual count
  requires an account nobody can create on your behalf:
  - **counterapi.dev v2** — needs a workspace plus an API key sent as
    `Authorization: Bearer ...`. On a public static site that token is readable by anyone,
    so it has to be one that is safe to expose (like the Calendar browser key, see
    `doc/DECISIONS.md`). Set `COUNTER_ENDPOINT` once the workspace exists.
  - **A different counter service** with a no-auth endpoint — drop its URL into
    `COUNTER_ENDPOINT` and the field name into `COUNTER_COUNT_FIELD`. Nothing else changes.
  - **Site-wide analytics instead of a visible per-page number** — see `doc/ANALYTICS.md`,
    which already recommends GoatCounter. This would not restore the on-page counter.
    Note Google cannot restore it either: GA4 can *record* visits client-side, but *reading*
    the count back needs the GA4 Data API behind an OAuth/service-account credential that is
    not safe to publish. Details and tested results are in the "Visible On-Page Visitor
    Counter" section of `doc/ANALYTICS.md`.
  - **A badge `<img>`** — the only no-signup option verified working from veltzer.org
    (`dwyl/hits`, `visitor-badge.laobi.icu`). Not a `fetch()`, so it sidesteps the CORS wall
    that rules out most free JSON counters; the tradeoff is a fixed-style image.
  - **Drop the feature** — remove the `<p>Page Visits: ...</p>` line from `media.md` and
    `media_app.html` and the `updateVisitorCount` function. Note `doc/problems.txt` lists
    counting and displaying visitors as a goal, so this contradicts a stated want.

## Testing

- ~~**Add unit tests for data import scripts.** — DONE.~~
  Added `tests/` with 27 pytest cases covering `csv_to_yaml.py` and `import_audible.py`:
  the YYYYMMDD -> ISO date rewrite, int/float coercion and what happens when it fails,
  the `METADATA_NOT_FOUND` path, field filtering, and the `QuotedStr` asin handling that
  keeps leading zeros surviving a YAML round trip. `tests/conftest.py` puts `scripts/` on
  `sys.path` since those are standalone executables, not an installed package.

  Wired into the build as `[processor.pytest]`, with `dep_inputs` naming the two scripts
  so edits to them re-run the suite. Verified the tests actually catch regressions by
  mutation testing: flipping the date format to DD-MM-YYYY failed
  `test_converts_yyyymmdd_to_iso`, and dropping the `QuotedStr` wrapper failed both asin
  tests. Both scripts were restored afterwards.

## Infrastructure

- ~~**mkdocs-rss-plugin is not idempotent (non-deterministic builds).** — DONE.~~
  The plugin delegates timestamp generation to MkDocs' `get_build_datetime()`, which
  honours `SOURCE_DATE_EPOCH`. `scripts/build_docs.py` sets
  `SOURCE_DATE_EPOCH` from `git log -1 --format=%ct` before calling `mkdocs build`, so
  `<pubDate>` / `<lastBuildDate>` are pinned to the last git commit time and the feed
  is byte-for-byte stable across rebuilds as long as no new commits are made.

- ~~**Use a persistent cache directory for image picker.** — DONE.~~
  `SEARCH_CACHE_DIR` moved from `/tmp/image_picker_cache` to
  `$XDG_CACHE_HOME/veltzer-site/image-picker`, falling back to `~/.cache` when the
  variable is unset. Downloaded search candidates now survive a reboot, so re-running a
  fetch script does not re-download images it already has.

  Chose the XDG path over the repo-local `.cache/`: that directory belongs to the build
  tooling, and these are user-level downloads rather than build artefacts.
  `download_candidates` already calls `os.makedirs(..., exist_ok=True)`, which creates the
  parents, so no extra setup was needed. Verified the directory is created, the cache-hit
  path returns the cached files, and `XDG_CACHE_HOME` is honoured when set.

- **NOT A PROBLEM: `blog/data/games.pgn.gz` is unreferenced by design.**
  Noting this so it does not get re-flagged by future audits. The file is 2.4 MB, is
  copied in by `scripts/copy_data.py`, and no HTML or JS fetches it — `chess.html:64`
  uses a hardcoded inline PGN instead. This is intentional: the game collection is staged
  for a planned chess viewer that will display it. Leave it in place.

- ~~**Python linters are configured but never run.** — DONE.~~
  Added `[processor.pylint]` and `[processor.mypy]` over `scripts/`, so CI now enforces
  what the config files always specified. Note mypy's `dep_auto` defaults to `mypy.ini`
  while this project uses `.mypy.ini`, so the config is passed explicitly via `args` and
  declared in `dep_inputs`.

  Turning the checks on surfaced 4 real pylint findings in `scripts/serve.py`, all fixed
  rather than suppressed wholesale: a lambda assigned to a variable became a `def`; a bare
  `except Exception` while polling for server startup became
  `except (urllib.error.URLError, OSError)` — which also exposed that `urllib.error` was
  never imported, a latent `NameError` on that path; and `urlopen` in `wait_for_server`
  now uses `with`, closing a response that was previously leaked on every poll. The two
  remaining `consider-using-with` hits are false positives (the server and the browser
  process are both meant to outlive their function and are cleaned up in `main`), so those
  carry targeted `# pylint: disable` comments explaining why.

  `.pylintrc` also gained the `init-hook` it had as a commented placeholder, so `tests/`
  can be linted without false import errors. Verified `serve.py` still works end to end:
  starts, serves a real page, and shuts down cleanly.

- ~~**Dead `src_files` entry in `rsconstruct.toml`.** — DONE.~~
  `[processor.eslint]` listed `src_files = [".eslintrc.js"]`, a file that does not exist
  in the repo. Removed the line; eslint still checks all 10 JS files via `src_dirs`
  (verified in the build output).

- **NOT A PROBLEM: `[processor.shellcheck]` currently checks zero files.**
  `src_dirs = ["scripts"]` but `scripts/` holds only `.py` files, so the status table
  shows 0. Deliberately left in place — it is a check waiting for its inputs, and
  removing it would silently drop shellcheck coverage the moment a `.sh` file is added.

- ~~**`blog/data/` is stale relative to the source repo.** — NOT AN ISSUE.~~
  Retracted. This was inferred from `../data` having commits through 2026-08-03 while the
  copies date to 2026-07-11, but the inference was wrong: the actual source files are
  OLDER than the copies (`all.list.csv` 2026-07-11 10:36, `games.pgn` 2025-09-20), and
  the five plain YAML files diff byte-identical. The later commits in `../data` touched
  files this site does not consume. `blog/data/` is current.

## Internationalization

- **NOT A PROBLEM / DO NOT RETRY: `mkdocs-static-i18n` cannot be used on this site.**
  Recorded because the failure is silent and expensive to rediscover. The plugin is the
  standard way to get a Material language selector, `/he/` URLs and same-page switching,
  and it was tried here on 2026-08-15 for a Hebrew translation of the blog.

  It is incompatible with the `blog` plugin. `blog` generates its post, archive and
  pagination pages *virtually* at build time; `mkdocs-static-i18n` rewrites the file set
  before pages are built and cannot handle them. Result: 34 `Unhandled file case`
  warnings and **zero post pages** — all 80 posts silently vanish.

  The dangerous part is that **the build still exits 0**. CI goes green, `rsconstruct`
  reports success, and the deployed site simply has no blog. It was caught only because
  the output was checked directly.

  Not a config or ordering mistake — verified with `i18n` placed both before and after
  `blog`, identical failure both ways. Upstream issue:
  https://github.com/squidfunk/mkdocs-material/issues/4863 . The `mkdocs-static-i18n`
  project is documented as frozen (core MkDocs upstream unmaintained), so a fix is not
  expected. A comment in `mkdocs.yml` says the same thing at the point of temptation.

  Note the build cache will happily restore the broken output: `rsconstruct clean all` is
  needed before rebuilding, or the empty blog keeps coming back and looks like the revert
  failed.

  If bilingual content is wanted, the options that work today are: Hebrew posts as their
  own posts with per-post RTL and explicit cross-links between an original and its
  translation (no site-wide selector), or replacing/bypassing the `blog` plugin so post
  pages are real files — a much larger change to how the site is built.

## Chess Viewer

- ~~**The chess viewer is broken in production (dead CDN).** — DONE.~~
  `chess.html` loads `https://unpkg.com/cm-chessboard@8.6.0/dist/cm-chessboard.js`,
  which now returns **404 Not Found**. The page therefore throws
  `ReferenceError: Chessboard is not defined` and renders no board at all — only the
  game caption. Confirmed on the live site at `https://veltzer.org/chess.html`, so this
  predates the Zola migration and is not caused by it.

  Fixes, in rough order of robustness: vendor the library into `static/` so an upstream
  removal cannot break the page again; pin a version that still exists on unpkg; or
  switch to a different board library. Vendoring is the only option that makes the page
  independent of a third party's retention policy.

  Related: `doc/IMPROVEMENTS.md` already notes `blog/data/games.pgn.gz` is staged for a
  planned chess viewer. Whatever replaces the CDN should probably read that file rather
  than the hardcoded inline PGN currently in `chess.html`.

  Fixed by vendoring both libraries into `static/vendor/` -- the page now loads nothing
  from a CDN except Tailwind, so an upstream removal cannot break it again. Three separate
  faults had to be fixed, only the first of which was the dead CDN:

  1. `unpkg` had removed `cm-chessboard@8.6.0` entirely (404), so `Chessboard` was never
     defined. Vendored 8.13.0.
  2. 8.x is **ESM-only** with relative imports, so the old `<script src>` could never work
     regardless of version. The page now uses `<script type="module">` and imports
     `{Chessboard, FEN}`. The config API also changed: `sprite: {url, size}` became
     `assetsUrl` plus `style.pieces.file`, and `position: "start"` must now be `FEN.start`
     (the shorthand throws inside `Position.setFen`).
  3. **The PGN never parsed, independently of any of the above.** chess.js requires a blank
     line between the header block and the movetext, and will not accept header lines that
     start with whitespace -- the literal in `chess.html` is indented to match the
     surrounding code. `load_pgn()` simply returned `false` and the viewer showed an empty
     board with the Next button disabled. Both are now handled, and a failed parse shows
     "Could not load the game." instead of failing silently.

  Verified in a browser: 32 pieces render, stepping forward walks e4, e5, Nf3, d6 ... to
  "Move 33: Rd8#" (the checkmate ending the Opera Game), Prev walks back, no console errors.

## Blog Content

- **NOT A PROBLEM: overlap between posts.**
  Posts on related themes revisiting shared ground is by design — each post stands on its
  own. Do not raise this as an issue.

- ~~**Dangling forward reference with the wrong tense.** — DONE.~~
  `geography_of_belief.md` said "(We'll cover this point in more depth in a separate
  post.)" about a post that had already published three weeks earlier. Changed to past
  tense and linked to `../04/outsider_test_for_faith.md`. The underlying content overlap
  between the two posts is still open — see the redundancy item above.

- ~~**The 3-tag convention was abandoned.** — DONE.~~
  All 33 single-tag posts (the entire 2026/04-05 religion sequence) now carry `religion`
  plus 1-2 topical tags, restoring the convention every pre-2026 post follows. Grouped as:
  history/textual criticism (`history`, `bible`, `archaeology`), philosophy of religion
  (`philosophy`, `ethics`), epistemology (`epistemology`, `science`), science/evidence
  (`science`, `neuroscience`, `statistics`) and culture (`culture`). Eight of the ten tags
  already existed in the vocabulary; only `ethics` and `neuroscience` are new. Proposed to
  and approved by the author before applying — the taxonomy is an editorial call.

  `atheism` was deliberately left on its single post rather than spread across the ~40
  posts arguing that position; that is a larger statement about self-labelling.

  ~~Original entry:~~
  Every pre-2026 post and every 2026/03 post has exactly 3 tags. 33 of the 2026 religion
  posts have exactly one (`religion`), which makes the tag index near-useless for half
  the corpus. Related: 32 of the 64 distinct tags are used exactly once, so half the tag
  index is single-item pages. Specific oddities — `atheism` is on exactly one post
  (`problem_of_evil.md`) despite ~40 posts arguing that position; `theory` is used only
  on `musical-tempo-table.md` where it means *music theory* and reads as a generic
  bucket next to `game-theory`; `bayes` / `probability` / `statistics` are three tags for
  one topic area.

- ~~**Same-day date collisions make ordering arbitrary.** — DONE for the 2026 clusters.~~
  16 posts re-dated: the 10 sharing 2026-04-04 spread across 2026-03-26..2026-04-05 plus
  04-19, the 6 sharing 2026-04-06 across 04-06 and 04-20..04-24, and 2 of the 3 sharing
  2026-05-30 to 05-28/05-29. Free windows were checked first so no new collisions were
  introduced. Four posts whose dates moved into March were `git mv`d into `2026/03/` to
  keep the directory matching the front matter.

  The author accepted the known cost: these are published URLs derived from `date:`, so
  the moved posts get new URLs and may re-surface in RSS readers.

  Four pre-2026 collisions remain (2 on 2010-06-11, 2 on 2010-06-19, 3 on 2010-07-21, 2
  on 2025-09-01). Left alone — they are small, old, and not worth the URL churn.

  ~~Original entry:~~
  10 posts share 2026-04-04, 7 share 2026-04-06, 3 share 2026-05-30. The blog plugin
  orders by date, so ties fall back to filename order rather than intended reading order.

- ~~**Minor: inconsistent capitalization between a post and its own sequel.** — DONE.~~
  `wordpress-and-unix-security.md` used "Wordpress" in its H1 while its own part 2 used
  the correct "WordPress". Fixed the part 1 heading.

- ~~**Minor: the two Hebrew posts have RTL titles but no `lang`/`dir` metadata.** — DONE.~~
  Both posts rendered inside `<html lang="en">` with no `dir` anywhere, so Hebrew text was
  laid out left-to-right: punctuation on the wrong side and mixed Hebrew/English lines in
  the wrong order. Added `lang: he` to the front matter of both, plus
  `overrides/partials/content.html`, which wraps a post's rendered body in
  `<div lang="he" dir="rtl">` when the front matter asks for it. RTL rules in
  `blog/custom.css` are scoped to `[lang="he"]`, so the other 78 posts are untouched and
  site chrome stays LTR.

  Two things worth knowing if this is ever revisited:
  - The override targets `partials/content.html`, NOT `main.html`. Blog posts render via
    `blog-post.html`, which defines its own `content` block, so a `main.html` override is
    silently ignored -- it builds fine and does nothing. Forking `blog-post.html` would
    work but means re-syncing 138 lines on every theme upgrade; the partial is 12 lines.
  - `{% extends "blog-post.html" %}` from a same-named override recurses infinitely
    (`RecursionError`), so extending the theme's own template by name is not an option.

  Verified in a browser: Hebrew prose computes `direction: rtl` / `text-align: right`
  while the header and `<body>` stay `ltr`; an English post has no wrapper and computes
  `ltr`. Post count (80) and sitemap (105 URLs) unchanged.

  Still open: `hebrew` remains a language tag in an otherwise topical tag vocabulary.
