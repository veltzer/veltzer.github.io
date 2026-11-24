# JavaScript and CSS Toolkits

What this site loads in the browser, where, and why. Rewritten 2026-08-19 after
the previous version went stale: it predated the zola migration and tabulated
seven standalone pages, five of which no longer exist.

Verified against the working tree rather than from memory. If you change a
dependency, change this file in the same commit -- a stale inventory is worse
than none, because it gets trusted.

## The short version

There is no single framework. The calendar loads what it needs, and the
blog loads nothing at all.

| Page | CSS | JS libraries |
|------|-----|--------------|
| `/en/calendar/` | site stylesheet | FullCalendar 6.1.20 + its Google Calendar plugin -- **vendored** |
| Blog posts, About, tags | site stylesheet (`sass/style.scss`) | none |

## CSS

### The site stylesheet

`sass/style.scss`, compiled by rssite. Colours come from the `shared-themes`
submodule (`shared/shared-themes/`), published to `_site/shared-themes/` by the
`[[publish]]` entry in `rssite.toml`. The submodule is the source of
truth; the copy is build output.

## JavaScript libraries

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

### What is no longer used

- **chess.js and cm-chessboard** -- removed on 2026-11-20 with the chess page; the
  games are in the myworld app.
- **js-yaml** -- removed. The data collection app read JSON, not YAML: parsing the 6.5 MB
  YouTube file with js-yaml took ~399 ms in the browser.
- **Tailwind** -- removed on 2026-11-23 with the data collection app (the
  education page, the last that ran it), whose compiled utilities it was; what
  it showed lives in My World (myworld.stream).
- **Bootstrap** -- removed before the zola migration, in favour of Tailwind on the
  data collection pages.
- **elasticlunr / `search_index.en.js`** -- gone. Under zola (the generator before rssite) it was switched off
  (the 4.1 MB index was generated and deployed on every build and nothing ever
  loaded it). The blog search replaced it: `[search]` in `rssite.toml` writes
  `<lang>/search.json` (title, opening text, tags and full text of every post,
  ~800 KB gzipped per language), and `static/blog-search.js` on the
  blog index fetches it on first use. It has three modes (`search_mode` and
  `search_modes` under `[extra]` in `rssite.toml`): two match every query word
  as a substring, case- and diacritic-insensitive so Hebrew needs no stemmer,
  over the titles, opening text and tags or over the full text too; the third
  ranks posts by meaning, with word vectors from
  [veltzer/embeddings](https://github.com/veltzer/embeddings) that
  `scripts/make_word_vectors.py` trims into `static/data/vectors/`.
