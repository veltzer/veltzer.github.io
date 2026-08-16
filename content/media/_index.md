+++
title = "Media Collection"
template = "embed.html"

[extra]
hide_title = true
+++
<script src="https://cdn.tailwindcss.com"></script>
<script>
// The media tracker's markup uses Tailwind colour utilities (bg-white,
// text-gray-500, text-blue-600 and so on), which are fixed colours and so
// ignored the site theme. Rather than rewrite two dozen classes across the
// plugins, the palette itself is redefined in terms of the theme tokens: every
// existing utility then resolves to a var() and follows the theme switcher.
//
// The scale is mapped by role, not by lightness -- 50/100/200 are the surface
// steps, 500+ are text -- so the same class means the same thing in a light or
// a dark theme instead of inverting.
tailwind.config = {
important: '#media-root',
corePlugins: { preflight: false },
theme: {
  extend: {
    colors: {
      white: 'var(--bg)',
      black: 'var(--text-primary)',
      gray: {
        50: 'var(--bg-surface)',
        100: 'var(--bg-surface)',
        200: 'var(--bg-elevated)',
        300: 'var(--border)',
        400: 'var(--text-muted)',
        500: 'var(--text-secondary)',
        600: 'var(--text-secondary)',
        700: 'var(--text-primary)',
        800: 'var(--text-primary)',
        900: 'var(--text-primary)'
      },
      blue: {
        50: 'var(--bg-surface)',
        100: 'var(--bg-elevated)',
        400: 'var(--accent)',
        500: 'var(--accent)',
        600: 'var(--accent)',
        700: 'var(--accent)',
        800: 'var(--accent)'
      },
      red: {
        100: 'var(--bg-surface)',
        400: 'var(--danger, #dc2626)',
        600: 'var(--danger, #dc2626)',
        700: 'var(--danger, #dc2626)'
      },
      green: {
        100: 'var(--bg-surface)',
        600: 'var(--success, #16a34a)',
        700: 'var(--success, #16a34a)'
      }
    }
  }
}
};
</script>

<style>
#media-root {
font-family: Inter, Heebo, sans-serif;
}
#media-root .stat-card { text-align: center; }
#media-root .stat-value { font-size: 1.875rem; font-weight: 700; color: var(--accent); }
#media-root .stat-label { font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem; }

/* Tailwind's preflight is disabled here (it would restyle the whole site), so
   form controls keep the browser defaults -- a white input on a dark theme.
   Give them the theme tokens explicitly. */
#media-root input,
#media-root select,
#media-root textarea {
    background: var(--bg-surface);
    color: var(--text-primary);
    border-color: var(--border);
}
#media-root input::placeholder { color: var(--text-muted); }
</style>
<style id="toggle-styles"></style>

<div id="media-root" class="antialiased" style="font-family: Inter, Heebo, sans-serif;">
<div class="max-w-6xl mx-auto px-4 my-12">

<header class="text-center mb-10">
<h1 id="page-title" class="text-4xl font-bold"></h1>
<p id="page-subtitle" class="text-lg text-gray-500 mt-2"></p>
</header>

<nav id="main-nav" class="flex flex-wrap justify-center gap-2 mb-10"></nav>

<div id="search-container" class="mb-10 mx-auto max-w-xl">
<input type="text" id="search-input" placeholder="Search..." aria-label="Search media collection"
class="w-full px-5 py-3 text-lg border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500">
<div class="flex justify-center items-center gap-2 mt-3">
<label for="sort-field" class="text-sm text-gray-500">Sort by:</label>
<select id="sort-field" class="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"></select>
<button id="sort-order-btn" class="text-sm px-3 py-1 border border-gray-300 rounded hover:bg-gray-100" title="Toggle sort order" aria-label="Toggle sort order"></button>
<button id="filters-toggle-btn" class="text-sm px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 ml-2" aria-label="Toggle filters and options" aria-expanded="false"></button>
</div>
<div id="filters-panel" class="hidden mt-3 p-4 bg-gray-50 border border-gray-200 rounded-lg">
<div id="filters-container" class="flex flex-wrap justify-center gap-2"></div>
<div id="toggles-container" class="flex flex-wrap justify-center gap-3 mt-3"></div>
</div>
</div>

<div id="status-message" class="text-center text-gray-500 text-lg"></div>

<main id="content-container">
<section id="stats-container" class="mb-10"></section>
<section id="items-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></section>
<nav id="pagination-container" class="flex justify-center items-center gap-3 mt-4 mb-3" style="display:none!important;"></nav>
</main>

</div>

<footer class="text-center text-gray-500 mt-12 py-4 border-t border-gray-200">
<p>Page Visits: <span id="visitor-count">Loading...</span></p>
</footer>
</div>

<script>
window.mediaFeatureFlags = {
showPeople: false,
};
</script>

<script src="../keys.js"></script>
<script src="../media-utils.js"></script>
<script>
window.mediaBasePath = '../';
</script>
<script src="../media-app.js"></script>
