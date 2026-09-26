# Scripts Reference

## Build Scripts

### `scripts/build_site.py`

The zola build, run by `rsconstruct build` (never invoke `zola build` by
hand -- see `CLAUDE.md`). Imports the teaching pages via
`scripts/import_teaching.py` (skipped when the sibling repos are absent, as in
CI), regenerates the archive stats via `scripts/gen_stats.py`, writes
`static/build_info.toml`, syncs the theme submodule's tokens into `static/`,
then runs `zola build` into `_site/` and post-processes the output (copies
the English feed to `/atom.xml`, the URL every page advertised until
2026-09-21; writes the legacy redirects; drops the paginator redirect stubs
from the sitemap and adds the root to it; writes the root language-chooser
page). `relocate_english()`, which used to sweep unprefixed English output
under `/en/`, was removed on 2026-09-21: every section is an explicit
`_index.en.md`, so zola emits both languages prefixed itself.

`write_legacy_redirects()` serves the pre-migration URLs Google still has
indexed -- MkDocs-era `/YYYY/MM/DD/<slug>/` permalinks and the root-level
zola URLs from before English moved to `/en/`. The map is `LEGACY_REDIRECTS`;
paginator URLs are expanded from the build output rather than listed. It is
kept as a post-processing step rather than zola `aliases` because aliases
exist only for pages, and half of what it rescues is not one (paginator URLs,
`/ascx/public_key.asc`, a section); see `doc/SEO.md` for the history.

`fix_sitemap()` also drops every `/page/1/` entry (`drop_redirecting_urls()`).
Zola emits that URL for each paginated section and builds it as a redirect to
the paginator root, so listing it makes the sitemap advertise 112 redirects.
The redirect stays for anyone holding such a link; only the sitemap entry goes.

## check_redirects.py

Asks the deployed site whether the retired URLs still work. It imports
`LEGACY_REDIRECTS` from `build_site.py` rather than keeping its own list, so
it cannot drift from what the build generates, and requests each source
against the live site along with the sitemap and the three non-canonical
host variants. Exits non-zero on any failure.

Not part of the build -- it talks to the network and tests the deployment,
not the tree. Run it after a deploy, or when Search Console reports an
indexing problem, to tell a regression here from Google's own crawl timing.
It deliberately cannot read a validation verdict: that is behind a Google
login, and `doc/SEO.md` says where to read it by hand.

### `scripts/import_teaching.py`

