# Design Decisions and Known Issues

## Calendar: the comparison is over, FullCalendar won

Three standalone calendar pages once existed side by side to evaluate which
approach was best: `calendar_full.html` (FullCalendar), `calendar_list_view.html`
(a raw Google Calendar API fetch rendered as a list) and
`calendar_google_embed.html` (Google's own iframe embed). Only the first was ever
linked; the other two stayed on disk for comparison.

That evaluation has concluded. The FullCalendar approach is now the real page at
`content/calendar/_index.md`, served at `/en/calendar/` and `/he/calendar/` with
month, week and day views, and `calendar_full.html` is gone -- superseded by it.

The two losing alternatives were deleted on 2026-08-18. They had become
unreachable when `full_index.html`, the only thing that linked them, was replaced
with a redirect, and keeping two unlinked implementations of a question already
answered was not worth the maintenance: both still carried live code against
`keys.js` and the Calendar API. Their history is in git if the comparison ever
needs revisiting.

`static/calendar_app.html` remains, as a redirect to `/en/calendar/`.

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
The key is stored in `pass` and injected at build time via `keys.js.mako`
template.

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

If the key were ever changed to a billing-bound or write-capable
credential, this decision should be revisited — a proxy would then be
warranted. As long as it stays a referrer-restricted, read-only Calendar
browser key, the visible-in-source key is the correct, simplest design.

## MkDocs owns `docs/` — manual files go in `blog/`

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
pairs a post with its translation**: `foo.md` and `foo.he.md` are one post in
two languages precisely because they share a base name. `page.translations` --
which renders the language switcher on all 330 post pages (165 per language) --
is built from that pairing.

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
English term under `/he/tags/`. The five technology tags that legitimately stay
in latin (gpg, ssh, mysql, mkdocs, github-pages) make that easy to miss.

## No custom JS/HTML minification

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
