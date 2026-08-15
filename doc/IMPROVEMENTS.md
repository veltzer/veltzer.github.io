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

- **Cross-file naming inconsistency.**
  Some files use `name` (podcasts, museums, video_features, video_series, audio_courses),
  others use `title` (audible, youtube). Some use `url`, others `webpage_url` or `cover_url`.
  Consider unifying to `title` everywhere for the primary name field.

- ~~**YouTube: `upload_date` uses `YYYYMMDD` format.** — DONE.~~
  `csv_to_yaml.py` now converts to `YYYY-MM-DD` and the frontend `formatDate` was simplified.

## SEO / Domain

- **Canonical URLs point at a domain that redirects away.** (highest impact)
  `mkdocs.yml` sets `site_url: "https://veltzer.github.io"`, but `CNAME` serves the site
  at `veltzer.org`. Verified live: `veltzer.org` emits
  `<link rel="canonical" href="https://veltzer.github.io/">` on every page, while
  `veltzer.github.io` returns `301 -> https://veltzer.org/`. So every page declares its
  canonical to be a URL that immediately bounces back, which splits ranking off the real
  domain. The same single `site_url` line also drives:
  - all 105 `<loc>` entries in the generated `sitemap.xml`;
  - every `<guid isPermaLink="true">` and item `<link>` in `feed_rss_created.xml` (if the
    domain is ever changed, GUIDs churn and every post re-appears as new in readers);
  - `blog/robots.txt` line 4, a cross-host `Sitemap:` reference that crawlers ignore.

  Fix is one line (`site_url: "https://veltzer.org"`) plus the hardcoded RSS links in
  `mkdocs.yml` (social link) and `blog/index.md` line 5. Note `CLAUDE.md` currently
  documents the split as intentional; that note should be updated too.

- ~~**`blog/sitemap.xml` is dead weight.** — DONE.~~
  Was a hand-written 9-URL sitemap, 2 of whose URLs (`/media.html`, `/calendar.html`)
  did not exist in the build. It never broke anything — MkDocs overwrites it — but it was
  a stale hand-maintained copy with no effect. Deleted; the generated 105-URL sitemap is
  unaffected (verified post-deletion).

## Security

- **Restrict Google Calendar API key.**
  `blog/keys.js` ships the API key to every visitor on the public site.
  Restrict the key in the Google Cloud Console with an HTTP referrer restriction to `veltzer.github.io/*`.

## Python Code Quality

- **Deduplicate image picker GUI in `fetch_audiocourse_images.py`.**
  This script (387 lines) reimplements the tkinter image browser that already exists in `image_picker.py`.
  Refactor to reuse `image_picker.pick_image()`.

- **Replace fragile YAML parsing in `check_images.py`.**
  Uses a line-by-line state machine instead of `yaml.safe_load()` / gzip.
  Will break on multi-line values, comments, or quoting changes. Use proper YAML parsing.

- **Use BeautifulSoup instead of regex for HTML scraping.**
  `fetch_audiocourse_images.py` extracts `og:image` via regex.
  Use BeautifulSoup for resilience against page layout changes.

- **Standardize logging across scripts.**
  Scripts mix `print()`, `print(..., file=sys.stderr)`, and silent failures.
  Add `logging.basicConfig()` at the top of each script for consistent output.

- **Use script-relative paths instead of hardcoded relative paths.**
  Scripts use paths like `../data/yaml/` or `blog/data/`, only working from specific directories.
  Use `pathlib.Path(__file__).parent` to compute paths relative to the script location.

- **Split `fetch_audiocourse_images.py` into smaller pieces.**
  Handles three different image sources (Great Courses CDN, Audible scraping, DuckDuckGo search)
  in one 387-line file. Split into a strategy pattern or separate functions per source.

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

- **Convert YAML data to JSON at build time for performance.**
  `youtube.yaml.gz` is 1.7MB compressed. Parsing with js-yaml in-browser on every page load
  is slow on mobile. `JSON.parse` is ~10x faster than YAML parsing. Pre-process during build.

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

- **Add null guards in media plugins.**
  Several plugins assume fields like `item.rating` or `item.date_utcz` always exist.
  Missing fields cause rendering failures or `NaN` in stats.
  Add defensive checks in `renderDetails` and `renderStats`.

- **Standardize date format in museum data.**
  Museums plugin has `date_utcz` / `date_ymd` fallback logic.
  Standardize on one format in the YAML data to simplify the code.

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

## Testing

- **Add unit tests for data import scripts.**
  `csv_to_yaml.py` and `import_audible.py` transform data with zero test coverage.
  A bug silently corrupts the media database. Add pytest tests for these at minimum.

## Infrastructure

