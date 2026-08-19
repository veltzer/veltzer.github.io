# JavaScript and CSS Toolkits

What this site loads in the browser, where, and why. Rewritten 2026-08-19 after
the previous version went stale: it predated the zola migration and tabulated
seven standalone pages, five of which no longer exist.

Verified against the working tree rather than from memory. If you change a
dependency, change this file in the same commit -- a stale inventory is worse
than none, because it gets trusted.

## The short version

There is no single framework. Four app pages each load what they need, and the
blog loads nothing at all.

| Page | CSS | JS libraries |
|------|-----|--------------|
| `/en/media/` | Tailwind (CDN) | none -- plain JS in `static/media-app.js` + seven plugins |
| `/en/chess/` | site stylesheet | chess.js, cm-chessboard -- both **vendored**, not CDN |
| `/en/calendar/` | site stylesheet | FullCalendar 6.1.20 + its Google Calendar plugin (CDN) |
| `/en/slides/`, `/en/syllabi/`, `/en/animations/` | site stylesheet | Material Web 2 (CDN) |
| Blog posts, About, tags | site stylesheet (`sass/style.scss`) | none |

## CSS

### Tailwind, on one page only

`content/media/_index.md` loads Tailwind from `https://cdn.tailwindcss.com` in
JIT mode.

**It is the only page that does.** The previous version of this file claimed
Tailwind was "the sole CSS framework for all custom standalone pages"; that was
true when there were seven standalone pages, and is not true now. Everything
else uses the site's own stylesheet, compiled from `sass/style.scss`.

Keeping Tailwind for the media app is deliberate. The card grid, filter row and
stat tiles are utility-class layouts that would have to be rewritten to move
off it, and the CDN's JIT mode ships only the classes the page actually uses.

The rest of the site does not need it, and adding it to `base.html` would put a
render-blocking CDN request on all ~690 built pages to serve a handful of
classes.

### The site stylesheet

`sass/style.scss`, compiled by zola. Colours come from the `shared-themes`
submodule (`static/shared-themes/themes.css`), copied in at build time by
`scripts/build_site.py`. That copy is why editing `static/shared-themes/`
directly is pointless -- it is overwritten on every build, and the submodule is
the source of truth.

## JavaScript libraries

### Material Web 2 -- slides, syllabi, animations

```text
https://cdn.jsdelivr.net/npm/@material/web@2/all.js/+esm
```

Three of the four app sections import it as an ES module. It supplies the
filter chips, buttons and cards those pages use.

Not pinned to a patch version, and loaded with no SRI hash. Both are worth
knowing about; neither is currently a problem, since the pages degrade to
unstyled-but-working elements if the CDN fails.

### FullCalendar 6.1.20 -- calendar

```text
https://cdn.jsdelivr.net/npm/fullcalendar@6.1.20/index.global.min.js
https://cdn.jsdelivr.net/npm/@fullcalendar/google-calendar@6.1.20/index.global.min.js
```

Pinned, and **the only CDN dependency on the site carrying SRI integrity
hashes.** The Google Calendar plugin reads a public API key from
`static/keys.js`; that key is public by design and referrer-restricted, see
`doc/DECISIONS.md`.

### chess.js and cm-chessboard -- chess

**Vendored, not loaded from a CDN**: `static/vendor/chess.min.js` and
`static/vendor/cm-chessboard/`.

cm-chessboard 8.x is ESM-only with relative imports, which is why it is a local
copy imported as a module rather than a script tag:

```js
import {Chessboard, FEN} from "/vendor/cm-chessboard/src/Chessboard.js";
```

### What is no longer used

- **js-yaml** -- removed. The media app reads JSON, not YAML: parsing the 6.5 MB
  YouTube file with js-yaml took ~399 ms in the browser. The only mention left in
  `static/media-app.js` is the comment recording that decision.
- **Bootstrap** -- removed before the zola migration, in favour of Tailwind on the
  media page.
- **elasticlunr / `search_index.en.js`** -- zola still generates a 4.1 MB search
  index for English (`build_search_index = true` in `config.toml`), and **nothing
  loads it.** The only search on the site is the media app's, which filters its
  own JSON client-side. Either wire up a search UI or turn the flag off.

## Media plugin filter system

Each plugin in `static/plugin-*.js` declares a `fields` registry. Filters are
*derived* from it by `deriveFieldsConfig` in `static/media-app.js` rather than
hand-declared, so adding a field to a plugin gives you its filter for free.

`filterable` defaults to true; every plugin marks exactly one field
`filterable: false` -- the title, which the search box already covers.

| Type | Description | Example |
|------|-------------|---------|
| `select` | Dropdown of unique field values | Device, City, Channel |
| `year` | Years extracted from a date field | Year Watched, Year Added |
| `boolean` | Yes/No toggle | Has Chapters |
| `range` | Numeric buckets, `{label, min, max}` | Duration (Short/Medium/Long) |
| `custom` | Plugin supplies `value(item)` and `match(item, val)` | Status (Finished/In Progress) |

Filters combine with the search box using AND.

### Adding one

```js
fields: [
    {field: 'device', label: 'Device', type: 'select'},
    {field: 'date_utcz', label: 'Year', type: 'year'},
    {field: 'duration', label: 'Duration', type: 'range',
        value: function(item) { return item.duration || 0; },
        ranges: [
            {label: 'Short (< 5 min)', min: 0, max: 300},
            {label: 'Long (5+ min)', min: 300, max: null}
        ]
    }
]
```

## Standalone HTML in `static/`

Four files, and only two are real pages:

| File | What it is |
|------|-----------|
| `media_app.html` | The media app outside the site chrome |
| `calendar_app.html` | The calendar outside the site chrome |
| `chess.html` | **A redirect stub.** The viewer moved to `/en/chess/`; this survives because `/chess.html` was linked from the old nav and may be bookmarked |
| `full_index.html` | Index linking to the standalone pages |

The app sections are language-prefixed (`/en/chess/`, not `/chess/`) now that
they have Hebrew versions, which is why the redirect points where it does.
