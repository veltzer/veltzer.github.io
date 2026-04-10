# Completed Improvements

## Calendar Pages

- Iframe URL in `calendar_google_embed.html` now built dynamically from `keys.js`
- Removed placeholder comments and commented-out alternative iframe from `calendar_google_embed.html`
- Updated stale error message in `calendar_list_view.html` to reference `keys.js`
- Upgraded FullCalendar from 5.11.5 to 6.1.20 with separate Google Calendar plugin
- Replaced `alert()` with inline error message div in `calendar_full.html`
- Added `refetchEvents()` auto-refresh every 5 minutes to `calendar_full.html`

## API Key Management

- Added `rotate` command to `manage_api_key.sh` (create new, rebuild, delete old)
- Added `pass` availability check at script startup
- Added empty key guard to `show` and `restrict` commands
- Wrapped `config/calendar.py` API key loading in try/except with clear error message

## Media Page

- Extracted inline CSS to `media.css`
- Lazy-load plugin scripts via `mediaPluginFiles` registry
- Sort preferences saved per data type in localStorage
- Created plugin development guide at `doc/PLUGIN_GUIDE.md`
- Standardized all plugins to `const`/`let` (no more `var`)
- Extracted shared `media-utils.js` with `renderBarChart()` and `renderStatCard()`
- All plugins now use `window.escapeHtml()` consistently in renderStats
- Added `DecompressionStream` fallback for older browsers (tries uncompressed file)
- Added source file validation to `scripts/copy_data.sh`
- Fixed `parseInt` NaN check in jump-to-page input

## Chess/Board Pages

- Added `aria-label` to navigation buttons in `chess.html`
- Added mobile responsive breakpoint for `board.html` (95vw below 480px)

## Security

- Added `rel="noopener noreferrer"` to all `target="_blank"` links in plugins
- Added `noopener,noreferrer` to `window.open()` in calendar.html
- Fixed broken `calendar_full.html` link in `full_index.html` (renamed to `calendar.html`)

## SEO

- Added `<meta name="description">` to all standalone HTML pages
- Moved Google Fonts `@import` from CSS to `<link>` tag with `preconnect` hints in media.html

## Accessibility

- Replaced emoji (📍) with text label in `calendar_list_view.html`
- Added `lang="en"` to `full_index.html`

## General

- Added SRI integrity hashes to CDN resources where supported (js-yaml, FullCalendar, cm-chessboard, chess.js). Tailwind CDN JIT does not support SRI.
- Cleaned up `build_docs.sh` — removed stale commented-out code, added documentation

## Images

- Added `renderImage` to all plugins (movies, series, audible, audio courses, museums, podcasts)
- Movie and series posters downloaded from TMDB with OMDB fallback
- Audible covers downloaded from `cover_url` in YAML
- Audio course images from Great Courses CDN, Audible, or DuckDuckGo picker
- Museum and podcast images via DuckDuckGo picker with tkinter GUI
- Uniform card image height via `object-fit: cover` in `media.css`
- Image check script (`check_images.py`) runs before build
- Reproducible gzip output (`-n` flag) in `copy_data.sh`

## Media Page Navigation

- Plugin switching is instant (no page reload) via `history.pushState`
- Back/forward browser buttons work via `popstate` listener
- "Back to Home" links on all standalone pages

## Data Management

- Added `internal_id` to museums, podcasts, and audio courses without external IDs
- Added `great_courses_id`, `great_courses_slug`, `audible_asin` to audio courses schema
- Added `internal_id` to museums and podcasts schemas
- Validation scripts for unique IDs, lecturer name matching, and image completeness
- Shared `image_picker.py` module for DuckDuckGo search with GUI picker
- Shared `poster_utils.py` module for TMDB/OMDB poster lookup

## Build

- Moved all manual files from `docs/` to `blog/` (MkDocs source)
- MkDocs now owns `docs/` completely — no manual editing needed
- `copy_data.sh` targets `blog/data/` instead of `docs/data/`
- `build_docs.sh` runs image check before `mkdocs build`

## Configuration

- Added `site_description` and `copyright` to `mkdocs.yml`
- Renamed calendar page to `calendar.html`
- Nav simplified: Home, About, Media, Calendar
- Chess and Board hidden from nav (not ready)

## Documentation

- `doc/SCRIPTS.md` — reference for all scripts
- `doc/IMAGES.md` — image naming conventions and workflow
- `doc/PLUGIN_GUIDE.md` — how to create a media plugin
- `doc/DECISIONS.md` — design decisions and known issues
- `doc/DONE.md` — completed improvements
- Removed stale `doc/TODO.txt`