- ~~**mkdocs-rss-plugin is not idempotent (non-deterministic builds).** — DONE.~~
  The plugin delegates timestamp generation to MkDocs' `get_build_datetime()`, which
  honours `SOURCE_DATE_EPOCH`. `scripts/build_docs.py` sets
  `SOURCE_DATE_EPOCH` from `git log -1 --format=%ct` before calling `mkdocs build`, so
  `<pubDate>` / `<lastBuildDate>` are pinned to the last git commit time and the feed
  is byte-for-byte stable across rebuilds as long as no new commits are made.

- **Use a persistent cache directory for image picker.**
  `image_picker.py` caches downloaded images to `/tmp` (lost on reboot).
  Use `~/.cache/veltzer-site/` or a project-local `.cache/` directory instead.

- **NOT A PROBLEM: `blog/data/games.pgn.gz` is unreferenced by design.**
  Noting this so it does not get re-flagged by future audits. The file is 2.4 MB, is
  copied in by `scripts/copy_data.py`, and no HTML or JS fetches it — `chess.html:64`
  uses a hardcoded inline PGN instead. This is intentional: the game collection is staged
  for a planned chess viewer that will display it. Leave it in place.

- **Python linters are configured but never run.**
  `.pylintrc` and `.mypy.ini` exist and cover the 16 scripts in `scripts/`, but
  `rsconstruct.toml` declares no processor for either, so CI never enforces them.
  Current state if run manually: mypy is clean; pylint is clean except 4 minor warnings
  in `scripts/serve.py` (a dev-only script) — `unnecessary-lambda-assignment`,
  `broad-exception-caught`, and two `consider-using-with`. Cheap to add and to keep green.

- ~~**Dead `src_files` entry in `rsconstruct.toml`.** — DONE.~~
  `[processor.eslint]` listed `src_files = [".eslintrc.js"]`, a file that does not exist
  in the repo. Removed the line; eslint still checks all 10 JS files via `src_dirs`
  (verified in the build output).

- **NOT A PROBLEM: `[processor.shellcheck]` currently checks zero files.**
  `src_dirs = ["scripts"]` but `scripts/` holds only `.py` files, so the status table
  shows 0. Deliberately left in place — it is a check waiting for its inputs, and
  removing it would silently drop shellcheck coverage the moment a `.sh` file is added.

- **`blog/data/` is stale relative to the source repo.**
  The copies were last refreshed 2026-07-11; the upstream `../data` repo has commits
  through 2026-08-03. The five plain YAML files diff byte-identical, so any actual drift
  is in the chess PGN / YouTube CSV sources. Worth a `copy_data.py` run to confirm.

## Blog Content

- **Redundant posts in the 2026/04-05 religion cluster.**
  - `euthyphro_dilemma.md` and `divine_command_theory_problems.md` run substantially the
    same argument, including the same rebuttal to the same "God's nature *is* goodness"
    dodge. Consider merging, or making the second explicitly a follow-on that links the
    first rather than restating it.
  - `brain_damage_disproves_the_soul.md`, `mind_brain_no_distinction.md`, and
    `neurotheology.md` overlap heavily on the mind-is-the-brain thesis.
  - `ancient_israel_polytheism.md` and `evolution_of_yahweh.md` both cover Yahweh's
    emergence from the Canaanite pantheon and the Asherah inscriptions.
  - `exodus_history_vs_myth.md` and `archaeology_of_the_conquest.md` both argue for
    indigenous emergence in Canaan.

- ~~**Dangling forward reference with the wrong tense.** — DONE.~~
  `geography_of_belief.md` said "(We'll cover this point in more depth in a separate
  post.)" about a post that had already published three weeks earlier. Changed to past
  tense and linked to `../04/outsider_test_for_faith.md`. The underlying content overlap
  between the two posts is still open — see the redundancy item above.

- **The 3-tag convention was abandoned.**
  Every pre-2026 post and every 2026/03 post has exactly 3 tags. 33 of the 2026 religion
  posts have exactly one (`religion`), which makes the tag index near-useless for half
  the corpus. Related: 32 of the 64 distinct tags are used exactly once, so half the tag
  index is single-item pages. Specific oddities — `atheism` is on exactly one post
  (`problem_of_evil.md`) despite ~40 posts arguing that position; `theory` is used only
  on `musical-tempo-table.md` where it means *music theory* and reads as a generic
  bucket next to `game-theory`; `bayes` / `probability` / `statistics` are three tags for
  one topic area.

- **Same-day date collisions make ordering arbitrary.**
  10 posts share 2026-04-04, 7 share 2026-04-06, 3 share 2026-05-30. The blog plugin
  orders by date, so ties fall back to filename order rather than intended reading order.

- ~~**Minor: inconsistent capitalization between a post and its own sequel.** — DONE.~~
  `wordpress-and-unix-security.md` used "Wordpress" in its H1 while its own part 2 used
  the correct "WordPress". Fixed the part 1 heading.

- **Minor: the two Hebrew posts have RTL titles but no `lang`/`dir` metadata.**
  `hebrew_security_policy.md` and `hebrew_tyson_survival.md`. Also note `hebrew` is a
  language tag sitting in an otherwise topical tag vocabulary.
