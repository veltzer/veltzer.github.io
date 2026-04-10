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
    window.mediaPluginFiles = {
        'audio_courses': '../plugin-audio-courses.js',
        'audible': '../plugin-audible.js',
        'features': '../plugin-movies.js',
        'museums': '../plugin-museums.js',
        'podcasts': '../plugin-podcasts.js',
        'series': '../plugin-series.js',
        'youtube': '../plugin-youtube.js'
    };
    window.mediaPlugins = window.mediaPlugins || {};

    function loadPlugin(key) {
        if (window.mediaPlugins[key]) return Promise.resolve();
        const src = window.mediaPluginFiles[key];
        if (!src) return Promise.reject(new Error('Unknown plugin: ' + key));
        return new Promise(function(resolve, reject) {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = function() { reject(new Error('Failed to load ' + src)); };
            document.head.appendChild(script);
        });
    }

    function loadAllPlugins() {
        return Promise.all(Object.keys(window.mediaPluginFiles).map(loadPlugin));
    }

    function deriveFieldsConfig(plugin) {
        if (!plugin.fields) return;
        if (!plugin.sortFields) {
            plugin.sortFields = plugin.fields
                .filter(function(f) { return f.sortable !== false; })
                .map(function(f) {
                    var sf = {field: f.field, label: f.label, type: f.type || 'string'};
                    if (f.value) sf.value = f.value;
                    return sf;
                });
        }
        if (!plugin.filters) {
            plugin.filters = plugin.fields
                .filter(function(f) { return f.filterable !== false; })
                .map(function(f) {
                    var ff = {field: f.field, label: f.label, type: f.filterType || 'select'};
                    if (f.value) ff.value = f.value;
                    if (f.ranges) ff.ranges = f.ranges;
                    if (f.extractValues) ff.extractValues = f.extractValues;
                    if (f.match) ff.match = f.match;
                    return ff;
                });
        }
    }
