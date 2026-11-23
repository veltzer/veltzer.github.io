# Data Collection Plugin Development Guide

This guide explains how to create a new plugin for the data collection app
(`static/data-collection-app.js`), which runs the training data and
education pages.

## Overview

Each plugin is a standalone JavaScript file that registers itself into
`window.collectionPlugins`. A page loads the plugins it lists and renders
their data based on a shared interface.

## File Location

Plugin files go in `static/` and are named `plugin-<name>.js`.

After creating a new plugin, register it in the
`window.collectionPluginRegistry` object in `templates/data_collection.html`:

```javascript
window.collectionPluginRegistry = {
// ... existing plugins ...
'mykey': {{ get_url(path='plugin-myname.js') | json_encode | safe }},
};
```

Write the path as one literal string: `get_url` then names the script by a
hash of its content (`?h=...`), so a reader never runs a cached old plugin
under new HTML, and the build rebuilds the page when the plugin changes. A
computed path gets no hash.

The key must match the key used in `window.collectionPlugins['mykey']` inside
the plugin file. It is also the value of the `?data=` URL parameter that
selects the tab.

Then add the key to the `plugins` list in the front matter of the page that
should show it. Every page using `templates/data_collection.html` hosts the
app, and the template holds the markup and scripts; a page only names its
plugins:

```toml
template = "data_collection.html"

[extra]
plugins = ["education", "certifiers"]    # the first is the default view
```

Today that is two pages (as of 2026-11-23; `grep -l data_collection.html
content/*/_index.en.md content/*/*/_index.en.md` lists them):

- `content/training/data/`: `companies`, over organizations.yaml;
- `content/training/education/`: `education`, `certifiers` and
  `certifications`.

The consulting page (`content/consulting/`, key `consulting`) went to My
World (myworld.stream) on 2026-11-22: the companies I consulted for are
organizations with the relation Consulting there. So did the training
companies I taught for (key `providers`, function `training-provider`), on
2026-11-23: there they have the relation Training provider and the type
Training Company.

A single-plugin page shows no tab row.

One script may register several keys: `plugin-companies.js` registers
`companies` and two copies of it (`education` and
`certifiers`, each with another `file` and titles), all three
keys map to it in `window.collectionPluginRegistry`, and the app loads each file once. A
copy made with `Object.assign` has to be a copy, not the same object under a
second key, because the app writes the derived `sortFields` and `filters`
onto each plugin object.

The Hebrew `_index.he.md` repeats `[extra]`, since front matter is per file.
The nav tabs are sorted by `navTitle`, not by list order.

## Data Files

Plugin data is authored as YAML in `data/yaml/` and loaded by the frontend
as gzipped JSON, never as YAML (see `CLAUDE.md` for why). It is generated at
build time: `scripts/build_site.py companies` runs
`scripts/import_companies.py` once per organization tab and
`scripts/import_certifications.py` once, and writes four files into
`_site/data/` (`companies`,
`education`, `certifiers` and `certifications`, all `.json.gz`) directly,
nothing committed. The YAML structure should be:

```yaml
items:
  - name: "Item Name"
    rating: 8
    # ... other fields
```

## Plugin Interface

Every plugin must register itself on `window.collectionPlugins` with the
following structure:

