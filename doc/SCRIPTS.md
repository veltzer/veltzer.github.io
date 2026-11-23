# Scripts Reference

## Build Scripts

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

## Image Fetch Scripts

All image scripts are incremental — they skip images that already exist.
Use `--force` to re-download.

### `scripts/fetch_museum_images.py`

Downloads museum images via DuckDuckGo image search with tkinter GUI picker.
Searches for `"{name} museum {city}"`.
Output: `static/images/museum-{internal_id}.jpg`

## Shared Modules

### `scripts/image_picker.py`

Shared module used by the museum image script.
Provides DuckDuckGo image search (with candidates cached under
`$XDG_CACHE_HOME/veltzer-site/image-picker/`, defaulting to
`~/.cache/veltzer-site/image-picker/`, so they survive a reboot) and a
tkinter image browser GUI with prev/next/select/skip/quit.

### `scripts/image_standard.py`

One place that decides how large an image in `static/images/` may be
(`800x384>`, JPEG, EXIF stripped) and the `normalise()` function the fetchers
call on save. The numbers were derived from the card geometry of the data
collection app (removed 2026-11-23); the module docstring explains the arithmetic.

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

Verifies every museum and concert has its image in `static/images/`. (The
films and series, with their poster fetchers, live in My World now.) Part of the build
(`[processor.explicit.generic.check_images]` in `rsconstruct.toml`, which
reruns when any image is added, changed or deleted): an
item added without its image fails it, so run the matching `fetch_*.py`.

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
