# Scripts Reference

## Build Scripts

### `scripts/build_site.py`

The zola build, run by `rsconstruct build` (never invoke `zola build` by
hand -- see `CLAUDE.md`). Imports the teaching data, regenerates the archive
stats via `scripts/gen_stats.py`, writes `static/build_info.toml`, syncs the
theme submodule's tokens into `static/`, then runs `zola build` with
`PYTHONHASHSEED=0` into `_site/` and post-processes the output (moves the
English pages under `/en/`, fixes the sitemap, writes the root redirect).

### `scripts/copy_data.py`

Copies YAML data and PGN files from the `../data/` repo into `static/data/`,
converts the YouTube CSV to YAML, runs the audible and books imports,
converts every YAML file to JSON (the frontend reads JSON, not YAML) and
gzips everything. Uses `gzip -n` for reproducible output. Validates source
files exist before copying. A manual step, not part of the build: CI has no
`../data` checkout, and the generated `static/data/` is committed.

The two chess archives (`games.pgn.gz`, `chesscom.pgn.gz`) arrive gzipped
and are decompressed and concatenated into a single `games.pgn`, which the
common gzip step then compresses like every other data file. The chess
viewer fetches that one merged file.

## Image Fetch Scripts

All image scripts are incremental — they skip images that already exist.
Use `--force` to re-download.

### `scripts/fetch_movie_posters.py`

Downloads movie poster images from TMDB (with OMDB fallback) by IMDB ID.
Output: `static/images/movie-{imdb_id}.jpg`
Requires: `pass` entries `keys/themoviedb.org.read` and `keys/omdbapi.com.key`

### `scripts/fetch_series_posters.py`

Downloads TV series poster images from TMDB (with OMDB fallback) by IMDB ID.
Output: `static/images/series-{imdb_id}.jpg`
Requires: same as movie posters.

### `scripts/fetch_audiocourse_images.py`

Downloads audio course cover images. Uses Great Courses CDN for courses
with `great_courses_id`, Audible for those with `audible_asin`, and
DuckDuckGo image search with tkinter GUI picker for the rest.
Output: `static/images/audiocourse-{gc|audible|internal}-{id}.jpg`

### `scripts/fetch_audible_images.py`

Downloads Audible book cover images using the `cover_url` field from
the YAML. No API keys or authentication needed.
Output: `static/images/audible-{asin}.jpg`

### `scripts/fetch_book_covers.py`

Downloads book covers for `books_read.yaml`. Every book carries a goodreads
or simania id; both sites publish the cover as the page's `og:image`, so no
API key is needed. goodreads pages are fetched through `/en/book/show/<id>`
(the plain url answers scripts with an empty WAF challenge).
Output: `static/images/book-{cover}.jpg`, where `{cover}` is the key
`scripts/import_books.py` puts on each item (`simania-<id>`, else
`goodreads-<id>`). A book whose page has no cover (listed in
`import_books.NO_COVER`) gets no key and the card shows
`static/images/book-no-cover.jpg`, a hand-made placeholder drawn at the
card's 800x384 geometry so `object-cover` crops nothing that matters.

### `scripts/import_books.py`

Flattens `../data/yaml/books_read.yaml` (names, authors, ownings and
readings, each a list per language) into one item per book for the media
page: `name`, `authors`, `rating`/`last_read`/`review` of the latest dated
reading, `readings`, `owned_languages`, `cover`, `url`. Run by
`scripts/copy_data.py`.

### `scripts/fetch_museum_images.py`

Downloads museum images via DuckDuckGo image search with tkinter GUI picker.
Searches for `"{name} museum {city}"`.
Output: `static/images/museum-{internal_id}.jpg`

### `scripts/fetch_podcast_images.py`

Downloads podcast images via DuckDuckGo image search with tkinter GUI picker.
Output: `static/images/podcast-{internal_id}.jpg`

## Shared Modules

### `scripts/image_picker.py`

Shared module used by museum, podcast, and audio course image scripts.
Provides DuckDuckGo image search (with caching in `/tmp/image_picker_cache/`)
and a tkinter image browser GUI with prev/next/select/skip/quit.

### `scripts/poster_utils.py`

Shared module used by movie and series poster scripts. Provides TMDB
and OMDB poster lookup with fallback.

## Validation Scripts

### `scripts/check_images.py`

Verifies every media item has a corresponding image in `static/images/`.
Checks movies, series, audible, audio courses, museums, podcasts, and books.
Skips YouTube (uses external CDN thumbnails). Not part of the build; run
manually as needed.

### `scripts/check_profile_links.py`

Requests every profile URL in `../data/yaml/profiles.yaml` — the ~30 links
rendered into `content/about/` and into `README.md` in the `../veltzer`
repository — and reports anything that no longer resolves. Run on demand:

```bash
scripts/check_profile_links.py            # problems only
scripts/check_profile_links.py --verbose  # list the working links too
```

Deliberately not part of `rsconstruct build`: a third-party outage must not fail
a site build, and nothing else in the build needs the network. Exits 1 if
anything is broken, so it can still gate a release script.

Results are split three ways, and the middle one is the point. Several of these
hosts answer an automated client with 403 while serving the page fine in a
browser — udemy did exactly that on one run here and not the next. Those are
reported as **blocked** rather than **broken**, so the report stays worth
reading; without that split it would be mostly false positives. The checker
sends a browser User-Agent and retries with GET when HEAD fails, since a number
of hosts do not implement HEAD properly.

## API Key Management

### `scripts/manage_api_key.py`

Manages a Google API key. Commands: `show`, `restrict`, `create`,
`delete`, `rotate`. Reads/writes the key via `pass`. The `rotate` command
creates a new key, waits for rebuild/deploy, then deletes the old one.
Project-specific values are no longer hardcoded — they default to the
calendar key (`--project-id veltzer-calendar-id`, `--pass-path
cloud/gcp/calendar`, `--referrer veltzer.github.io/*`, etc.) and can be
overridden via flags or the matching `API_KEY_*` environment variables.

## Scripts in `../data/` repo

### `../data/scripts/great_courses_fetch_ids.py`

Interactive script to look up Great Courses IDs and slugs by searching
shop.thegreatcourses.com. Shows course info, professor, and cover image
for confirmation. Incremental with cache in `/tmp/great_courses_cache.json`.

### `../data/scripts/great_courses_check_unique.py`

Checks that all `great_courses_id` and `great_courses_slug` values
in `audio_courses.yaml` are unique.

### `../data/scripts/audio_courses_check_ids.py`

Checks that every audio course has at least one identifier:
`great_courses_id`, `audible_asin`, or `internal_id`.

### `../data/scripts/audio_courses_check_lecturers.py`

Compares lecturer names in YAML against professor names on The Great
Courses website for courses with a `great_courses_slug`.