```javascript
/* global renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

window.collectionPlugins['mykey'] = {
    // --- Required Properties ---

    file: 'data/mydata.json.gz',       // Path to JSON data file (relative to the site root)
    navTitle: 'My Items',              // Short label for the navigation tab
    title: 'My Item Collection',       // Page heading when this plugin is active
    subtitle: 'Description here.',     // Subheading text
    searchPlaceholder: 'Search...',    // Placeholder text for the search input
    searchFields: ['name', 'review'],  // item field names to search against
    defaultSort: {field: 'name', order: 'asc'},  // Initial sort

    // --- Unified Fields Registry ---
    // Each field drives both sorting and filtering automatically.
    // The framework derives sortFields and filters from this array.
    fields: [
        // Simple field — sortable and filterable by select dropdown
        {field: 'name', label: 'Name', type: 'string', filterable: false},

        // Numeric field with select filter
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},

        // Field with computed value — used for both sorting and filtering
        {field: 'date', label: 'Date', type: 'string',
            value: function(item) { return item.date_utcz || ''; },
            filterType: 'year'
        },

        // Range filter with buckets
        {field: 'duration', label: 'Duration', type: 'number',
            filterType: 'range',
            ranges: [
                {label: 'Short (< 1h)', min: 0, max: 60},
                {label: 'Long (1h+)', min: 60, max: null}
            ]
        },

        // Boolean filter (not sortable)
        {field: 'has_review', label: 'Has Review', type: 'string',
            sortable: false, filterType: 'boolean',
            value: function(item) { return item.review && item.review.trim() !== ''; }
        },

        // Custom filter with extractValues for multi-value fields
        {field: 'genres', label: 'Genre', type: 'string',
            sortable: false, filterType: 'custom',
            extractValues: function(item) { return item.genres || []; },
            match: function(item, val) { return item.genres && item.genres.indexOf(val) !== -1; }
        },

        // Custom filter with value/match for computed categories
        {field: 'status', label: 'Status', type: 'string',
            sortable: false, filterType: 'custom',
            value: function(item) { return item.is_done ? 'Done' : 'Pending'; },
            match: function(item, val) { return val === 'Done' ? item.is_done : !item.is_done; }
        }
    ],

    // --- Required Methods ---

    // renderDetails(item) -> HTML string
    // Returns <li> elements with item-specific details for the card view.
    // Use window.escapeHtml() for all user data.
    // Use data-toggle="key" to tie items to toggleFields checkboxes.
    renderDetails: function(item) {
        var html = '';
        if (item.author) {
            html += '<li class="py-2" data-toggle="author"><strong>Author:</strong> '
                  + window.escapeHtml(item.author) + '</li>';
        }
        if (item.url) {
            html += '<li class="py-2" data-toggle="link"><a href="'
                  + window.escapeHtml(item.url)
                  + '" target="_blank" rel="noopener noreferrer"'
                  + ' class="text-blue-600 hover:text-blue-800 underline">'
                  + '&#x1F517; Visit Site</a></li>';
        }
        return html;
    },

    // renderStats(items) -> HTML string
    // Returns full HTML for the statistics view.
    // Use renderBarChart() and renderStatCard() helpers from data-collection-utils.js.
    renderStats: function(items) {
        var counts = {};
        items.forEach(function(item) {
            if (item.category) {
                counts[item.category] = (counts[item.category] || 0) + 1;
            }
        });

        var html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Items') + '</div>';
        html += '</div>';
        html += renderBarChart('By Category', counts, {unit: 'items', sort: 'desc', last: true});
        return html;
    },

    // --- Optional Properties ---

    // prepareItem(item) — called once per loaded item, right after `title`
    // is renamed to `name` and before search, sort, filters and rendering
    // see the item. It mutates the item in place (return value ignored). Use
    // it to derive fields in the page's language from the language-neutral
    // data: the certifications plugin builds `item.subtitle` here with t().
    prepareItem: function(item) {
        item.subtitle = t('mine_line', {name: item.name});
    },

    // sortFields and filters — normally derived from `fields`. A plugin that
    // sets either one explicitly keeps it: the app derives only the ones
    // that are missing. Use it when sorting needs something the unified
    // field cannot say. The certifications plugin gives sortFields so that
    // an undated certification sorts after the dated ones (its `value`
    // returns a high placeholder), while its filters still come from
    // `fields`, where the year filter must not see that placeholder. The
    // shapes are {field, label, type, value?} for a sort field and
    // {field, label, type: <filterType>, value?, ranges?, extractValues?,
    // match?, defaultValue?} for a filter.
    sortFields: [
        {field: 'date', label: 'Date', type: 'string',
            value: function(item) { return item.date || '\uffff'; }}
    ],

    ratingScale: 10,       // If set, shows "Rating: X / <scale>" on cards.
                           // Set to null to hide ratings.

    // toggleFields — checkboxes to show/hide detail sections.
    // An "Images" toggle is auto-added if renderImage is defined.
    toggleFields: [
        {key: 'author', label: 'Author', default: true},
        {key: 'link', label: 'Link', default: true}
    ],

    // renderImage(item, allItems) -> URL string or ''
    // If provided, returns an image URL to display at the top of the card.
    // allItems is the whole loaded dataset, for plugins whose image name
    // depends on other items (one image shared by several entries).
    renderImage: function(item) {
        return item.thumbnail_url || '';
    },

    // imageFit — optional, 'cover' (default) or 'contain'. The card image box
    // is a fixed 2:1 landscape; declare 'contain' when the sources are
    // portrait (book covers, film posters) so they are shown whole over a
    // blurred backdrop instead of being cropped to the middle third.
    imageFit: 'contain',

    // imageBackground — optional, 'light'. With imageFit 'contain', makes the
    // box white in every theme and drops the blurred backdrop. For logos on a
    // transparent canvas, which were drawn for a white page and would vanish
    // against a dark theme's card surface.
    imageBackground: 'light',

    // placeholderImage — optional. When the image renderImage named fails to
    // load (not fetched yet, wrong id), the card swaps in this one instead of
    // showing the browser's broken-image icon. renderImage can also return it
    // directly for an item that has nothing to name an image by.
    placeholderImage: 'images/thing-no-cover.jpg',

    // formatDate — a per-plugin convention, not a framework hook: data-collection-app.js
    // never reads it. Plugins keep it here so renderDetails/renderStats can
    // call this.formatDate; the shared mediaFormatDate utility is the usual value.
    formatDate: mediaFormatDate
};
```

