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

- ~~**`blog/data/` is stale relative to the source repo.** — NOT AN ISSUE.~~
  Retracted. This was inferred from `../data` having commits through 2026-08-03 while the
  copies date to 2026-07-11, but the inference was wrong: the actual source files are
  OLDER than the copies (`all.list.csv` 2026-07-11 10:36, `games.pgn` 2025-09-20), and
  the five plain YAML files diff byte-identical. The later commits in `../data` touched
  files this site does not consume. `blog/data/` is current.

## Blog Content

- **NOT A PROBLEM: overlap between posts.**
  Posts on related themes revisiting shared ground is by design — each post stands on its
  own. Do not raise this as an issue.

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
