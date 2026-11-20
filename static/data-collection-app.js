/*
 * The data collection app: a searchable, sortable, filterable card grid over
 * one JSON file per plugin (static/plugin-*.js).
 *
 * Entry points: every page using templates/data_collection.html -- the media
 * section (/en/media/, /he/media/) and the training section's teaching
 * data page (/en/training/data/, /he/training/data/). The template
 * sets, BEFORE loading this script:
 *
 *   window.collectionBasePath   where plugins and data live ('/')
 *   window.collectionPluginKeys the plugins this page shows, in order
 *   window.collectionPluginRegistry every plugin key and its script's URL
 *
 * There used to be a second copy -- a standalone static/media_app.html carrying its
 * own copy of the page. It was replaced with a redirect on 2026-08-18 (since removed): bypassing
 * templates/base.html meant it silently missed whatever the templates added, and
 * the analytics snippet was the case that surfaced it.
 *
 * Do not fork this file: divergent copies are exactly how the stats count
 * silently drifted before. A new page is a new plugin list, not a new app.
 */
(function () {
    'use strict';

    const BASE_PATH = window.collectionBasePath || './';


    // --- Plugin Registry ---
    // Maps plugin key to its script file. Scripts are loaded on demand.
    // The registry itself is window.collectionPluginRegistry, written by
    // templates/data_collection.html: there each script's URL comes from
    // get_url, which names it by a hash of its content, so new HTML never
    // runs against a cached old plugin and an unchanged plugin stays cached.
    // Keys MUST match the key each plugin registers itself under in
    // window.collectionPlugins — getDataSources() returns that object, so those keys
    // are what drive the ?data=... URLs and the load-once guard in loadPlugin.
    //
    // The registry knows every plugin; window.collectionPluginKeys picks the
    // ones this page shows. The first key is the view shown when the URL names
    // none. The nav tabs
    // are sorted by their label (see generateNav), not by this order or by
    // these keys: the keys are URL and preference identifiers and three of
    // them differ from their label (audio -> Audio Courses, features ->
    // Movies, videos -> Video Series). Nothing may derive any order from
    // window.collectionPlugins: the scripts load in parallel and register in
    // whatever order they finish, so the tabs used to reshuffle between loads.
    const ALL_PLUGIN_FILES = window.collectionPluginRegistry || {};
    const pageKeys = window.collectionPluginKeys || Object.keys(ALL_PLUGIN_FILES);
    window.collectionPluginFiles = {};
    pageKeys.forEach(function(key) {
        if (ALL_PLUGIN_FILES[key]) window.collectionPluginFiles[key] = ALL_PLUGIN_FILES[key];
        else console.error('Unknown plugin in collectionPluginKeys: ' + key);
    });

    window.collectionPlugins = window.collectionPlugins || {};

    // One load per script file: a file may register several keys (the
    // companies plugin registers companies and providers), and loading all
    // plugins in parallel would otherwise insert it once per key.
    const scriptLoads = {};

    function loadPlugin(key) {
        if (window.collectionPlugins[key]) return Promise.resolve();
        const src = window.collectionPluginFiles[key];
        if (!src) return Promise.reject(new Error('Unknown plugin: ' + key));
        if (scriptLoads[src]) return scriptLoads[src];
        scriptLoads[src] = new Promise(function(resolve, reject) {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = function() { reject(new Error('Failed to load ' + src)); };
            document.head.appendChild(script);
        });
        return scriptLoads[src];
    }

    function loadAllPlugins() {
        return Promise.all(Object.keys(window.collectionPluginFiles).map(loadPlugin));
    }

    // Plugin keys in registry order; the first is the default view.
    function pluginKeys() {
        return Object.keys(window.collectionPluginFiles);
    }

    // Plugin keys sorted by the label the reader sees on the tab.
    function pluginKeysByLabel() {
        const sources = window.collectionPlugins || {};
        return pluginKeys()
            .filter(function(key) { return sources[key]; })
            .sort(function(a, b) { return sources[a].navTitle.localeCompare(sources[b].navTitle); });
    }

    // --- Derive sortFields/filters from unified fields registry ---
    // Each field entry: {field, label, type ('string'|'number'), value?, sortable?, filterable?,
    //   filterType ('select'|'boolean'|'year'|'range'|'custom'), ranges?, extractValues?, match?,
    //   defaultValue?}
    // Defaults: sortable=true, filterable=true, filterType='select'
    // defaultValue preselects that option instead of 'All' on load.
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
                    if (f.defaultValue) ff.defaultValue = f.defaultValue;
                    return ff;
                });
        }
    }

    // This script is loaded at the end of <body>, so DOMContentLoaded may have
    // already fired by the time we get here (a cached/inline-fast load). In that
    // case addEventListener would never fire and the app would never boot.
    function onReady(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    onReady(() => {
        const itemsContainer = document.getElementById('items-container');
        const searchContainer = document.getElementById('search-container');
        const searchInput = document.getElementById('search-input');
        const statusMessage = document.getElementById('status-message');
        const pageTitle = document.getElementById('page-title');
        const pageSubtitle = document.getElementById('page-subtitle');
        const mainNav = document.getElementById('main-nav');
        const statsContainer = document.getElementById('stats-container');

        let allItems = []; // To store the fetched data
        let activeConfig = {}; // To store the config of the current view
        // Bumped on every loadData() call. A load that finishes after a newer
        // one started must not touch the page: clicking YouTube then another tab
        // used to render the 29k YouTube items through that tab's plugin
        // when the slower fetch landed second.
        let loadSequence = 0;
        let currentPage = 1;
        let currentFilteredItems = [];
        // A multiple of 6 so every page fills its last row at both the 2- and
        // 3-column widths of the grid (50 left two cards alone on the last row).
        const PAGE_SIZE = 48;
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
        let activeFilters = {}; // {filterField: selectedValue}
        let activeToggles = {}; // {key: boolean}

        // --- Helper Functions ---
        function escapeHtml(str) {
            if (str === null || str === undefined) return '';
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
        }
        window.escapeHtml = escapeHtml;

        // --- Sort Functions ---
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

        // The accessible name carries the visible text (and so the state), not
        // only the static "Toggle sort order" the template gives the button.
        function updateSortOrderBtn() {
            const text = currentSortOrder === 'asc' ? t('ui_sort_asc') : t('ui_sort_desc');
            sortOrderBtn.textContent = text;
            sortOrderBtn.setAttribute('aria-label', t('ui_sort_order') + ': ' + text);
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
            return 'collectionSortPref_' + dataType;
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
            const dataType = urlParams.get('data') || pluginKeys()[0];
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

        // --- Filter Functions ---
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
                select.className = 'control';
                select.setAttribute('aria-label', t('ui_filter_by', {label: filter.label}));
                select.dataset.filterField = filter.field;
                select.dataset.filterType = filter.type;

                const defaultOpt = document.createElement('option');
                defaultOpt.value = '';
                defaultOpt.textContent = t('ui_filter_all', {label: filter.label});
                select.appendChild(defaultOpt);

                values.forEach(function(val) {
                    const opt = document.createElement('option');
                    opt.value = val;
                    // Boolean filters keep 'Yes'/'No' as their values (applyFilters
                    // compares them) and show them translated.
                    opt.textContent = filter.type === 'boolean' ? t(val === 'Yes' ? 'ui_yes' : 'ui_no') : val;
                    select.appendChild(opt);
                });

                // Preselect a default option (and seed activeFilters so the very
                // first render is filtered too, not just subsequent changes).
                if (filter.defaultValue && values.indexOf(filter.defaultValue) !== -1) {
                    select.value = filter.defaultValue;
                    activeFilters[filter.field] = {
                        value: filter.defaultValue, type: filter.type, valueFn: filter.value
                    };
                }

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
                // If filter provides extractValues, use it (returns array of values per item)
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
                    // boolean filters have fixed options, skip extraction
                } else if (filter.type === 'range') {
                    // range filters have fixed buckets, skip extraction
                } else if (filter.type === 'custom') {
                    val = filter.value ? filter.value(item) : item[filter.field];
                    if (val != null && val !== '') valueSet.add(String(val));
                } else {
                    // select
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
                // 2 before 10 when every value is a number (ratings, counts)
                sortKeys(sorted);
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
                        const raw = filterConfig.value ? filterConfig.value(item) : item[field];
                        const numVal = Number(raw);
                        // An item with no value for this field is in no bucket.
                        // NaN compares false against both bounds, so without
                        // this the metadata-less YouTube items matched every
                        // duration and view-count range at once.
                        if (raw == null || raw === '' || Number.isNaN(numVal)) return false;
                        const range = filterConfig.ranges.find(function(r) { return r.label === f.value; });
                        if (!range) return true;
                        if (range.min != null && numVal < range.min) return false;
                        if (range.max != null && numVal >= range.max) return false;
                        return true;
                    }
                    if (filterConfig.type === 'custom' && filterConfig.match) {
                        return filterConfig.match(item, f.value);
                    }
                    // select
                    const val = filterConfig.value ? filterConfig.value(item) : item[field];
                    return String(val) === f.value;
                });
            });
        }

        // --- Toggle Functions ---
        function getTogglePrefKey(dataType) {
            return 'collectionTogglePref_' + dataType;
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
                        css += '.collection-card-image { display: none; }\n';
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
                fields.unshift({key: '_images', label: t('ui_images'), default: true});
            }
            if (fields.length === 0) {
                togglesContainer.style.display = 'none';
                toggleStyles.textContent = '';
                return;
            }
            togglesContainer.style.display = 'flex';

            var urlParams = new URLSearchParams(window.location.search);
            var dataType = urlParams.get('data') || pluginKeys()[0];
            var saved = loadTogglePref(dataType);

            fields.forEach(function(tf) {
                var isOn = saved && Object.hasOwn(saved, tf.key) ? saved[tf.key] : tf.default;
                activeToggles[tf.key] = isOn;

                var label = document.createElement('label');
                label.className = 'inline-flex items-center gap-1 text-sm text-gray-600 cursor-pointer select-none';
                var cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.checked = isOn;
                cb.className = '';
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

        // --- Filters Panel Toggle ---
        function updateFiltersBtnText() {
            const activeCount = Object.keys(activeFilters).length;
            const label = activeCount > 0 ? t('ui_filters_count', {count: activeCount}) : t('ui_filters');
            const arrow = filtersPanel.classList.contains('hidden') ? '\u25BC' : '\u25B2';
            filtersToggleBtn.textContent = label + ' ' + arrow;
            // The name includes the visible state ("Filters (2)"), not only the template's static text.
            filtersToggleBtn.setAttribute('aria-label', t('ui_filters_toggle') + ': ' + label);
            filtersToggleBtn.setAttribute('aria-expanded', !filtersPanel.classList.contains('hidden'));
        }

        filtersToggleBtn.addEventListener('click', function() {
            filtersPanel.classList.toggle('hidden');
            updateFiltersBtnText();
        });

        // --- Master Configuration Object (populated by plugins) ---
        // Read through to window.collectionPlugins on every access rather than
        // snapshotting it: each plugin script begins with
        //   window.collectionPlugins = window.collectionPlugins || {};
        // so a plugin that lands before this line would leave us holding a
        // stale, empty object -- loadData() would then bail on its
        // !activeConfig guard and the nav (including the statistics button)
        // would never render.
        function getDataSources() {
            return window.collectionPlugins || {};
        }

        // --- Dynamically Generate Navigation ---
        function generateNav(activeDataType, showStatsOnly) {
            // The tabs are rebuilt on every click, which would drop keyboard
            // focus to <body>: remember which link had it and refocus its twin.
            const focused = mainNav.contains(document.activeElement) ? document.activeElement.dataset.nav : null;
            mainNav.innerHTML = ''; // Clear existing nav
            // A page with a single plugin (the clients page) gets no tab row:
            // one tab that is always selected is not navigation.
            const tabKeys = pluginKeys().length > 1 ? pluginKeysByLabel() : [];
            for (const key of tabKeys) {
                const config = getDataSources()[key];
                const navLink = document.createElement('a');
                navLink.href = '?data=' + key;
                navLink.textContent = config.navTitle;
                navLink.className = 'chip';
                navLink.dataset.nav = key;
                if (key === activeDataType) {
                    navLink.classList.add('current');
                    navLink.setAttribute('aria-current', 'page');
                }
                navLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(key, false);
                });
                mainNav.appendChild(navLink);
            }

            // An unknown ?data= key still gets its tabs, as the way out of the error.
            if (!activeDataType) return;

            const statsToggle = document.createElement('a');
            statsToggle.dataset.nav = 'stats';
            statsToggle.className = 'chip chip-outline' + (tabKeys.length ? ' ms-4' : '');

            if (showStatsOnly) {
                statsToggle.textContent = t('ui_back_to_full_view');
                statsToggle.href = '?data=' + activeDataType;
                statsToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(activeDataType, false);
                });
            } else {
                statsToggle.textContent = t('ui_view_statistics');
                statsToggle.href = '?data=' + activeDataType + '&stats=true';
                statsToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    switchView(activeDataType, true);
                });
            }
            mainNav.appendChild(statsToggle);
            if (focused !== null) {
                const again = Array.from(mainNav.children).find(function(el) { return el.dataset.nav === focused; });
                if (again) again.focus({preventScroll: true});
            }
        }

        function switchView(dataType, showStats) {
            const params = new URLSearchParams();
            params.set('data', dataType);
            if (showStats) params.set('stats', 'true');
            history.pushState(null, '', '?' + params.toString());
            loadData();
        }

        // Handle browser back/forward
        window.addEventListener('popstate', function() {
            loadData();
        });

        // --- Fetch and Parse JSON Data ---
        // The parsed items per plugin key (see loadData).
        const datasetCache = new Map();

        async function fetchItems(config) {
            const response = await fetch(BASE_PATH + config.file);
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status + ". Make sure '" + config.file + "' is accessible.");
            }

            let jsonText;
            if (config.file.endsWith('.gz')) {
                // Only the .json.gz is shipped (see scripts/copy_data.py), so
                // a browser without DecompressionStream has nothing to fall
                // back to; say so rather than fetching a file that is not there.
                if (typeof DecompressionStream === 'undefined') {
                    throw new Error('This browser cannot decompress the data file (no DecompressionStream support).');
                }
                const ds = new DecompressionStream('gzip');
                const decompressed = response.body.pipeThrough(ds);
                jsonText = await new Response(decompressed).text();
            } else {
                jsonText = await response.text();
            }
            // JSON rather than YAML: js-yaml took ~399ms on the 6.5MB youtube
            // data against ~31ms for JSON.parse, all on the main thread.
            const data = JSON.parse(jsonText);
            // Rename 'title' to 'name' for consistency if it exists
            return (data.items || []).map(item => {
                if (item.title && typeof item.name === 'undefined') {
                    item.name = item.title;
                }
                // A plugin may derive fields in the page's language
                // (the data itself is language-neutral) before search,
                // sort and render see the item.
                if (config.prepareItem) {
                    config.prepareItem(item);
                }
                return item;
            });
        }

        async function loadData() {
            const thisLoad = ++loadSequence;
            const isStale = () => thisLoad !== loadSequence;
            const urlParams = new URLSearchParams(window.location.search);
            const dataType = urlParams.get('data') || pluginKeys()[0];
            const showStatsOnly = urlParams.get('stats') === 'true';
            // Object.hasOwn: ?data=constructor must not resolve to an inherited property.
            const sources = getDataSources();
            activeConfig = Object.hasOwn(sources, dataType) ? sources[dataType] : null;

            if (!activeConfig) {
                // Draw the tabs first: they are the way out of the error.
                generateNav(null, false);
                itemsContainer.innerHTML = '';
                statsContainer.innerHTML = '';
                paginationContainer.hidden = true;
                statusMessage.innerHTML = '<div class="notice-error">' + escapeHtml(t('ui_invalid_data_type')) + '</div>';
                return;
            }
            deriveFieldsConfig(activeConfig);

            generateNav(dataType, showStatsOnly);

            clearTimeout(searchTimer);
            searchInput.value = '';
            currentPage = 1;
            pageTitle.textContent = activeConfig.title;
            pageSubtitle.textContent = showStatsOnly ? t('ui_statistics_overview') : activeConfig.subtitle;
            searchInput.placeholder = activeConfig.searchPlaceholder;
            document.title = activeConfig.title;

            if (showStatsOnly) {
                searchContainer.style.display = 'none';
                itemsContainer.style.display = 'none';
                paginationContainer.hidden = true;
                statsContainer.style.display = 'block';
            } else {
                searchContainer.style.display = 'block';
                itemsContainer.style.display = 'grid';
                statsContainer.style.display = 'none';
            }

            try {
                // The parsed dataset is kept per plugin, so switching tab or
                // view back and forth does not refetch and reparse it (the
                // YouTube file is ~30,000 items).
                let items = datasetCache.get(dataType);
                if (!items) {
                    statusMessage.textContent = t('ui_loading', {title: activeConfig.title});
                    items = await fetchItems(activeConfig);
                    if (isStale()) return;
                    datasetCache.set(dataType, items);
                }
                allItems = items;
                setupSortUI();
                setupFilters();
                setupToggles();
                filtersPanel.classList.add('hidden');
                updateFiltersBtnText();
                // allItems stays sorted: filtering keeps the order, so only a
                // change of sort field or direction sorts again.
                sortItems(allItems);

                if (showStatsOnly) {
                    statsContainer.innerHTML = activeConfig.renderStats(allItems);
                    statusMessage.textContent = '';
                } else {
                    // The same path as every later render, so a default
                    // filter (YouTube: Available) applies to the first one too.
                    currentPage = 1;
                    renderItems(getFilteredItems());
                }

            } catch (error) {
                if (isStale()) return;
                console.error('Error loading or parsing data file:', error);
                itemsContainer.innerHTML = '';
                statsContainer.innerHTML = '';
                statusMessage.innerHTML = '<div class="notice-error"><strong>' + t('ui_loading_failed') + '</strong> ' + escapeHtml(error.message) + '</div>';
            }
        }

        // --- Render Item Cards to the DOM (Generic) ---
        function renderItems(itemList) {
            currentFilteredItems = itemList;
            itemsContainer.innerHTML = '';

            if (itemList.length === 0) {
                statusMessage.textContent = t('ui_no_items');
                paginationContainer.hidden = true;
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

                // allItems is passed as a second argument so a plugin can
                // resolve an item against the whole set, for entries that
                // share one image.
                const rawImgUrl = activeConfig.renderImage ? activeConfig.renderImage(item, allItems) : '';
                const imgUrl = rawImgUrl && !/^https?:\/\//.test(rawImgUrl) ? BASE_PATH + rawImgUrl : rawImgUrl;
                // The image box is a fixed 2:1 landscape. Landscape sources
                // (Audible banners, course art, museum photos) fill it with
                // object-fit: cover. Portrait posters and book covers would
                // lose two thirds of their height to that crop, so a plugin
                // whose sources are portrait declares imageFit: 'contain':
                // the whole image is shown, and the bands either side are a
                // blurred, enlarged copy of the same image rather than flat
                // colour. A plugin whose images are logos on a transparent
                // canvas declares imageBackground: 'light' as well: the box is
                // then white whatever the theme, since the marks were drawn
                // for a white page, and the blurred backdrop is dropped
                // because a blurred logo behind a crisp one reads as a
                // printing error. Styles for the classes live in
                // content/media/_index.en.md next to the other #collection-root rules.
                const contain = activeConfig.imageFit === 'contain';
                const light = activeConfig.imageBackground === 'light';
                const imgHtml = imgUrl
                    ? '<div class="collection-card-image' + (contain ? ' collection-card-image--contain' : '') + (light ? ' collection-card-image--light' : '') + '">' +
                        (contain && !light ? '<img class="collection-card-backdrop" src="' + escapeHtml(imgUrl) + '" alt="" aria-hidden="true" loading="lazy">' : '') +
                        '<img class="collection-card-img" src="' + escapeHtml(imgUrl) + '" alt="' + escapeHtml(item.name || '') + '" loading="lazy">' +
                      '</div>'
                    : '';
                // A plugin may name a placeholder to swap in when the image
                // it asked for does not exist on the server, so an entry whose
                // image has not been fetched yet shows that instead of the
                // broken-image icon. Bound after innerHTML below, since error
                // events do not bubble.
                const placeholderUrl = activeConfig.placeholderImage ? BASE_PATH + activeConfig.placeholderImage : '';

                col.innerHTML =
                    '<div class="bg-gray-50 rounded-lg border border-gray-200 h-full flex flex-col overflow-hidden">' +
                        imgHtml +
                        '<div class="p-4 flex flex-col flex-1">' +
                            // dir="auto": the data is mostly English and the page may be Hebrew;
                            // each text takes its direction from its own first letters.
                            '<h2 class="text-lg font-bold mb-2" dir="auto">' + escapeHtml(item.name || t('ui_no_title')) + '</h2>' +
                            '<p class="text-gray-600 mb-4" dir="auto">' + escapeHtml(item.review || item.subtitle || t('ui_no_description')) + '</p>' +
                            '<ul class="mt-auto divide-y divide-gray-200">' +
                                (activeConfig.ratingScale ? '<li class="py-2"><strong>' + t('ui_rating') + '</strong> <span dir="ltr" class="badge">' + escapeHtml(item.rating === null || item.rating === undefined || item.rating === '' ? '?' : item.rating) + ' / ' + activeConfig.ratingScale + '</span></li>' : '') +
                                (item.device ? '<li class="py-2"><strong>' + t('ui_device') + '</strong> <bdi>' + escapeHtml(item.device) + '</bdi>' + '</li>' : '') +
                                specificDetails +
                            '</ul>' +
                        '</div>' +
                    '</div>';
                const cardImg = col.querySelector('img.collection-card-img');
                if (cardImg && placeholderUrl && imgUrl !== placeholderUrl) {
                    cardImg.addEventListener('error', function() {
                        col.querySelectorAll('.collection-card-image img').forEach(function(img) { img.src = placeholderUrl; });
                    }, {once: true});
                }
                itemsContainer.appendChild(col);
            });

            renderPagination(totalPages, itemList.length);
        }

        // --- Pagination Controls ---
        function renderPagination(totalPages, totalItems) {
            // The pager is rebuilt on every click, which would drop keyboard
            // focus to <body>: remember the control that had it.
            const focusedId = paginationContainer.contains(document.activeElement) ? document.activeElement.id : '';
            if (totalPages <= 1) {
                paginationContainer.hidden = true;
                return;
            }
            paginationContainer.hidden = false;

            const start = (currentPage - 1) * PAGE_SIZE + 1;
            const end = Math.min(currentPage * PAGE_SIZE, totalItems);

            paginationContainer.innerHTML =
                '<button id="btnPrevPage" aria-label="' + escapeHtml(t('ui_previous_page')) + '" class="control">' + escapeHtml(t('ui_previous')) + '</button>' +
                '<span class="text-gray-500">' + escapeHtml(t('ui_showing', {start: start, end: end, total: totalItems})) + '</span>' +
                '<div class="flex items-center gap-2">' +
                    '<label for="jumpToPage" class="text-sm text-gray-500">' + escapeHtml(t('ui_page')) + '</label>' +
                    '<input type="number" id="jumpToPage" aria-label="' + escapeHtml(t('ui_jump_to_page')) + '" class="control w-20" min="1" max="' + totalPages + '" value="' + currentPage + '">' +
                    '<span class="text-gray-500">/ ' + totalPages + '</span>' +
                '</div>' +
                '<button id="btnNextPage" aria-label="' + escapeHtml(t('ui_next_page')) + '" class="control">' + escapeHtml(t('ui_next')) + '</button>';

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

            if (focusedId) {
                // A button that is now disabled (the last page reached) cannot
                // take focus; the other button, or the page box, does.
                const candidates = [focusedId, 'btnNextPage', 'btnPrevPage', 'jumpToPage'];
                for (const id of candidates) {
                    const el = document.getElementById(id);
                    if (el && !el.disabled) { el.focus({preventScroll: true}); break; }
                }
            }
        }

        // --- Filter, Sort, and Render ---
        function getFilteredItems() {
            let items = allItems.slice();
            // Apply dropdown filters
            items = applyFilters(items);
            // Apply search
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

        // allItems is kept sorted (loadData and the sort controls sort it), and
        // filtering and searching keep that order, so nothing re-sorts here.
        function applyFilterSortRender() {
            currentPage = 1;
            renderItems(getFilteredItems());
        }

        function resortAndRender() {
            sortItems(allItems);
            applyFilterSortRender();
        }

        // --- Handle Search Input ---
        // Debounced: the YouTube tab searches ~30,000 items per keystroke.
        let searchTimer = null;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(applyFilterSortRender, 150);
        });

        // --- Handle Sort Changes ---
        function getCurrentDataType() {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get('data') || pluginKeys()[0];
        }

        sortFieldSelect.addEventListener('change', function() {
            applySortFieldConfig(sortFieldSelect.value);
            saveSortPref(getCurrentDataType());
            resortAndRender();
        });

        sortOrderBtn.addEventListener('click', function() {
            currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            updateSortOrderBtn();
            saveSortPref(getCurrentDataType());
            resortAndRender();
        });

        // --- Initial Load ---
        loadAllPlugins().then(loadData).catch(function(error) {
            // Without this, a single failing plugin script rejects the Promise.all
            // in loadAllPlugins, loadData never runs, and the page stays blank with
            // nothing but an uncaught rejection in the console.
            console.error('Error loading collection plugins:', error);
            statusMessage.innerHTML = '<div class="notice-error"><strong>' + t('ui_loading_failed') + '</strong> ' + escapeHtml(error.message) + '</div>';
        });
    });
}());