## Field Properties Reference

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `field` | yes | — | Unique identifier for this field |
| `label` | yes | — | Display label in sort/filter dropdowns |
| `type` | no | `'string'` | `'string'` or `'number'` (affects sort comparison) |
| `value` | no | `item[field]` | Function to compute the value from an item |
| `sortable` | no | `true` | Set `false` to exclude from sort dropdown |
| `filterable` | no | `true` | Set `false` to exclude from filter dropdown |
| `filterType` | no | `'select'` | One of: `select`, `boolean`, `year`, `range`, `custom` |
| `ranges` | no | — | Required for `range` filterType. Array of `{label, min, max}` |
| `extractValues` | no | — | For `custom` filterType: extract array of values from item |
| `match` | no | — | For `custom` filterType: `(item, selectedValue) -> boolean` |
| `defaultValue` | no | — | For `select` filters: preselect this option instead of "All" on load, and seed the active filters so the first render is already filtered (the YouTube plugin, since removed, used it for its metadata filter; no plugin does now) |

## Built-in Fields

The data collection app automatically handles these item fields if present:

- `name` (or `title`, which gets renamed to `name`) - displayed as card title
- `review` (or `subtitle`) - displayed as card description
- `rating` - displayed if `ratingScale` is set
- `device` - displayed as "Device: ..." on the card

## Translation

The app is bilingual (English and Hebrew), and no plugin may contain a user
visible English string. Every label, title, unit, link text and fixed
enumeration a plugin shows is a key in the site's own translation files,
`i18n/en.toml` and `i18n/he.toml`, named `app_<plugin>_<name>`, and the
plugin reads it with the global `t()` from `data-collection-utils.js`,
without the `app_` prefix:

```javascript
navTitle: t('books_nav_title'),
html += renderBarChart(t('books_per_year', {undated: undated}), counts, {unit: t('books_unit')});
```

`{name}` placeholders are filled from the second argument; a sentence with a
number in it is one string with a placeholder, never fragments glued around
the number. `templates/data_collection.html` writes every `app_*` key of
`i18n/en.toml` into the page, looking each up in the page's language with
rssite's `trans()`, so a key added to `en.toml` but not `he.toml` fails the
build. The strings are ready before any plugin script loads, so `t()` may be
called while the plugin object is built.

The data itself (titles, names, reviews, genres) is not translated. In a
Hebrew page the app runs right to left: use logical Tailwind spacing
(`ms-*`/`me-*`, not `ml-*`/`mr-*`) and rerun `scripts/build_collection_css.sh`
after adding a class.

## Available Globals

Inside plugin methods you can use:

- `window.escapeHtml(str)` - HTML-escape a string (always use for user data)
- `mediaFormatDate(str)` - shared date formatter (returns `YYYY-MM-DD` or null)
- `renderBarChart(title, counts, options)` - render a bar chart card
- `renderStatCard(value, label)` - render a stat summary card
- `this.formatDate(str)` - call your own formatDate from renderDetails/renderStats

## Statistics Helpers

For `renderStats`, use the shared helpers from `data-collection-utils.js`:

```javascript
// Bar chart with options
renderBarChart('Title', {label: count, ...}, {
    unit: 'items',       // label for counts
    sort: 'desc',        // 'alpha' (default), 'desc' (by count), 'reverse'
    limit: 20,           // max entries to show
    barClass: 'bg-success',  // color class (or cycles through palette)
    last: true           // no bottom margin
});

// Stat card
renderStatCard(42, 'Total Items');
```

The counting and markup every plugin needs live there too; use them rather
than writing the loop again:

- `tally(counts, key)` - add one to `counts[key]` (skips an empty key)
- `countBy(items, keyFn)` - a counts object over `keyFn(item)`
- `yearOf(date)` / `countByYear(items, dateFn)` - the year of a date, and
  items per year
- `sortKeys(keys)` - numeric order when every key is a number, text otherwise

## Existing Plugins

The registry is `window.collectionPluginRegistry` in `templates/data_collection.html`; as of
2026-11-22 it holds these five keys in two files (the films and series,
`plugin-movies.js` and `plugin-series.js`, went to My World that day).

| Key | File | Data |
|-----|------|------|
| `companies` | `plugin-companies.js` | `data/companies.json.gz` (the `teaching` organizations of `organizations.yaml`, written into `_site/` at build time by `scripts/import_companies.py`; their logos are copied from `data/logos/` to `/logos/` the same way) |
| `education` | `plugin-companies.js` | `data/education.json.gz` (function `education`; build-time) |
| `certifiers` | `plugin-companies.js` | `data/certifiers.json.gz` (function `certification`: who certified me; build-time) |
| `certifications` | `plugin-certifications.js` | `data/certifications.json.gz` (one card per certification, `certifications.yaml` joined with the issuers by `scripts/import_certifications.py`; build-time) |
