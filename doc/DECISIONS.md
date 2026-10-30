# Design Decisions and Known Issues

## Calendar: the comparison is over, FullCalendar won

Three standalone calendar pages once existed side by side to evaluate which
approach was best: `calendar_full.html` (FullCalendar), `calendar_list_view.html`
(a raw Google Calendar API fetch rendered as a list) and
`calendar_google_embed.html` (Google's own iframe embed). Only the first was ever
linked; the other two stayed on disk for comparison.

That evaluation has concluded. The FullCalendar approach is now the real page at
`content/calendar/_index.en.md`, served at `/en/calendar/` and `/he/calendar/` with
month, week and day views, and `calendar_full.html` is gone -- superseded by it.

The two losing alternatives were deleted on 2026-08-18. They had become
unreachable when `full_index.html`, the only thing that linked them, was replaced
with a redirect, and keeping two unlinked implementations of a question already
answered was not worth the maintenance: both still carried live code against
`keys.js` and the Calendar API. Their history is in git if the comparison ever
needs revisiting.

`static/calendar_app.html` remained as a redirect to `/en/calendar/` until the
legacy redirects were all removed on 2026-10-28 (see the end of this file).

## No `<noscript>` fallback needed

The site is JavaScript-dependent by design. All target users have JS enabled.

## Favicon is consistent across all pages

All pages use `<link rel="icon" href="/favicon.svg">`.

## YouTube thumbnails are loaded from CDN, not stored locally

Unlike other media types, YouTube thumbnails are fetched at runtime from
`i.ytimg.com` by the plugin's `renderImage`. Downloading ~30,000 images
locally would add 1-2GB to the git repo and slow every build. The current
approach is correct and intentional.

## Google Calendar API key is intentionally public

The API key is restricted by HTTP referrer (`veltzer.github.io/*`, and the
custom domain `veltzer.org/*`) and limited to the Calendar API only. Google
designed browser API keys to be public — the restrictions prevent misuse.
The key is stored in `pass` (see `scripts/manage_api_key.py`, which reads and
rotates it there) and committed verbatim in `static/keys.js`, which the
calendar page loads directly. There is no build-time injection.

### Why not hide the key behind an edge proxy (Cloudflare Worker etc.)?

The question was raised of moving the key server-side — e.g. a Cloudflare
Worker (sometimes mis-remembered as a "CloudFront worker"; CloudFront is
AWS's CDN, the edge-function product you'd want there is Lambda@Edge) that
holds the key as a secret and proxies Calendar API requests so clients
never see it. We decided **not** to do this. Reasoning:

- **The key is already restricted**, so a copied key is useless to anyone:
  Google rejects requests whose `Referer` is not one of our domains, and
  the key can only touch the Calendar API (read-only access to *public*
  calendars). It is not billing-bound. There is nothing to abuse.
- **A proxy would hide the string but protect nothing extra.** It only
  changes a cosmetic fact ("the key is readable in page source"), while
  adding an always-on dependency that can break the calendar if it goes
  down or is misconfigured.
- **`CALENDAR_ID` is public regardless.** The iframe embed in
  `calendar_google_embed.html` needs it client-side, and a public
  calendar's ID is inherently exposed. A proxy cannot hide that.
- **Not all consumers can even be proxied cleanly.** Of the three pages:
  `calendar_list_view.html` does a direct `fetch` (proxyable);
  `calendar_app.html` uses FullCalendar's `googleCalendarApiKey` option
  which wants to talk to Google directly (would need rewiring to an
  `events: function(){...}` callback); `calendar_google_embed.html` uses
  no key at all.

  (2026-09-21: of those three pages only the FullCalendar one survives, as
  `content/calendar/_index.en.md`; the other two were deleted, see the
  Calendar section above. The argument stands for the remaining consumer.)

If the key were ever changed to a billing-bound or write-capable
credential, this decision should be revisited — a proxy would then be
warranted. As long as it stays a referrer-restricted, read-only Calendar
browser key, the visible-in-source key is the correct, simplest design.

## Company cards show a static OpenStreetMap image, not a Google Maps iframe

Each card on the companies tab shows a small map of the company's one
`geo` point (chosen in `organizations.yaml`, see `organizations_pick_geo.py`)
above the "on Google Maps" link. The map is a static JPEG rendered once
from OpenStreetMap tiles by `scripts/organizations_fetch_maps.py` and
committed under `static/images/map-<lat>_<lon>.jpg`, one file per distinct
point (88 companies sit on 24 points, since Nominatim puts every company
in a city on the city centroid). The card loads it with `loading="lazy"`
and prints the "© OpenStreetMap contributors" credit its licence asks
for; the link under it still opens the point in Google Maps for the rare
visitor who wants the real thing.

For one day (2026-09-26) the card embedded the classic keyless Google
Maps iframe (`maps.google.com/maps?q=LAT,LON&output=embed`) instead. It
worked, but each frame that scrolled into view loaded a whole maps
application, megabytes of JavaScript and Google cookies, for a map that
is looked at and almost never clicked. The static image costs one lazy
image of roughly 80 KB served from the site, and no third-party request.
The alternatives and why they lost:

- **The Maps Static API** (or the Maps Embed API for the iframe form) is
  the Google-looking version of the same thing. Both need an API key from
  a Google Cloud project with **billing enabled**, and the one key the
  site has (`static/keys.js`) is deliberately restricted to the Calendar
  API. The Static API is metered per image request as well. Extending the
  key means a billing account on the calendar project, or a second
  project and key to rotate and document, for a map that looks much like
  the OSM one. The keyless embed, besides being heavy, has been
  undocumented since the 2013 Maps redesign and could go at any time.
- **Leaflet + OpenStreetMap tiles** needs no key either, but is a tile
  layer's worth of JavaScript and requests per card, for a map nobody
  pans. The rendered image is the same tiles, stitched once.
- **Hotlinking tiles or a third-party static-map service** (Wikimedia's
  Kartotherian, staticmap.openstreetmap.de) would put every page view on
  someone else's server, against OSM's tile usage policy for the former
  and the Wikimedia-projects-only policy for the latter. Fetching the
  tiles once, paced and cached under `out/osm_tiles/`, is what the OSM
  policy allows, and the result is served from here.
- **A single map of all companies** was considered and rejected as a
  different feature: the card is the unit of the media page, and a map
  on the card is what was asked for. It can still be added on top.

The build enforces the invariant: `import_companies.py --images-dir`
fails when a teaching organization's point has no rendered image, so a
new organization or a changed point means running the renderer and
committing the JPEG. The "Map" toggle hides image, link and credit
together for anyone who finds them noisy.

## MkDocs owns `docs/` — manual files go in `blog/`

**Historical (MkDocs era).** There is no `docs/` or `blog/` directory any more:
static files live in `static/`, posts in `content/blog/`, and zola writes to
`_site/`. Kept as a record of the earlier layout.

All static files (HTML, JS, CSS, images, data) live in `blog/` alongside
the Markdown blog posts. MkDocs copies them through as-is to `docs/` on
build. Never edit files in `docs/` directly.

## Some Audible books return 404

A few Audible ASINs return 404 because the publisher removed the book
from the public store. The user still has access in their private library.
The `cover_url` field in the YAML is used instead of scraping the product
page, which avoids this issue for cover images.

## Some Great Courses are not on the website

A few audio courses (Holiday Music, Discovery of Ancient Civilizations,
The Bible and Western Culture, etc.) are not available on
shop.thegreatcourses.com. These use `internal_id` for image naming
and DuckDuckGo image search for cover images.

## MkDocs 2.0 will break Material for MkDocs

**Historical (MkDocs era).** The site no longer uses MkDocs, so this warning
no longer applies; kept as the record of why the upgrade was watched.

The Material for MkDocs team has warned that MkDocs 2.0 will introduce
backward-incompatible changes: all plugins will stop working, all theme
overrides will break, and no migration path exists. Currently on MkDocs
1.6.1 which works fine. Monitor this before upgrading MkDocs.
See: https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/

## Hebrew font: Heebo alongside Inter

The media viewer uses Inter (Google Fonts) for Latin text. Inter has no
Hebrew glyphs, so Hebrew text was falling back to the browser default,
which looked ugly. Added Heebo (a clean, modern Hebrew font from Google
Fonts) as a fallback: `font-family: Inter, Heebo, sans-serif`. Latin
text still uses Inter; Hebrew text uses Heebo.

## Filters and toggles are behind a collapsible panel

### Problem

The media viewer has many filters (rating, year, device, location, etc.)
and toggle checkboxes (images, links, chapters, etc.) per plugin. With
the unified `fields` registry making every field sortable and filterable,
the number of controls grew further. Showing them all inline below the
search bar consumed too much vertical space and pushed the actual content
below the fold.

### Options considered

1. **Collapsible panel** — A "Filters" button next to the sort controls
   that expands/collapses a panel containing all filters and toggles.
2. **Dropdown menu / popover** — A button that opens a floating dropdown.
   More compact but requires click-outside handling, z-index management,
   and can feel awkward on mobile.
3. **Sidebar drawer** — A slide-out panel from the side (like e-commerce
   sites). Heavy UX for a simple media tracker; overkill.
4. **Pill/chip bar** — Show active filters as removable chips with a "+"
   to add more. Elegant but complex to implement and unfamiliar to users.

### Decision

Option 1: collapsible panel. It is the simplest to implement, takes zero
space when collapsed, preserves the existing filter/toggle layout for
users who expand it, and the button shows the active filter count so
users know when filters are applied. The sort controls remain always
visible since they are small and frequently used.

## Post slugs are shared between languages; tag slugs are not

`/en/blog/bayes-theorem-liars/` and `/he/blog/bayes-theorem-liars/` serve the
same post in two languages under the *same* English slug. Tags, by contrast,
are fully translated: `/en/tags/religion/` and `/he/tags/דת/`.

That asymmetry is deliberate.

### Why posts keep a shared slug

Zola derives a post's URL from its filename, and **the filename is also what
pairs a post with its translation**: `foo.en.md` and `foo.he.md` are one post
in two languages precisely because they share a base name. `page.translations`
-- which renders the language switcher on every post page (the current count
is in `[extra.stats]` of `content/blog/_index.en.md`) -- is built from that
pairing.

Giving Hebrew posts Hebrew URLs therefore means one of:

- renaming the Hebrew files, which severs the pairing and kills the language
  switcher on every post; or
- adding an explicit `slug = "..."` to each Hebrew post's front matter, which
  preserves the pairing but adds one hand-maintained key per post that must not
  drift.

Neither buys much. Three further points settled it:

1. The English URLs are already published. Changing them creates a dead URL
   per post unless redirects are left behind for each.
2. Post slugs are long multi-word phrases. Percent-encoded Hebrew turns
   `/he/blog/bayes-theorem-liars/` into a ~200-character URL that is unpleasant
   to share, type or paste into a terminal.
3. An ASCII post slug stays greppable and stable regardless of the reading
   language -- a property worth keeping for URLs that get linked to.

### Why tags are different

Tags are short, reader-facing, and browsed as a list. `/he/tags/` is a page a
Hebrew reader actually reads down, so English words there were plainly wrong in
a way an opaque post URL is not. Tags are also *not* a shared key -- nothing
pairs on them -- so translating them costs nothing structurally.

This needs `[slugify] taxonomies = "safe"` in `config.toml`, scoped to
taxonomies only. Zola's default slugify transliterates rather than strips, so
ארכיאולוגיה would otherwise become `rky-vlvgyh`: unreadable in either language.
`paths` and `anchors` stay on the default so post URLs do not move.

### Consequence to be aware of

Because tags are no longer copied verbatim between a post and its translation,
nothing checks that the two tag sets stay conceptually in step. A Hebrew post
tagged with an English word will not error -- it will quietly create a new
English term under `/he/tags/`. The technology tags that legitimately stay in
latin (today only `mysql`; gpg, ssh, mkdocs and github-pages were translated
since) make that easy to miss.

## No custom JS/HTML minification

**Written in the MkDocs era.** The numbers and the theme references below are
from then; the conclusion still holds, and zola's output is served gzipped by
GitHub Pages the same way.

Investigated adding minification (terser, html-minifier) for custom plugin
JS files (`plugin-*.js`, `media-utils.js`) and HTML files. Decided against
it because:

- GitHub Pages CDN already serves gzip-compressed responses automatically.
- Custom JS files are tiny (~3-4K each, ~27K total); minification would
  save ~10K total — negligible.
- HTML files are 12-20K each, mostly MkDocs boilerplate with minimal savings.
- MkDocs Material theme already minifies its own CSS/JS bundles.
- Data files (YAML, PGN) are already pre-gzipped.
- Adding build tooling for near-zero user-perceived improvement is not
  worth the complexity. If performance becomes a concern, better wins
  would come from lazy-loading images or other optimizations.

## Spellchecking runs on aspell, not rsconstruct's zspell

rsconstruct has a built-in `zspell` checker, and it would replace both
`build_*_dict.sh` / `spellcheck_*.sh` pairs with a few lines of config. It is
not used because it cannot load the Hebrew dictionary.

The `he_IL` hunspell dictionary has 469,509 stems and 3,335 PFX rules; English
(`en_US`) has 79,013 stems and 14 PFX rules -- 6x the stems, 238x the prefix
rules. zspell expands the affix table eagerly when it builds the dictionary
instead of applying prefixes at lookup, so for Hebrew the cross product is on
the order of 1e9 strings. Measured on a 30GB machine it reached 18GB resident
and was still climbing. Narrowing the file set and forcing `max_jobs = 1` did
not help: a single loaded dictionary is the entire cost, so this is not a
parallelism problem. aspell checks the whole blog in ~17MB peak, in under a
second.

English alone would work on zspell. Both languages use aspell anyway, so there
is one spellcheck mechanism to understand rather than two.

The aspell side has its own traps, which is why it runs through scripts
rather than plain commands in `rsconstruct.toml`; each script's header
records them (see also `doc/SCRIPTS.md`):

- every aspell path option resolves relative names against `/usr/lib/aspell`,
  not the working directory, so the scripts compute absolute paths at run time;
- the allowlists (`.aspell.{en,he}.txt`) cannot be passed as `--personal`
  wordlists -- with Hebrew, any non-ASCII entry there segfaults aspell, and for
  English aspell reads that file as Latin-1 whatever `--encoding` says -- so
  they are compiled to `.rws` extra dictionaries under `out/aspell/`.

**When to revisit:** if zspell (rsconstruct pins `zspell = "0.5"`, 0.5.5 as of
2026-10) starts applying affixes lazily at lookup, re-measure loading `he_IL`.
If it fits comfortably in memory, moving both languages to the built-in
checker would delete four scripts.

## The site is built by rssite, not zola (2026-10-16)

zola built the site from 2026-08 to 2026-10. It worked, through a long list of
workarounds that `rssite`'s own documentation records in full (its "Lessons
from zola" chapter was written from this repository): a phantom default
language `cs` so that every real file could carry a language suffix; a
`content/_index.md` that existed only to satisfy the generator; translations
lists whose order changed between builds, so every template looped the config
instead; no translation link between tag pages, patched with a generated table
and a template lookup; `now()` in templates, which no reproducible build can
have; `/page/1/` stubs the sitemap had to be told to hide; the shared design
tokens copied by a script because a sass `@import` of a `.css` file is left
for the browser; and the sibling teaching sites imported by hand because the
layout could not be shared. Every one of those is a design choice in rssite
rather than a workaround here.

### What changed

- `config.toml` is `rssite.toml`; the translations moved from it to
  `i18n/{en,he}.toml`, with the Hebrew month names beside the strings; the
  tag translation table moved from `static/` to `i18n/tags.toml`.
- Every template gets `lang`, `language`, `languages`, `translations` and
  `alternates` from the generator, so `base.html` lost its alt-URL string
  juggling and the tag pages link to their counterpart with no template
  lookup. `page.taxonomies.tags` are objects with a `permalink`. The post
  neighbours are `previous` and `next`.
- The root language chooser is `templates/root.html`; the custom feed and
  sitemap templates are gone, the built-in ones do the same.
- The shared-themes files are published by `[[publish]]` in `rssite.toml`;
  the Python copy step is gone.
- Every page's footer names the generator, its version and the commit it was
  built from ("Made by rssite version ..."). The commit comes from
  `out/build_info.toml`, which is therefore a source of every page: a new
  commit rebuilds the site, which takes seconds.
- The Hebrew app stubs declare `body_from = "en"` instead of the template
  fetching the English section.

### Not preserved

URL compatibility with the zola build was not a goal. One Hebrew tag slug
changed (the geresh in `ג׳אווה` is not a slug character to rssite), the
`/page/1/` stubs are not written, and heading anchors in Hebrew posts are
Hebrew rather than transliterated. The legacy redirects from the MkDocs era
stay as they were.

## No legacy-URL redirects (2026-10-28)

The site is built as if it were made today. Until this date it carried every
earlier generation of URL forward: 30 `[[redirects]]` in `rssite.toml`
(MkDocs-era `/YYYY/MM/DD/<slug>/` permalinks, root-level paths from before
English moved under `/en/`, `/jschess/`, `/ascx/public_key.asc`),
`pager_aliases` for the old `/page/N/` pagers, `feeds.root` serving the
English feed again at `/atom.xml`, and four meta-refresh stubs in `static/`
(`chess.html`, `media_app.html`, `calendar_app.html`, `full_index.html`).
They were kept for Search Console and old bookmarks; the decision is that
those are not worth the configuration, the tests and the check that kept
them alive. All of it was removed, along with `tests/test_legacy_redirects.py`
and the retired-URL half of `scripts/check_redirects.py`, which now checks
only the host redirects and the sitemap. An old URL now gets the 404 page.
`doc/SEO.md` is the history of the Search Console work and still describes
the redirects as they were.

## No "updated" date on posts (2026-10-30)

rssite supports an `updated` front-matter key (shown in the post header,
`dateModified` in the JSON-LD, the feeds' `<updated>`). The site does not
use it, by the author's decision: a post carries the date it was published
and nothing else. Revisions, including the meta descriptions added to every
post on 2026-10-30, do not get a second date. Do not add `updated =` to
posts or render `page.updated` in the templates.

## No series navigation (2026-10-30)

Considered with the blog improvements of 2026-10-30: a `series` taxonomy
with "part N of M" links on runs of related posts (the 2026 religion
sequence, the 2023 direct-democracy posts, the two-part WordPress security
post). Declined by the author. Posts link to each other with `@/` links
where the text calls for it, and `page.related` plus previous/next cover
the rest. Do not reopen it as an improvement.