</script>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const itemsContainer = document.getElementById('items-container');
        const searchContainer = document.getElementById('search-container');
        const searchInput = document.getElementById('search-input');
        const statusMessage = document.getElementById('status-message');
        const pageTitle = document.getElementById('page-title');
        const pageSubtitle = document.getElementById('page-subtitle');
        const mainNav = document.getElementById('main-nav');
        const statsContainer = document.getElementById('stats-container');

        let allItems = [];
        let activeConfig = {};
        let currentPage = 1;
        let currentFilteredItems = [];
        const PAGE_SIZE = 50;
        const paginationContainer = document.getElementById('pagination-container');
        const sortFieldSelect = document.getElementById('sort-field');
        const sortOrderBtn = document.getElementById('sort-order-btn');
        let currentSortField = '';
        let currentSortType = 'string';
        let currentSortOrder = 'asc';
        let currentSortValueFn = null;
        const filtersContainer = document.getElementById('filters-container');
        const togglesContainer = document.getElementById('toggles-container');
        const toggleStyles = document.getElementById('toggle-styles');
        const filtersPanel = document.getElementById('filters-panel');
        const filtersToggleBtn = document.getElementById('filters-toggle-btn');
        let activeFilters = {};
        let activeToggles = {};

        function escapeHtml(str) {
            if (str === null || str === undefined) return '';
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
        }
        window.escapeHtml = escapeHtml;

        function formatDate(dateString) {
            if (!dateString) return null;
            return dateString.substring(0, 10);
        }

        function sortItems(items) {
            items.sort(function(a, b) {
                let va = currentSortValueFn ? currentSortValueFn(a) : a[currentSortField];
                let vb = currentSortValueFn ? currentSortValueFn(b) : b[currentSortField];
                if (va === null || va === undefined) va = currentSortType === 'number' ? 0 : '';
                if (vb === null || vb === undefined) vb = currentSortType === 'number' ? 0 : '';
                let result;
                if (currentSortType === 'number') {
                    result = Number(va) - Number(vb);
                } else {
                    result = String(va).localeCompare(String(vb));
                }
                return currentSortOrder === 'asc' ? result : -result;
            });
        }

        function updateSortOrderBtn() {
            sortOrderBtn.textContent = currentSortOrder === 'asc' ? '\u2191 Asc' : '\u2193 Desc';
        }

        function findSortFieldConfig(fieldName) {
            const fields = activeConfig.sortFields || [];
            for (let i = 0; i < fields.length; i++) {
                if (fields[i].field === fieldName) return fields[i];
            }
            return null;
        }

        function applySortFieldConfig(fieldName) {
            currentSortField = fieldName;
            const sf = findSortFieldConfig(fieldName);
            currentSortType = sf ? (sf.type || 'string') : 'string';
            currentSortValueFn = sf && sf.value ? sf.value : null;
        }

        function getSortPrefKey(dataType) {
            return 'mediaSortPref_' + dataType;
        }

        function saveSortPref(dataType) {
            try {
                localStorage.setItem(getSortPrefKey(dataType), JSON.stringify({
                    field: currentSortField,
                    order: currentSortOrder
                }));
            } catch (e) { /* ignore */ }
        }

        function loadSortPref(dataType) {
            try {
                const saved = localStorage.getItem(getSortPrefKey(dataType));
                return saved ? JSON.parse(saved) : null;
            } catch (e) { return null; }
        }

        function setupSortUI() {
            const fields = activeConfig.sortFields || [];
            const defaultSort = activeConfig.defaultSort || {field: 'name', order: 'asc'};
            const urlParams = new URLSearchParams(window.location.search);
            const dataType = urlParams.get('data') || Object.keys(dataSources)[0];
            const savedPref = loadSortPref(dataType);
            sortFieldSelect.innerHTML = '';
            fields.forEach(function(sf) {
                const opt = document.createElement('option');
                opt.value = sf.field;
                opt.textContent = sf.label;
                opt.dataset.type = sf.type || 'string';
                sortFieldSelect.appendChild(opt);
            });
            let sortField = defaultSort.field;
            let sortOrder = defaultSort.order || 'asc';
            if (savedPref && findSortFieldConfig(savedPref.field)) {
                sortField = savedPref.field;
                sortOrder = savedPref.order || sortOrder;
            }
            currentSortOrder = sortOrder;
            sortFieldSelect.value = sortField;
            applySortFieldConfig(sortField);
            updateSortOrderBtn();
        }

        function setupFilters() {
            filtersContainer.innerHTML = '';
            activeFilters = {};
            const filters = activeConfig.filters || [];
            if (filters.length === 0) {
                filtersContainer.style.display = 'none';
                return;
            }
            filtersContainer.style.display = 'flex';

            filters.forEach(function(filter) {
                const values = extractFilterValues(filter);
                if (values.length === 0) return;

                const select = document.createElement('select');
                select.className = 'text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500';
                select.setAttribute('aria-label', 'Filter by ' + filter.label);
                select.dataset.filterField = filter.field;
                select.dataset.filterType = filter.type;

                const defaultOpt = document.createElement('option');
                defaultOpt.value = '';
                defaultOpt.textContent = filter.label + ': All';
                select.appendChild(defaultOpt);

                values.forEach(function(val) {
                    const opt = document.createElement('option');
                    opt.value = val;
                    opt.textContent = val;
                    select.appendChild(opt);
                });

                select.addEventListener('change', function() {
                    if (select.value) {
                        activeFilters[filter.field] = {value: select.value, type: filter.type, valueFn: filter.value};
                    } else {
                        delete activeFilters[filter.field];
                    }
                    updateFiltersBtnText();
                    applyFilterSortRender();
                });

                filtersContainer.appendChild(select);
            });
        }

        function extractFilterValues(filter) {
            const valueSet = new Set();
            allItems.forEach(function(item) {
                if (filter.extractValues) {
                    const vals = filter.extractValues(item);
                    if (vals) vals.forEach(function(v) { if (v != null && v !== '') valueSet.add(String(v)); });
                    return;
                }
                let val;
                if (filter.type === 'year') {
                    const raw = filter.value ? filter.value(item) : item[filter.field];
                    if (raw) {
                        val = String(raw).substring(0, 4);
                        if (/^\d{4}$/.test(val)) valueSet.add(val);
                    }
                } else if (filter.type === 'boolean') {
                } else if (filter.type === 'range') {
                } else if (filter.type === 'custom' && filter.value) {
                    val = filter.value(item);
                    if (val != null && val !== '') valueSet.add(String(val));
                } else {
                    val = filter.value ? filter.value(item) : item[filter.field];
                    if (val != null && val !== '') valueSet.add(String(val));
                }
            });

            if (filter.type === 'boolean') {
                return ['Yes', 'No'];
            }
            if (filter.type === 'range' && filter.ranges) {
                return filter.ranges.map(function(r) { return r.label; });
            }

            const sorted = Array.from(valueSet);
            if (filter.type === 'year') {
                sorted.sort().reverse();
            } else {
                sorted.sort();
            }
            return sorted;
        }

        function applyFilters(items) {
            const filterKeys = Object.keys(activeFilters);
            if (filterKeys.length === 0) return items;

            return items.filter(function(item) {
                return filterKeys.every(function(field) {
                    const f = activeFilters[field];
                    const filterConfig = (activeConfig.filters || []).find(function(fc) { return fc.field === field; });
                    if (!filterConfig) return true;

                    if (filterConfig.type === 'year') {
                        const raw = filterConfig.value ? filterConfig.value(item) : item[field];
                        if (!raw) return false;
                        return String(raw).substring(0, 4) === f.value;
                    }
                    if (filterConfig.type === 'boolean') {
                        const boolVal = filterConfig.value ? filterConfig.value(item) : item[field];
                        if (f.value === 'Yes') return !!boolVal;
                        return !boolVal;
                    }
                    if (filterConfig.type === 'range' && filterConfig.ranges) {
                        const numVal = filterConfig.value ? filterConfig.value(item) : Number(item[field]);
                        const range = filterConfig.ranges.find(function(r) { return r.label === f.value; });
                        if (!range) return true;
                        if (range.min != null && numVal < range.min) return false;
                        if (range.max != null && numVal >= range.max) return false;
                        return true;
                    }
                    if (filterConfig.type === 'custom' && filterConfig.match) {
                        return filterConfig.match(item, f.value);
                    }
                    const val = filterConfig.value ? filterConfig.value(item) : item[field];
                    return String(val) === f.value;
                });
            });
        }

        function getTogglePrefKey(dataType) {
            return 'mediaTogglePref_' + dataType;
        }

        function loadTogglePref(dataType) {
            try {
                var saved = localStorage.getItem(getTogglePrefKey(dataType));
                return saved ? JSON.parse(saved) : null;
            } catch (e) { return null; }
        }

        function saveTogglePref(dataType) {
            try {
                localStorage.setItem(getTogglePrefKey(dataType), JSON.stringify(activeToggles));
            } catch (e) { /* ignore */ }
        }

        function applyToggleStyles() {
            var css = '';
            Object.keys(activeToggles).forEach(function(key) {
                if (key === '_images') {
                    if (!activeToggles[key]) {
                        css += '.media-card-image { display: none; }\n';
                    }
                } else if (!activeToggles[key]) {
                    css += 'li[data-toggle="' + key + '"] { display: none; }\n';
                }
            });
            toggleStyles.textContent = css;
        }

        function setupToggles() {
            togglesContainer.innerHTML = '';
            activeToggles = {};
            var fields = (activeConfig.toggleFields || []).slice();
            if (activeConfig.renderImage) {
                fields.unshift({key: '_images', label: 'Images', default: true});
            }
            if (fields.length === 0) {
                togglesContainer.style.display = 'none';
                toggleStyles.textContent = '';
                return;
            }
            togglesContainer.style.display = 'flex';

            var urlParams = new URLSearchParams(window.location.search);
            var dataType = urlParams.get('data') || Object.keys(dataSources)[0];
            var saved = loadTogglePref(dataType);

            fields.forEach(function(tf) {
                var isOn = saved && saved.hasOwnProperty(tf.key) ? saved[tf.key] : tf.default;
                activeToggles[tf.key] = isOn;

                var label = document.createElement('label');
                label.className = 'inline-flex items-center gap-1 text-sm text-gray-600 cursor-pointer select-none';
                var cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.checked = isOn;
                cb.className = 'rounded border-gray-300 text-blue-600 focus:ring-blue-500';
                cb.addEventListener('change', function() {
                    activeToggles[tf.key] = cb.checked;
                    saveTogglePref(dataType);
                    applyToggleStyles();
                });
                label.appendChild(cb);
                label.appendChild(document.createTextNode(' ' + tf.label));
                togglesContainer.appendChild(label);
            });

            applyToggleStyles();
        }

        function updateFiltersBtnText() {
            const activeCount = Object.keys(activeFilters).length;
            const label = activeCount > 0 ? 'Filters (' + activeCount + ')' : 'Filters';
            const arrow = filtersPanel.classList.contains('hidden') ? '\u25BC' : '\u25B2';
            filtersToggleBtn.textContent = label + ' ' + arrow;
            filtersToggleBtn.setAttribute('aria-expanded', !filtersPanel.classList.contains('hidden'));
        }

        filtersToggleBtn.addEventListener('click', function() {
            filtersPanel.classList.toggle('hidden');
            updateFiltersBtnText();
        });

        const dataSources = window.mediaPlugins || {};

        function generateNav(activeDataType, showStatsOnly) {
            mainNav.innerHTML = '';
            for (const [key, config] of Object.entries(dataSources)) {
                const navLink = document.createElement('a');
                navLink.href = '?data=' + key;
                navLink.textContent = config.navTitle;
                navLink.className = 'px-4 py-2 rounded-full text-sm font-medium no-underline transition-colors';
                if (key === activeDataType) {
                    navLink.classList.add('bg-blue-600', 'text-white');
                } else {
                    navLink.classList.add('bg-gray-200', 'text-gray-700', 'hover:bg-gray-300');
                }
                navLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(key, false);
                });
                mainNav.appendChild(navLink);
            }

            const statsToggle = document.createElement('a');
            statsToggle.className = 'px-4 py-2 rounded-full text-sm font-medium no-underline border border-gray-300 ml-4 transition-colors';

            if (showStatsOnly) {
                statsToggle.textContent = '\u2190 Back to Full View';
                statsToggle.classList.add('text-gray-700', 'hover:bg-gray-100');
                statsToggle.href = '?data=' + activeDataType;
                statsToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(activeDataType, false);
                });
            } else {
                statsToggle.textContent = 'View Statistics';
                statsToggle.classList.add('text-gray-700', 'hover:bg-gray-100');
                statsToggle.href = '?data=' + activeDataType + '&stats=true';
                statsToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(activeDataType, true);
                });
            }
            mainNav.appendChild(statsToggle);
        }

        function switchView(dataType, showStats) {
            const params = new URLSearchParams();
            params.set('data', dataType);
            if (showStats) params.set('stats', 'true');
            history.pushState(null, '', '?' + params.toString());
            loadData();
        }

        window.addEventListener('popstate', function() {
            loadData();
        });

        async function loadData() {
            const urlParams = new URLSearchParams(window.location.search);
            const dataType = urlParams.get('data') || Object.keys(dataSources)[0];
            const showStatsOnly = urlParams.get('stats') === 'true';
            activeConfig = dataSources[dataType];
            if (activeConfig) deriveFieldsConfig(activeConfig);

            if (!activeConfig) {
                statusMessage.innerHTML = '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">Error: Invalid data type in URL or plugins not loaded.</div>';
                return;
            }

            generateNav(dataType, showStatsOnly);

            searchInput.value = '';
            currentPage = 1;
            pageTitle.textContent = activeConfig.title;
            pageSubtitle.textContent = showStatsOnly ? 'Statistics Overview' : activeConfig.subtitle;
            searchInput.placeholder = activeConfig.searchPlaceholder;
            document.title = activeConfig.title;

            if (showStatsOnly) {
                searchContainer.style.display = 'none';
                itemsContainer.style.display = 'none';
                statsContainer.style.display = 'block';
            } else {
                searchContainer.style.display = 'block';
                itemsContainer.style.display = 'grid';
                statsContainer.style.display = 'none';
            }

            try {
                statusMessage.textContent = 'Loading ' + activeConfig.title + '...';
                const response = await fetch('../data/' + activeConfig.file.replace(/^data\//, ''));

                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status + ". Make sure '" + activeConfig.file + "' is accessible.");
                }

                let yamlText;
                if (activeConfig.file.endsWith('.gz') && typeof DecompressionStream !== 'undefined') {
                    const ds = new DecompressionStream('gzip');
                    const decompressed = response.body.pipeThrough(ds);
                    yamlText = await new Response(decompressed).text();
                } else if (activeConfig.file.endsWith('.gz')) {
                    const fallbackUrl = '../data/' + activeConfig.file.replace(/^data\//, '').replace(/\.gz$/, '');
                    const fallbackResponse = await fetch(fallbackUrl);
                    if (!fallbackResponse.ok) {
                        throw new Error('Browser does not support DecompressionStream and uncompressed file not available.');
                    }
                    yamlText = await fallbackResponse.text();
                } else {
                    yamlText = await response.text();
                }
                const data = jsyaml.load(yamlText);
                allItems = (data.items || []).filter(item => item.status !== 'missing').map(item => {
                    if (item.title && typeof item.name === 'undefined') {
                        item.name = item.title;
                    }
                    return item;
                });
                setupSortUI();
                setupFilters();
                setupToggles();
                filtersPanel.classList.add('hidden');
                updateFiltersBtnText();
                sortItems(allItems);

                if (showStatsOnly) {
                    statsContainer.innerHTML = activeConfig.renderStats(allItems);
                } else {
                    renderItems(allItems);
                }
                statusMessage.textContent = '';

            } catch (error) {
                console.error('Error loading or parsing YAML file:', error);
                itemsContainer.innerHTML = '';
                statsContainer.innerHTML = '';
                statusMessage.innerHTML = '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"><strong>Loading Failed:</strong> ' + escapeHtml(error.message) + '</div>';
            }
        }

        function renderItems(itemList) {
            currentFilteredItems = itemList;
            itemsContainer.innerHTML = '';

            if (itemList.length === 0) {
                statusMessage.textContent = 'No items found matching your search.';
                paginationContainer.style.cssText = 'display:none!important';
                return;
            }

            statusMessage.textContent = '';
            const totalPages = Math.ceil(itemList.length / PAGE_SIZE);
            if (currentPage > totalPages) currentPage = totalPages;
            const start = (currentPage - 1) * PAGE_SIZE;
            const pageItems = itemList.slice(start, start + PAGE_SIZE);

            pageItems.forEach(item => {
                const col = document.createElement('div');

                const specificDetails = activeConfig.renderDetails(item);

                var rawImgUrl = activeConfig.renderImage ? activeConfig.renderImage(item) : '';
                const imgUrl = rawImgUrl && !rawImgUrl.startsWith('http') ? '../' + rawImgUrl : rawImgUrl;
                const imgHtml = imgUrl ? '<img src="' + escapeHtml(imgUrl) + '" class="media-card-image w-full h-48 object-cover" alt="' + escapeHtml(item.name || '') + '" loading="lazy">' : '';

                col.innerHTML =
                    '<div class="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col overflow-hidden">' +
                        imgHtml +
                        '<div class="p-4 flex flex-col flex-1">' +
                            '<h5 class="text-lg font-bold mb-2">' + escapeHtml(item.name || 'No Title') + '</h5>' +
                            '<p class="text-gray-600 mb-4">' + escapeHtml(item.review || item.subtitle || 'No description.') + '</p>' +
                            '<ul class="mt-auto divide-y divide-gray-200">' +
                                (activeConfig.ratingScale ? '<li class="py-2"><strong>Rating:</strong> <span class="inline-block bg-blue-600 text-white text-sm font-semibold px-2.5 py-0.5 rounded-full">' + escapeHtml(item.rating || '?') + ' / ' + activeConfig.ratingScale + '</span></li>' : '') +
                                (item.device ? '<li class="py-2"><strong>Device:</strong> ' + escapeHtml(item.device) + '</li>' : '') +
                                specificDetails +
                            '</ul>' +
                        '</div>' +
                    '</div>';
                itemsContainer.appendChild(col);
            });

            renderPagination(totalPages, itemList.length);
        }

        function renderPagination(totalPages, totalItems) {
            if (totalPages <= 1) {
                paginationContainer.style.cssText = 'display:none!important';
                return;
            }
            paginationContainer.style.cssText = '';

            const start = (currentPage - 1) * PAGE_SIZE + 1;
            const end = Math.min(currentPage * PAGE_SIZE, totalItems);

            paginationContainer.innerHTML =
                '<button id="btnPrevPage" aria-label="Previous page" class="px-4 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50">&laquo; Previous</button>' +
                '<span class="text-gray-500">Showing ' + start + '–' + end + ' of ' + totalItems + '</span>' +
                '<div class="flex items-center gap-2">' +
                    '<label for="jumpToPage" class="text-sm text-gray-500">Page</label>' +
                    '<input type="number" id="jumpToPage" aria-label="Jump to page" class="w-20 text-sm border border-gray-300 rounded px-2 py-1" min="1" max="' + totalPages + '" value="' + currentPage + '">' +
                    '<span class="text-gray-500">/ ' + totalPages + '</span>' +
                '</div>' +
                '<button id="btnNextPage" aria-label="Next page" class="px-4 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50">Next &raquo;</button>';

            document.getElementById('btnPrevPage').disabled = currentPage <= 1;
            document.getElementById('btnNextPage').disabled = currentPage >= totalPages;

            document.getElementById('btnPrevPage').addEventListener('click', () => {
                if (currentPage > 1) { currentPage--; renderItems(currentFilteredItems); window.scrollTo(0, 0); }
            });
            document.getElementById('btnNextPage').addEventListener('click', () => {
                if (currentPage < totalPages) { currentPage++; renderItems(currentFilteredItems); window.scrollTo(0, 0); }
            });
            document.getElementById('jumpToPage').addEventListener('change', (e) => {
                const page = parseInt(e.target.value, 10);
                if (Number.isNaN(page) || page < 1 || page > totalPages) { e.target.value = currentPage; }
                else { currentPage = page; renderItems(currentFilteredItems); window.scrollTo(0, 0); }
            });
            document.getElementById('jumpToPage').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.target.dispatchEvent(new Event('change')); }
            });
        }

        function getFilteredItems() {
            let items = allItems.slice();
            items = applyFilters(items);
            const searchTerm = searchInput.value.toLowerCase().trim();
            if (searchTerm) {
                items = items.filter(function(item) {
                    return activeConfig.searchFields.some(function(field) {
                        const fieldValue = item[field];
                        if (!fieldValue) return false;
                        return fieldValue.toString().toLowerCase().includes(searchTerm);
                    });
                });
            }
            return items;
        }

        function applyFilterSortRender() {
            const items = getFilteredItems();
            sortItems(items);
            currentPage = 1;
            renderItems(items);
        }

        searchInput.addEventListener('input', applyFilterSortRender);

        function getCurrentDataType() {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get('data') || Object.keys(dataSources)[0];
        }

        sortFieldSelect.addEventListener('change', function() {
            applySortFieldConfig(sortFieldSelect.value);
            saveSortPref(getCurrentDataType());
            applyFilterSortRender();
        });

        sortOrderBtn.addEventListener('click', function() {
            currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            updateSortOrderBtn();
            saveSortPref(getCurrentDataType());
            applyFilterSortRender();
        });

        function updateVisitorCount() {
            const namespace = window.location.hostname || 'local-file-viewer';
            const key = 'main-viewer-counter';
            const apiUrl = 'https://api.counterapi.dev/v1/' + namespace + '/' + key + '/up';

            fetch(apiUrl)
            .then(function(response) {
                if (!response.ok) throw new Error('Counter API error: ' + response.status);
                return response.json();
            })
            .then(function(data) {
                const countElement = document.getElementById('visitor-count');
                if (countElement) {
                    countElement.textContent = data.count;
                }
            })
            .catch(function(error) {
                console.error('Error fetching visitor count:', error);
                const countElement = document.getElementById('visitor-count');
                if (countElement) {
                    countElement.textContent = 'N/A';
                }
            });
        }

        loadAllPlugins().then(loadData);
        updateVisitorCount();
    });
</script>
