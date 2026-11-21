# Scripts Reference

## Build Scripts

### `scripts/build_site.py`

The one build step around rssite, run by `rsconstruct build` as a processor
(see `rsconstruct.toml`; a real build goes through the build system -- see
`CLAUDE.md`). rssite itself is rsconstruct's
`processor.mass_generator.generic.site`: `rssite plan` lists every file a
build writes with its sources, and each is cached separately.

- `companies` writes the organization tabs' data, seven files in
  `_site/data/`, and copies `data/logos/*.svg` to `_site/logos/`.
  `scripts/import_companies.py`, once per `--function` of
  `organizations.yaml`, writes `companies.json.gz` (taught at),
  `training_providers.json.gz` (taught for), `consulting.json.gz`
  (consulted for), `publishers.json.gz` (the media page's publishers),
  `education.json.gz` (studied at) and `certifiers.json.gz` (certified by);
  `scripts/import_certifications.py` joins `certifications.yaml` with the
  issuers into `certifications.json.gz` (one entry per certification). The
  stanza in `rsconstruct.toml` names all seven outputs; every map image the
  YAML names must exist under `static/images/`.

Everything else that used to be a step here is the generator's own now: the
commit every footer names is the `git` context variable; the root language
chooser is `templates/root.html`; the sitemap and the feeds are built in; and
the shared-themes files are published by the `[[publish]]` entry.

### `scripts/make_post_cards.py`

Draws the share card (`og:image`, 1200x630) of every blog post: the author
line, the post's title at the largest size that fits four lines, its tags,
and `veltzer.org`, right to left for Hebrew. Run by rsconstruct as
`processor.generator.generic.post_cards`, in batch mode with
`<post.md> <card.jpg>` pairs: `content/blog/2026-04-28-euthyphro-dilemma.en.md` becomes
`_site/images/og/2026-04-28-euthyphro-dilemma.en.jpg`, which `templates/base.html` names. The cards
are build output, not committed, so each is redrawn when its post changes.
Needs Pillow (whose wheel bundles libraqm), the system's libfribidi and
Liberation Sans (`fonts-liberation`), all declared in `rsconstruct.toml`.

### `scripts/make_og_images.py`

Draws the two site-wide share cards, `static/images/og/card-{en,he}.jpg`,
used by every page that is not a blog post. Run by hand after changing
`home_title` or the colours; the JPEGs are committed. `make_post_cards.py`
imports its layout constants, so the two kinds of card match. Both paste
the logo from `make_logo.py`.

### `scripts/make_logo.py`

The one definition of the site's logo (a shell prompt on an accent tile, on
a 64x64 grid), and the writer of the icon files drawn from it:
`static/favicon.svg`, `static/favicon.ico` (16/32/48 px) and
`static/apple-touch-icon.png` (180 px). Run by hand after changing the mark,
then run `make_og_images.py`; all of these are committed. The header's
inline copy in `templates/base.html` is checked against it by
`tests/test_logo.py`.

## check_redirects.py

Asks the deployed site whether its host redirects and sitemap are sound:
each of the three non-canonical host variants (http, www) must 301 once to
`https://veltzer.org/`, and the sitemap must list real pages only. Exits
non-zero on any failure.

Not part of the build -- it talks to the network and tests the deployment,
not the tree. Run it after a deploy, or when Search Console reports an
indexing problem, to tell a regression here from Google's own crawl timing.
It deliberately cannot read a validation verdict: that is behind a Google
login; `check_indexing.py` below reads the per-page state through the API.

## check_indexing.py

Compares what Google has indexed with what the live sitemap lists, and
prints the pages that are not indexed, grouped by Google's reason
(*Discovered - currently not indexed*, *Crawled - currently not indexed*,
...). Google has no call that lists every indexed URL, so it works in two
steps: one Search Analytics request for every page that appeared in a search
result in the last `--days` days (shown means indexed), then one URL
Inspection request for each page that step did not settle. Inspection is
slow, about seven seconds a page against a quota of 2000 a day, so a page
found indexed is remembered in `~/.cache/veltzer.github.io/indexed.json` for
`--max-age` days and a later run inspects only new pages and the ones still
waiting. `--no-inspect` runs the first step alone.

