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

- **Convert YAML data to JSON at build time for performance.**
  `youtube.yaml.gz` is 1.7MB compressed. Parsing with js-yaml in-browser on every page load
  is slow on mobile. `JSON.parse` is ~10x faster than YAML parsing. Pre-process during build.

- **Add null guards in media plugins.**
  Several plugins assume fields like `item.rating` or `item.date_utcz` always exist.
  Missing fields cause rendering failures or `NaN` in stats.
  Add defensive checks in `renderDetails` and `renderStats`.

- **Standardize date format in museum data.**
  Museums plugin has `date_utcz` / `date_ymd` fallback logic.
  Standardize on one format in the YAML data to simplify the code.

## Testing

- **Add unit tests for data import scripts.**
  `csv_to_yaml.py` and `import_audible.py` transform data with zero test coverage.
  A bug silently corrupts the media database. Add pytest tests for these at minimum.

## Infrastructure

- ~~**mkdocs-rss-plugin is not idempotent (non-deterministic builds).** — DONE.~~
  The plugin delegates timestamp generation to MkDocs' `get_build_datetime()`, which
  honours `SOURCE_DATE_EPOCH`. `scripts/build_docs.sh` exports
  `SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)` before calling `mkdocs build`, so
  `<pubDate>` / `<lastBuildDate>` are pinned to the last git commit time and the feed
  is byte-for-byte stable across rebuilds as long as no new commits are made.

- **Use a persistent cache directory for image picker.**
  `image_picker.py` caches downloaded images to `/tmp` (lost on reboot).
  Use `~/.cache/veltzer-site/` or a project-local `.cache/` directory instead.
