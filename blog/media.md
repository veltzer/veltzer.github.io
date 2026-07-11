---
hide:
  - toc
---

# Media Collection

<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
    important: '#media-root',
    corePlugins: { preflight: false }
};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js" integrity="sha384-+pxiN6T7yvpryuJmE1gM9PX7yQit15auDb+ZwwvJOd/4be2Cie5/IuVXgQb/S9du" crossorigin="anonymous"></script>

<style>
#media-root {
    font-family: Inter, Heebo, sans-serif;
}
#media-root .stat-card { text-align: center; }
#media-root .stat-value { font-size: 1.875rem; font-weight: 700; color: #2563eb; }
#media-root .stat-label { font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem; }
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

<script src="../media-utils.js"></script>
<script>
    window.mediaBasePath = '../';
</script>
<script src="../media-app.js"></script>