It authenticates as the gcloud application-default login, which must carry
the Search Console scope, and the Search Console API must be enabled on the
quota project (`veltzer-calendar-id`). The one-time commands are in the
script's docstring. No key is stored anywhere.

Not part of the build -- it talks to the network and reports Google's state,
not the tree's. It covers this site's sitemap only; the domain property's
other reasons (404, redirect, the other repositories' pages) are still read
in the Search Console UI, see `doc/SEO.md`.

### `scripts/export_posts_for_ai.py`

Mirrors every blog post (`content/blog/*.{en,he}.md`, front matter included,
the section's `_index` files left out) into `~/insync/for_ai/blog`, which Insync
syncs to Google Drive, so AI agents with access to the Drive can read them.
Only changed posts are copied again, and a `.md` there with no post behind it
(renamed or deleted) is removed; other files are never touched, except the
temporary files a killed run leaves behind. Because it deletes, it only works in
a directory holding its `.export_posts_for_ai` marker; one without it is adopted
only if it is empty or holds nothing but post files, and refused otherwise.
`--dest` picks another directory. The build runs it (the `export_posts_for_ai`
stanza) whenever a post changes, but only on a machine where the destination
exists (`enabled_if_dir_exists`); elsewhere the build reports it as skipped.
One gap: reverting a post to a state already built does not rerun it (the
cache matches the old state), so run the script by hand after a revert.

### `scripts/import_teaching.py`

Imports the three sibling teaching sites (`../teaching-slides`,
`../teaching-syllabi`, `../teaching-animations`) into
`content/{slides,syllabi,animations}/_index.en.md` as native site pages. Each
sibling builds a single self-contained `_site/index.html`; the script strips
the document wrapper, drops the embedded header and theme `<select>` (this
site's chrome supplies both), drops the inlined `@font-face` rules (this site
links the same shared-themes fonts), scopes the page's CSS under an `#app-<section>`
wrapper, and writes the result with this site's front matter. A manual step,
run after rebuilding a sibling site; the output is committed, and the build
(local and CI, which has no sibling checkouts) uses the committed copies. `--check` reports what would be written without writing.
The Hebrew `_index.he.md` stubs are hand-written and are not touched.

### `scripts/gen_profiles.py`

Renders `data/yaml/profiles.yaml` into the region between the
`<!-- BEGIN generated profiles -->` markers in `content/about/_index.en.md`
and `_index.he.md` (contact line, intro, link groups and extras, in both
languages), and writes `data/identity.toml`, the `sameAs` URLs the
`Person` JSON-LD in `templates/base.html` reads. A manual step whose
output is committed. Run it after editing `profiles.yaml` and commit.

### `scripts/make_word_vectors.py`

Writes the word vectors behind the blog search's semantic mode into
`static/data/vectors/`: from the newest release of
[veltzer/embeddings](https://github.com/veltzer/embeddings) (downloaded once
into `download/embeddings/<tag>/`, 160 MB per language), the 10,000 most
frequent words plus every word a post uses, as int8 rows with a float32 scale
per row (~6 MB English, ~11 MB Hebrew). Checks that the release's tokenizer
version is the one it and `static/blog-search.js` implement. A manual step,
and the output is committed; the browser builds the post vectors itself, so
rerun it only for a new release or once new posts have brought many new words.

### `scripts/copy_data.py`

Builds `static/data/` from the media YAML in `data/yaml/`: copies the
plain files, runs the books import, converts every
YAML file to JSON (the frontend reads JSON, not YAML) and gzips everything.
Uses `gzip -n` for reproducible output. Validates source files exist before
copying. A manual step, not part of the build; the generated `static/data/`
is committed.

## Image Fetch Scripts

All image scripts are incremental — they skip images that already exist.
Use `--force` to re-download.

The poster fetchers (`fetch_movie_posters.py`, `fetch_series_posters.py`) read
the built `static/data/video_features.json.gz` and `video_series.json.gz`, not
the YAML. A video added to `data/yaml/` is therefore skipped until
`scripts/copy_data.py` has rebuilt those files: run `copy_data.py` first.

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

Flattens `data/yaml/books_read.yaml` (names, authors, ownings and
readings, each a list per language) into one item per book for the media
page: `name`, `authors`, `rating`/`last_read`/`review` of the latest dated
reading, `readings`, `owned_languages`, `cover`, `url`. Run by
`scripts/copy_data.py`.

### `scripts/fetch_museum_images.py`

Downloads museum images via DuckDuckGo image search with tkinter GUI picker.
Searches for `"{name} museum {city}"`.
Output: `static/images/museum-{internal_id}.jpg`

## Shared Modules

### `scripts/image_picker.py`

Shared module used by the museum and audio course image scripts.
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
`data-collection-app.js`; the module docstring explains the arithmetic.

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
record the aspell quirks in detail. Why aspell and not rsconstruct's built-in
zspell checker is in `doc/DECISIONS.md`.

### `scripts/spellcheck_en.sh`, `scripts/spellcheck_he.sh`

Run `aspell list` over the blog posts of one language with the compiled
allowlist as an extra dictionary, and fail on any misspelled word. Run by
`rsconstruct build` over `content/blog/*.en.md` and `*.he.md`. The compiled
dictionary is a `dep_inputs` of the check in `rsconstruct.toml`, so rsconstruct
builds it first, on a cold build and after every edit of the word list.

## Validation Scripts

### `scripts/check_hebrew.py`

Checks that the Hebrew feeds and share cards carry no untranslated text. Run
by rsconstruct as three instances: `hebrew_posts` over the `.he.md` posts
(`title` and `description` contain Hebrew, and so does every tag not in the
script's `LATIN_TAGS`, the technical names that stay as they are),
`hebrew_strings` over `i18n/he.toml` (`home_title`, the name on the cards)
and `hebrew_feeds` over every built `_site/he/**/atom.xml` (the feed's
title, each entry's title and each author name). "Contains Hebrew" is one
Hebrew letter, so a title that mixes in a product name passes. The bodies
of the posts are not checked here.

### `scripts/check_post_names.py`

Checks that every blog post is named `<date>-<slug>.<lang>.md` after its own
front matter, and that its `slug` is at most four lowercase ASCII words
joined by `-`. Run by rsconstruct as `processor.checker.script.post_names`
over `content/blog/` (the `_index` files excluded). Because rssite pairs
translations by file name, checking each file alone also keeps the
languages' `date` and `slug` equal. The rule is in `CLAUDE.md` under "Blog
Posts".

### `scripts/check_images.py`

Verifies every media item has a corresponding image in `static/images/`.
Checks movies, series, audio courses, museums, concerts
and books. Part of the build
(`[processor.explicit.generic.check_images]` in `rsconstruct.toml`, which
reruns when any image is added, changed or deleted): a media
item added without its image fails it, so run the matching `fetch_*.py`.

### `scripts/import_companies.py`

Picks the organizations with one `--function` (`teaching`,
`training-provider`, `consulting`, `publisher`, `education` or
`certification`; `TABS` in the script) among their `functions` out of
`data/yaml/organizations.yaml`, trims each to the fields the companies tab
shows (name, logo, status, headquarters, Israel office, the one `geo` map
point and the path of its static map image, website, logo attribution) and
gives each a `review` line: what happened to it, or its status when nothing
did. Writes gzipped JSON with a fixed mtime. Unlike the other importers this
is a build step: `build_site.py companies` runs it once per tab and writes
the `_site/data/*.json.gz` named under `build_site.py` above, and copies `data/logos/*.svg` to
`_site/logos/` next to it. Nothing is committed. With `--images-dir` (the
build passes `static/images/`) it fails when a company's map image has not
been rendered by `organizations_fetch_maps.py`.

### `scripts/check_wikidata_ids.py`

Run by rsconstruct as `processor.checker.script.wikidata_ids` over the video
yaml files. Fails when an entry has no `wikidata_id` or `rotten_tomatoes_id`,
or when the Wikidata id is not the item whose IMDb id is the entry's
`imdb_id`, or the Rotten Tomatoes id is neither the item's nor the
hand-verified one. Reads only `shelve/wikidata_imdb.json` and
`data/rotten_tomatoes_manual.json`, so it never uses the network; the fix for
a new entry is to run `videos_fetch_wikidata.py`.

### `scripts/import_certifications.py`

Builds the certifications tab of the education page: one card per
certification in `data/yaml/certifications.yaml`, joined with the issuing
organization's name, logo, website and status from `organizations.yaml`.
Fails when a certification names an organization that does not exist or one
whose `functions` lack `certification`. Run by `build_site.py companies`, which
writes `_site/data/certifications.json.gz`.

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

## Tailwind

### `scripts/build_collection_css.sh`

Compiles the data collection app's Tailwind stylesheet:
`config/tailwind.collection.config.js` and `config/tailwind.collection.css`
become `static/vendor/tailwind-collection.css` (minified), through
`npx tailwindcss@3`. It is run by hand, needs node, and its output is
committed, so the build itself needs no node. Run it after adding a Tailwind
class to the app or to a plugin: a class the scan has not seen has no rule.

## Local Preview

### `scripts/serve.py`

Serves `_site/` with a plain static server, which is the closest local
approximation to GitHub Pages (`rssite serve` rebuilds on change but skips
the steps around rssite). It does not build: run `rsconstruct build` first,
and it refuses to start when `_site/` is missing. Options: `--port`,
`--preview` (open a browser), `--anonymous` (a browser with a fresh temp
profile, implies `--preview`).

## API Key Management

### `scripts/manage_api_key.py`

Manages a Google API key. Commands: `show`, `restrict`, `create`,
`delete`, `rotate`. Reads/writes the key via `pass`. The `rotate` command
creates a new key, writes it into `static/keys.js` (for the calendar key;
any other `--pass-path` leaves the file alone), waits for rebuild/deploy,
then stores the new key in `pass` and deletes the old one.
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
blocks survive unless `--force`, which also reports a block whose place no
longer resolves. An entry in the script's `OVERRIDES` wins over the cache, so
adding one fixes a place that was cached as unresolved. Edits the yaml textually (the file is
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

### `scripts/organizations_fetch_maps.py`

Renders the static map image each company card shows: for every
organization shown on any tab (not only the teaching ones; `import_companies.shown`)
its `geo` point, an 800x320 JPEG of OpenStreetMap tiles at zoom
13 with a pin on the point, written to `static/images/map-<lat>_<lon>.jpg`
(one file per distinct point, named by `import_companies.map_path`, so
companies on the same city centroid share one image and the duplicate-image
check stays happy). Tiles are fetched paced with a real User-Agent, as the
OSM tile policy asks, and cached under `out/osm_tiles/` (gitignored), so a
re-run fetches nothing. Existing images are skipped unless `--force`. Run
it after adding an organization or changing its point: the build fails
(`import_companies.py --images-dir`) when an image is missing. The images
are committed. Why a static image and not a Google Maps iframe is in
`doc/DECISIONS.md`.

### `scripts/videos_fetch_wikidata.py`

Fills `wikidata_id` and `rotten_tomatoes_id` into `video_series.yaml` and
`video_features.yaml` from each entry's `imdb_id`. Asks the Wikidata Query
Service which item has that IMDb id (P345) and takes the item's Rotten
Tomatoes path (P1258), or the hand-verified path in
`data/rotten_tomatoes_manual.json` when Wikidata has none (`null` there means
Rotten Tomatoes has no page). Lookups are cached in
`shelve/wikidata_imdb.json` (committed); only what is not cached is queried.
The yaml is edited textually so its hand formatting survives. `--dry-run`
reports without writing.
