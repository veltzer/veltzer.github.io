# JavaScript Toolkits

## CSS Framework: Tailwind CSS

The site uses **Tailwind CSS** (via CDN JIT mode) as its sole CSS framework for all
custom standalone pages. Bootstrap was removed in favor of Tailwind.

### Why Tailwind over Bootstrap

- **Lighter payload**: Tailwind CDN JIT generates only the classes actually used on
  the page. Bootstrap's CDN ships the entire 227K CSS file regardless of usage.
- **No unused JS**: Bootstrap's JS bundle (~80K) was loaded but none of its interactive
  components (modals, dropdowns, carousels, tooltips) were used.
- **Better fit for utility-first layouts**: The media tracker and chess viewer use
  custom card layouts and controls that benefit from fine-grained utility classes
  rather than opinionated component styles.
- **Single framework**: Using one CSS framework across all pages keeps the codebase
  consistent and reduces the mental overhead of switching between class naming
  conventions.

### Pages using Tailwind

All custom standalone HTML pages use Tailwind:

| Page | Purpose |
|------|---------|
| `media.html` | Media tracker (podcasts, movies, series, books, etc.) |
| `chess.html` | Interactive chess game viewer |
| `board.html` | Minimal chessboard display |
| `calendar.html` | FullCalendar-based interactive calendar |
| `calendar_list_view.html` | Calendar events in list format |
| `calendar_google_embed.html` | Google Calendar iframe embed |
| `full_index.html` | Index page linking to all standalone pages |

### Pages not using Tailwind

| Page | Styling approach |
|------|-----------------|
| Blog posts (Markdown) | MkDocs Material theme (auto-generated) |

### Where Tailwind classes appear

- `blog/media.html` — page structure, navigation, search, filters, pagination, cards, alerts
- `blog/chess.html` — page layout, controls
- `blog/board.html` — page layout
- `blog/calendar.html` — page layout, error display
- `blog/calendar_list_view.html` — page layout, event cards
- `blog/calendar_google_embed.html` — page layout
- `blog/full_index.html` — page layout, links
- `blog/media-utils.js` — shared stat cards, bar chart components
- `blog/plugin-*.js` — item detail lists, stats grid layouts

## Media Plugin Filter System

Each media plugin defines a `filters` array in its config. Filters are rendered as
dropdown selects below the search bar and combine with search using AND logic.

### Filter types

| Type | Description | Example |
|------|-------------|---------|
| `select` | Dropdown populated from unique field values | Device, City, Channel |
| `year` | Dropdown of years extracted from a date field | Year Watched, Year Added |
| `boolean` | Yes/No toggle | Has Chapters |
| `range` | Numeric range buckets with `{label, min, max}` | Duration (Short/Medium/Long) |
| `custom` | Plugin provides `value(item)` and `match(item, val)` functions | Status (Finished/In Progress/Not Started) |

### Filters by plugin

| Plugin | Filters |
|--------|---------|
| Audible | Rating, Status, Year Added, Year Released, Author, Narrator, Genre, Length (range), Part of Series |
| Audio Courses | Rating, Device, Year, Location, Progress, Lecturer, Has Review, Source (Great Courses/Audible/Other) |
| Movies | Rating, Device, Year Watched, Location, Has Review, Watched With Others |
| Museums | Rating, City, Year Visited, Has Review, Has Website, Visited With Others |
| Podcasts | Rating, Has Chapters, Has Review, Has URL |
| Video Series | Rating, Device, Year Watched, Location, Has Review, Seasons Count (range), Completed (Fully Watched/Has Unwatched) |
| YouTube | Category, Channel, Year Uploaded, Duration (range), Views (range) |

### Adding filters to a plugin

Add a `filters` array to the plugin config object:

```js
filters: [
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

## Other JavaScript Libraries

| Library | Used by | Purpose |
|---------|---------|---------|
| js-yaml 4.1.0 | `media.html` | Parse YAML data files in the browser |
| chess.js 0.10.3 | `chess.html` | Chess game logic and PGN parsing |
| cm-chessboard 8.6.0 | `chess.html`, `board.html` | SVG chessboard rendering |
| FullCalendar 6.1.20 | `calendar.html` | Calendar UI |

All libraries are loaded from CDN with SRI integrity hashes where available.
