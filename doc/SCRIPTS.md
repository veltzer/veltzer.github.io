# Scripts Reference

## Build Scripts

### `scripts/build_docs.sh`
Full site build. Runs image check then `mkdocs build`. MkDocs reads
from `blog/` and writes to `docs/`.

### `scripts/copy_data.sh`
Copies YAML data and PGN files from `../data/` repo into `blog/data/`,
converts YouTube CSV to YAML, and gzips everything. Uses `gzip -n` for
reproducible output. Validates source files exist before copying.

## Image Fetch Scripts

All image scripts are incremental — they skip images that already exist.
Use `--force` to re-download.

### `scripts/fetch_movie_posters.py`
Downloads movie poster images from TMDB (with OMDB fallback) by IMDB ID.
Output: `blog/images/movie-{imdb_id}.jpg`
Requires: `pass` entries `keys/themoviedb.org.read` and `keys/omdbapi.com.key`

### `scripts/fetch_series_posters.py`
Downloads TV series poster images from TMDB (with OMDB fallback) by IMDB ID.
Output: `blog/images/series-{imdb_id}.jpg`
Requires: same as movie posters.

### `scripts/fetch_audiocourse_images.py`
Downloads audio course cover images. Uses Great Courses CDN for courses
with `great_courses_id`, Audible for those with `audible_asin`, and
DuckDuckGo image search with tkinter GUI picker for the rest.
Output: `blog/images/audiocourse-{gc|audible|internal}-{id}.jpg`

### `scripts/fetch_audible_images.py`
Downloads Audible book cover images using the `cover_url` field from
the YAML. No API keys or authentication needed.
Output: `blog/images/audible-{asin}.jpg`

### `scripts/fetch_museum_images.py`
Downloads museum images via DuckDuckGo image search with tkinter GUI picker.
Searches for `"{name} museum {city}"`.
Output: `blog/images/museum-{internal_id}.jpg`

### `scripts/fetch_podcast_images.py`
Downloads podcast images via DuckDuckGo image search with tkinter GUI picker.
Output: `blog/images/podcast-{internal_id}.jpg`

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
Verifies every media item has a corresponding image in `blog/images/`.
Checks movies, series, audible, audio courses, museums, and podcasts.
Skips YouTube (uses external CDN thumbnails). Run automatically by
`build_docs.sh` before `mkdocs build`.

## API Key Management

### `scripts/manage_api_key.sh`
Manages the Google Calendar API key. Commands: `show`, `restrict`,
`create`, `delete`, `rotate`. Reads/writes key via `pass` at
`cloud/gcp/calendar`. The `rotate` command creates a new key, waits
for rebuild/deploy, then deletes the old one.

## Scripts in `../data/` repo

### `../data/scripts/fetch_great_courses_ids.py`
Interactive script to look up Great Courses IDs and slugs by searching
shop.thegreatcourses.com. Shows course info, professor, and cover image
for confirmation. Incremental with cache in `/tmp/great_courses_cache.json`.

### `../data/scripts/check_great_courses_unique.py`
Checks that all `great_courses_id` and `great_courses_slug` values
in `audio_courses.yaml` are unique.

### `../data/scripts/check_audio_courses_ids.py`
Checks that every audio course has at least one identifier:
`great_courses_id`, `audible_asin`, or `internal_id`.

### `../data/scripts/check_audio_courses_lecturers.py`
Compares lecturer names in YAML against professor names on The Great
Courses website for courses with a `great_courses_slug`.

### `../data/scripts/apply_slugs.py`
One-time script to apply manually looked-up Great Courses slugs.
Shows course page info for confirmation before writing.
