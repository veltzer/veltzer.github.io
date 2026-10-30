# JavaScript and CSS Toolkits

What this site loads in the browser, where, and why. Rewritten 2026-08-19 after
the previous version went stale: it predated the zola migration and tabulated
seven standalone pages, five of which no longer exist.

Verified against the working tree rather than from memory. If you change a
dependency, change this file in the same commit -- a stale inventory is worse
than none, because it gets trusted.

## The short version

There is no single framework. The app pages each load what they need, and the
blog loads nothing at all.

| Page | CSS | JS libraries |
|------|-----|--------------|
| `/en/media/` | Tailwind (compiled, vendored) | none -- plain JS in `static/media-app.js` + eight plugins |
| `/en/chess/` | site stylesheet | chess.js, cm-chessboard -- both **vendored**, not CDN |
| `/en/calendar/` | site stylesheet | FullCalendar 6.1.20 + its Google Calendar plugin -- **vendored** |
| `/en/slides/`, `/en/syllabi/`, `/en/animations/` | site stylesheet | Material Web 2 (CDN) |
| Blog posts, About, tags | site stylesheet (`sass/style.scss`) | none |

## CSS

### Tailwind, on one page only

`content/media/_index.en.md` links `static/vendor/tailwind-media.css`: the
utilities the media app uses, compiled with Tailwind 3 by
`scripts/build_media_css.sh` from `config/tailwind.media.config.js` (the
theme-token palette) and committed. Until 2026-10-29 the page loaded Tailwind's
in-browser compiler from `https://cdn.tailwindcss.com`, which Tailwind says is
not for production: a render-blocking third-party script that compiled the CSS
on every visit.

Tailwind finds classes by scanning the files the config lists for whole class
names. A class added to the media app or a plugin has no rule until the script
is rerun, and a class assembled at run time (`'bg-' + colour`) is never found;
write class names out in full.

**It is the only page that does.** The previous version of this file claimed
Tailwind was "the sole CSS framework for all custom standalone pages"; that was
true when there were seven standalone pages, and is not true now. Everything
else uses the site's own stylesheet, compiled from `sass/style.scss`.

Keeping Tailwind for the media app is deliberate. The card grid, filter row and
stat tiles are utility-class layouts that would have to be rewritten to move
off it, and the compiled file holds only the classes the app uses (about 9 KB).

The rest of the site does not need it, and adding it to `base.html` would put a
render-blocking stylesheet on all ~630 built pages to serve a handful of
classes.

### The site stylesheet

`sass/style.scss`, compiled by zola. Colours come from the `shared-themes`
submodule (`shared/shared-themes/`), copied to `_site/shared-themes/` at build
time by `scripts/build_site.py shared-themes`. The submodule is the source of
truth; the copy is build output.

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

**Vendored** since 2026-10-29: `static/vendor/fullcalendar/` holds the two
files the jsDelivr URLs served
(`fullcalendar@6.1.20/index.global.min.js` and
`@fullcalendar/google-calendar@6.1.20/index.global.min.js`), verified byte for
byte against the SRI hashes the page used to carry, and the MIT licence. To
upgrade, download the new version's two files into that directory and change
the version here. The Google Calendar plugin reads a public API key from
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
- **elasticlunr / `search_index.en.js`** -- gone. Under zola it was switched off
  (the 4.1 MB index was generated and deployed on every build and nothing ever
  loaded it). The blog search replaced it: `[search]` in `rssite.toml` writes
  `<lang>/search.json` (title, opening text, tags and full text of every post,
  ~800 KB gzipped per language), and `static/blog-search.js` on the
  blog index fetches it on first use and matches every query word as a
  substring, case- and diacritic-insensitive, so Hebrew needs no stemmer. The
  other search boxes are per-page filters over each page's own data: the media
  app, chess, slides, syllabi and animations.

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

None. The standalone apps were replaced by the templated sections on
2026-08-18 and kept as redirect stubs until 2026-10-28, when every legacy
redirect was removed (see `doc/DECISIONS.md`).
