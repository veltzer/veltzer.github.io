+++
title = "Media Collection"
description = "What Mark Veltzer has read, watched and listened to: books, audiobooks, audio courses, movies, series, podcasts, museums and YouTube, with ratings and notes; and the companies he has taught at."
template = "embed.html"
+++

<!-- The Tailwind utilities the media app uses, compiled ahead of time with
     the theme-token palette in config/tailwind.media.config.js; rebuild with
     scripts/build_media_css.sh after adding a class. -->
<link rel="stylesheet" href="/vendor/tailwind-media.css">

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

/* Card image box, rendered by media-app.js. A fixed 2:1 landscape box; the
   image inside covers it unless the plugin asked for contain, in which case
   the whole image is shown and a blurred, enlarged copy of it fills the bands
   either side. The backdrop is scaled up so the blur does not fade to
   transparent at the edges. */
#media-root .media-card-image {
    position: relative;
    height: 12rem;
    overflow: hidden;
    background: var(--bg-surface);
}
#media-root .media-card-image img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
#media-root .media-card-img { position: relative; }
#media-root .media-card-image--contain .media-card-img { object-fit: contain; }
#media-root .media-card-backdrop {
    position: absolute;
    inset: 0;
    transform: scale(1.2);
    filter: blur(14px) saturate(0.8);
    opacity: 0.6;
}
/* Company logos: dark marks on a transparent canvas, drawn for a white page.
   The one place on the site with a fixed colour, deliberately: a logo box
   that followed a dark theme would swallow half the logos. The padding
   keeps the 6% canvas margin from looking cramped in the 2:1 box. */
#media-root .media-card-image--light {
    background: #fff;
    padding: 0.75rem;
}
/* The static map image on a company card (plugin-companies.js): a short
   landscape strip, 800x320 rendered for a box about 400x160, above the
   "on Google Maps" link and the OpenStreetMap credit. */
#media-root .media-card-map {
    display: block;
    width: 100%;
    height: 10rem;
    object-fit: cover;
    margin-bottom: 0.5rem;
    border-radius: 0.375rem;
    background: var(--bg-surface);
}
#media-root .media-card-map-credit {
    display: block;
    font-size: 0.75rem;
    color: var(--text-muted);
}
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

</div>

<script>
window.mediaFeatureFlags = {
showPeople: false,
};
</script>

<script src="/media-utils.js"></script>
<script>
// Absolute, not '../': the plugins and data live at the site root, and a
// relative path only reached them while English was served there. From
// /en/media/ it would resolve to /en/.
window.mediaBasePath = '/';
</script>
<script src="/media-app.js"></script>
