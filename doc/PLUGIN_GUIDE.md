# Media Plugin Development Guide

This guide explains how to create a new media plugin for the media page.

## Overview

Each plugin is a standalone JavaScript file that registers itself into
`window.mediaPlugins`. The media page loads all plugins and renders their
data based on a shared interface.

## File Location

Plugin files go in `blog/` and are named `plugin-<name>.js`.

After creating a new plugin, register it in `blog/media.html` in the
`window.mediaPluginFiles` object:

```javascript
window.mediaPluginFiles = {
    // ... existing plugins ...
    'mykey': 'plugin-myname.js'
};
```

The key must match the key used in `window.mediaPlugins['mykey']` inside
the plugin file.

## Data Files

Plugin data is a YAML file (optionally gzip-compressed) placed in
`blog/data/` (copied from the external `../data/` repo during build).
The YAML structure should be:

```yaml
items:
  - name: "Item Name"
    rating: 8
    # ... other fields
```

## Plugin Interface

Every plugin must register itself on `window.mediaPlugins` with the
following structure:

```javascript
/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['mykey'] = {
    // --- Required Properties ---

    file: 'data/mydata.yaml.gz',       // Path to YAML data file (relative to blog/)
    navTitle: 'My Items',              // Short label for the navigation tab
    title: 'My Item Collection',       // Page heading when this plugin is active
    subtitle: 'Description here.',     // Subheading text
    searchPlaceholder: 'Search...',    // Placeholder text for the search input
    searchFields: ['name', 'review'],  // YAML field names to search against
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
    // Use renderBarChart() and renderStatCard() helpers from media-utils.js.
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

    ratingScale: 10,       // If set, shows "Rating: X / <scale>" on cards.
                           // Set to null to hide ratings.

    // toggleFields — checkboxes to show/hide detail sections.
    // An "Images" toggle is auto-added if renderImage is defined.
    toggleFields: [
        {key: 'author', label: 'Author', default: true},
        {key: 'link', label: 'Link', default: true}
    ],

    // renderImage(item) -> URL string or ''
    // If provided, returns an image URL to display at the top of the card.
    renderImage: function(item) {
        return item.thumbnail_url || '';
    },

    // formatDate — use the shared mediaFormatDate utility
    formatDate: mediaFormatDate
};
```

## Field Properties Reference

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `field` | yes | — | Unique identifier for this field |
| `label` | yes | — | Display label in sort/filter dropdowns |
| `type` | yes | — | `'string'` or `'number'` (affects sort comparison) |
| `value` | no | `item[field]` | Function to compute the value from an item |
| `sortable` | no | `true` | Set `false` to exclude from sort dropdown |
| `filterable` | no | `true` | Set `false` to exclude from filter dropdown |
| `filterType` | no | `'select'` | One of: `select`, `boolean`, `year`, `range`, `custom` |
| `ranges` | no | — | Required for `range` filterType. Array of `{label, min, max}` |
| `extractValues` | no | — | For `custom` filterType: extract array of values from item |
| `match` | no | — | For `custom` filterType: `(item, selectedValue) -> boolean` |

## Built-in Fields

The media page automatically handles these YAML fields if present:

- `name` (or `title`, which gets renamed to `name`) - displayed as card title
- `review` (or `subtitle`) - displayed as card description
- `rating` - displayed if `ratingScale` is set
- `device` - displayed as "Device: ..." on the card

## Available Globals

Inside plugin methods you can use:

- `window.escapeHtml(str)` - HTML-escape a string (always use for user data)
- `window.mediaFeatureFlags.showPeople` - whether to show "With:" people info
- `mediaFormatDate(str)` - shared date formatter (returns `YYYY-MM-DD` or null)
- `renderBarChart(title, counts, options)` - render a bar chart card
- `renderStatCard(value, label)` - render a stat summary card
- `this.formatDate(str)` - call your own formatDate from renderDetails/renderStats

## Statistics Helpers

For `renderStats`, use the shared helpers from `media-utils.js`:

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

## Existing Plugins

| Key | File | Data |
|-----|------|------|
| `audio` | `plugin-audio-courses.js` | `data/audio_courses.yaml.gz` |
| `audible` | `plugin-audible.js` | `data/audible.yaml.gz` |
| `features` | `plugin-movies.js` | `data/video_features.yaml.gz` |
| `museums` | `plugin-museums.js` | `data/museums.yaml.gz` |
| `podcasts` | `plugin-podcasts.js` | `data/podcasts.yaml.gz` |
| `videos` | `plugin-series.js` | `data/video_series.yaml.gz` |
| `youtube` | `plugin-youtube.js` | `data/youtube.yaml.gz` |