Imports the three sibling teaching sites (`../teaching-slides`,
`../teaching-syllabi`, `../teaching-animations`) into
`content/{slides,syllabi,animations}/_index.en.md` as native zola pages. Each
sibling builds a single self-contained `_site/index.html`; the script strips
the document wrapper, drops the embedded header and theme `<select>` (this
site's chrome supplies both), scopes the page's CSS under an `#app-<section>`
wrapper, and writes the result with this site's front matter. Run by
`scripts/build_site.py` when the sibling `_site/` directories exist, and
skipped otherwise, so CI (which has no sibling checkouts) builds from the
committed copies. `--check` reports what would be written without writing.
The Hebrew `_index.he.md` stubs are hand-written and are not touched.

### `scripts/gen_stats.py`

Computes the blog archive statistics (post counts per year and per language)
and rewrites the `[extra.stats]` table below the `# BEGIN generated stats`
marker in `content/blog/_index.en.md` and `_index.he.md`; everything above the
marker is preserved. Also writes `static/tag_translations.toml`, one row per
tag pair, derived by zipping each post's tag list with its translation's
(the lists must be in the same order); `templates/base.html` reads it so a
tag page's language switcher and hreflang alternates point at the same tag in
the other language. Fails the build if any `.en.md` post lacks its `.he.md`
translation or vice versa (an unpaired post would otherwise lose its language
switcher silently), if a pair's tag lists differ in length, or if a tag lines
up with two different counterparts. Part of the build (run from
`scripts/build_site.py`); both outputs are committed so `zola serve` shows the
right numbers and links.

### `scripts/gen_profiles.py`

Renders `data/yaml/profiles.yaml` into the region between the
`<!-- BEGIN generated profiles -->` markers in `content/about/_index.en.md`
and `_index.he.md` (contact line, intro, link groups and extras, in both
languages), and writes `static/identity.toml`, the `sameAs` URLs the
`Person` JSON-LD in `templates/base.html` reads. A manual step whose
output is committed. Run it after editing `profiles.yaml` and commit.

### `scripts/copy_data.py`

Builds `static/data/` from the media YAML in `data/yaml/` and the chess
archives and YouTube CSV in the sibling `../data/` repo: converts the
YouTube CSV to YAML, runs the audible and books imports, converts every
YAML file to JSON (the frontend reads JSON, not YAML) and gzips everything.
Uses `gzip -n` for reproducible output. Validates source files exist before
copying. A manual step, not part of the build: CI has no `../data` checkout
for the chess and YouTube half, and the generated `static/data/` is committed.

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

### `scripts/csv_to_yaml.py`

Converts the YouTube CSV export (`input output` positional arguments) into
the trimmed YAML the media viewer loads, keeping only title, channel, upload
date, duration, view count, categories and URL. Rows whose title is
`METADATA_NOT_FOUND` are kept with `status: missing` and a rebuilt watch URL
so the viewer can still link out. Run by `scripts/copy_data.py`.

### `scripts/import_audible.py`

Copies `data/yaml/audible.yaml` into `static/data/` keeping only the
fields the audible plugin uses, with integer fields coerced and string
fields force-quoted so the output is stable. Run by `scripts/copy_data.py`.

### `scripts/import_books.py`

Flattens `data/yaml/books_read.yaml` (names, authors, ownings and
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
Provides DuckDuckGo image search (with candidates cached under
`$XDG_CACHE_HOME/veltzer-site/image-picker/`, defaulting to
`~/.cache/veltzer-site/image-picker/`, so they survive a reboot) and a
tkinter image browser GUI with prev/next/select/skip/quit.

### `scripts/poster_utils.py`

Shared module used by movie and series poster scripts. Provides TMDB
and OMDB poster lookup with fallback.

### `scripts/image_standard.py`

One place that decides how large an image in `static/images/` may be
(`800x384>`, JPEG, EXIF stripped) and the `normalise()` function the fetchers
call on save. The numbers are derived from the card geometry in
`media-app.js`; the module docstring explains the arithmetic.

### `scripts/normalise_images.py`

Brings every existing image in `static/images/` down to that standard, for
files that predate `image_standard.py` or were added by hand. Reports what
would change by default; `--apply` does it. Idempotent: images already within
the box are skipped.

## Spellcheck Scripts

### `scripts/build_en_dict.sh`, `scripts/build_he_dict.sh`

Compile the allowlists `.aspell.en.txt` and `.aspell.he.txt` into aspell
dictionaries under `out/aspell/` (gitignored). They are scripts rather than
plain commands because aspell resolves relative paths against
`/usr/lib/aspell` and cannot take the allowlist as a `--personal` wordlist
(Hebrew segfaults, English mojibakes non-Latin-1 entries). Run by
`rsconstruct build` as generator processors; the comments in the scripts
record the aspell quirks in detail.

### `scripts/spellcheck_en.sh`, `scripts/spellcheck_he.sh`

Run `aspell list` over the blog posts of one language with the compiled
allowlist as an extra dictionary, and fail on any misspelled word. Run by
`rsconstruct build` over `content/blog/*.en.md` and `*.he.md`. Each builds its
dictionary itself if it is missing, because rsconstruct does not order
generators before checkers.

## Validation Scripts

### `scripts/check_images.py`

Verifies every media item has a corresponding image in `static/images/`.
Checks movies, series, audible, audio courses, museums, podcasts, and books.
Skips YouTube (uses external CDN thumbnails). Not part of the build; run
manually as needed.

### `scripts/check_profile_links.py`

Requests every profile URL in `data/yaml/profiles.yaml` — the ~30 links
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

## Local Preview

### `scripts/serve.py`

Runs the full `scripts/build_site.py` build, then serves `_site/` with a plain
static server, which is the closest local approximation to GitHub Pages
(`zola serve` builds in memory and skips the post-processing). Options:
`--port`, `--preview` (open a browser), `--anonymous` (a browser with a fresh
temp profile, implies `--preview`), `--no-build`.

## API Key Management

### `scripts/manage_api_key.py`

Manages a Google API key. Commands: `show`, `restrict`, `create`,
`delete`, `rotate`. Reads/writes the key via `pass`. The `rotate` command
creates a new key, waits for rebuild/deploy, then deletes the old one.
Project-specific values are no longer hardcoded — they default to the
calendar key (`--project-id veltzer-calendar-id`, `--pass-path
cloud/gcp/calendar`, `--referrer veltzer.org/*`, etc.) and can be
overridden via flags or the matching `API_KEY_*` environment variables.

## Data maintenance scripts

These edit or check the YAML under `data/yaml/` and use paths relative to
the repository root, so run them from there. They came across from the
`../data` repo together with the YAML in 2026-09.

### `scripts/great_courses_fetch_ids.py`

Interactive script to look up Great Courses IDs and slugs by searching
shop.thegreatcourses.com. Shows course info, professor, and cover image
for confirmation. Incremental with cache in `/tmp/great_courses_cache.json`.

### `scripts/great_courses_check_unique.py`

Checks that all `great_courses_id` and `great_courses_slug` values
in `audio_courses.yaml` are unique.

### `scripts/audio_courses_check_ids.py`

Checks that every audio course has at least one identifier:
`great_courses_id`, `audible_asin`, or `internal_id`.

### `scripts/audio_courses_check_lecturers.py`

Compares lecturer names in YAML against professor names on The Great
Courses website for courses with a `great_courses_slug`.

### `scripts/books_fetch_ids.py`

Interactive lookup of goodreads ids for the books in `books_read.yaml` that
have none yet: searches goodreads by the english title, scores the hits,
verifies a confirmed hit against the book page and writes the id (and the
exact page title, which `check_books` insists on). Caches page lookups in
`shelve/`, the same caches `check_books` reads.

### `scripts/organizations_geocode.py`

Adds map coordinates to `organizations.yaml`: every `location`,
`israel_office` and `former_location` gets a `<field>_geo` block right after
it (`place`, the prose reduced to one city; `lat`/`lon` in WGS84 decimal
degrees), resolved through Nominatim (OpenStreetMap) at one request per
second. Lookups are cached in `shelve/nominatim_geocode.json`, so a re-run
after adding an organization only resolves the new places; existing `_geo`
blocks survive unless `--force`. Edits the yaml textually (the file is
hand-wrapped, no dumper round-trips it), so the diff is only the new blocks.
Places with no city (`unknown, Israel`) get no block.

### `scripts/organizations_pick_geo.py`

Interactive: chooses the one map point per organization from the `_geo`
blocks the geocoder wrote, and records it as a `geo` block (`from`, `place`,
`lat`, `lon`) just before the item's `sources`. Organizations whose points
all fall on one spot are decided silently; the rest prompt with every
distinct spot and the prose behind it, the Israel office suggested first.
The file is saved after each answer, so `q` or Ctrl-C loses nothing and the
next run resumes. `--auto` takes every suggestion, `--force` asks again.

### `scripts/podcasts_add_podcast.py`

Interactive: search the iTunes Search API, pick a result, and append the
podcast to `podcasts.yaml`.

### `scripts/podcasts_add_chapters.py`

Appends the next N episodes (default 10) of a podcast to its chapters from
the RSS feed, continuing from where the last run stopped.

### `scripts/podcasts_backfill_rss.py`

Fills in missing `rss_feed` URLs in `podcasts.yaml` by looking each podcast
up on the iTunes Search API.

### `scripts/podcasts_backfill_rss_data.py`

Backfills RSS metadata (description, pubDate, duration, enclosure, …) into
existing chapters by matching titles against the feed.

### `scripts/podcasts_fill_chapter_names.py`

Replaces numeric chapter titles with the real episode data from the feed;
non-numeric titles are left alone.

### `scripts/youtube_add_names.py`

Fetches the title for every item without a `name` in a YouTube YAML file
(`video_youtube.yaml`) and writes it back in place.
