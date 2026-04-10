# Design Decisions and Known Issues

## Calendar pages are kept separate intentionally
The three calendar pages (`calendar_full.html`, `calendar_list_view.html`,
`calendar_google_embed.html`) exist to evaluate which approach is best.
Only `calendar_full.html` is linked in navigation. The others remain on
disk for comparison but are not user-facing.

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
The API key is restricted by HTTP referrer (`veltzer.github.io/*`) and
limited to the Calendar API only. Google designed browser API keys to be
public — the restrictions prevent misuse. The key is stored in `pass`
and injected at build time via `keys.js.mako` template.

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
