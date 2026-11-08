// Shared utilities for the data collection app and its plugins

/**
 * The UI string ``app_<key>`` in the page's language.
 *
 * templates/data_collection.html writes every app_* key of i18n/<lang>.toml
 * into window.collectionStrings, so the strings live in the site's own
 * translation files and a key missing from a language fails the build there.
 * ``{name}`` placeholders are filled from ``vars``. A key the page does not
 * have is a bug: it is logged and its name shown, never silently English.
 * @param {string} key - the key without its app_ prefix
 * @param {Object} [vars] - values for {placeholders}
 * @returns {string}
 */
function t(key, vars) {
    const strings = window.collectionStrings || {};
    let text = strings['app_' + key];
    if (text === undefined) {
        console.error('Missing UI string app_' + key + ' (add it to i18n/en.toml and i18n/he.toml)');
        text = key;
    }
    if (vars) {
        text = text.replace(/\{(\w+)\}/g, function(match, name) {
            return Object.hasOwn(vars, name) ? String(vars[name]) : match;
        });
    }
    return text;
}

// Bar colours from the theme, so a chart follows the theme switcher like the
// rest of the site: the accent, the four entity colours, then the status ones.
const CHART_COLORS = ['var(--accent)', 'var(--entity-1)', 'var(--entity-2)', 'var(--entity-3)',
    'var(--entity-4)', 'var(--success)', 'var(--warning)'];

// Map color keys to Tailwind background classes
const COLOR_CLASS_MAP = {
    'bg-primary': 'bg-blue-600',
    'bg-success': 'bg-green-600',
    'bg-info': 'bg-blue-500',
    'bg-danger': 'bg-red-600',
    'bg-warning': 'bg-yellow-500'
};

/**
 * Render a horizontal bar chart card.
 * @param {string} title - Card header text
 * @param {Object} counts - {label: count} object
 * @param {Object} [options]
 * @param {string} [options.unit='items'] - Unit label for counts
 * @param {string} [options.barClass] - Color class (e.g. 'bg-success'). Overrides color cycling.
 * @param {string} [options.sort='alpha'] - 'alpha' (alphabetical), 'desc' (by count), 'reverse' (reverse alphabetical)
 * @param {number} [options.limit] - Max number of entries to show
 * @param {boolean} [options.last=false] - If false, adds mb-4 to card
 * @returns {string} HTML string
 */
function renderBarChart(title, counts, options) {
    const opts = options || {};
    const unit = opts.unit || t('ui_items');
    const barClass = opts.barClass || null;
    const sort = opts.sort || 'alpha';
    const limit = opts.limit || 0;
    const last = opts.last || false;

    let keys = Object.keys(counts);
    if (sort === 'desc') {
        keys.sort(function(a, b) { return counts[b] - counts[a]; });
    } else if (sort === 'reverse') {
        keys.sort().reverse();
    } else {
        keys.sort();
    }
    if (limit > 0) {
        keys = keys.slice(0, limit);
    }

    const maxCount = keys.reduce(function(max, k) { return Math.max(max, counts[k]); }, 0);
    let colorIndex = 0;

    let html = '<div class="bg-gray-50 rounded-lg border border-gray-200' + (last ? '' : ' mb-4') + '">' +
        '<div class="px-4 py-3 border-b border-gray-200 font-semibold">' + window.escapeHtml(title) + '</div>' +
        '<div class="p-4">';

    keys.forEach(function(key) {
        const count = counts[key];
        const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
        const resolvedClass = barClass ? (COLOR_CLASS_MAP[barClass] || barClass) : '';
        const style = barClass ? '' : 'background-color:' + CHART_COLORS[colorIndex % CHART_COLORS.length] + ';';

        html += '<div class="mb-3">';
        html += '<p class="mb-1"><strong>' + window.escapeHtml(key) + '</strong> ' +
            '<span class="text-gray-500">(' + count + ' ' + window.escapeHtml(unit) + ')</span></p>';
        html += '<div class="w-full bg-gray-200 rounded-full h-5">';
        html += '<div class="h-5 rounded-full ' + resolvedClass + '" style="width: ' + pct + '%;' +
            style + '"></div>';
        html += '</div></div>';
        colorIndex++;
    });

    html += '</div></div>';
    return html;
}

/**
 * Render a stat summary card.
 * @param {string} value - The stat value
 * @param {string} label - The stat label
 * @returns {string} HTML string for one stat card column
 */
function renderStatCard(value, label) {
    return '<div class="bg-gray-50 rounded-lg border border-gray-200 stat-card h-full"><div class="p-4">' +
        '<span class="stat-value">' + window.escapeHtml(String(value)) + '</span>' +
        '<span class="stat-label block">' + window.escapeHtml(label) + '</span>' +
        '</div></div>';
}

/**
 * Format a date string to YYYY-MM-DD.
 * @param {string} dateString - ISO date or date-like string
 * @returns {string|null} Formatted date or null if input is falsy
 */
function mediaFormatDate(dateString) {
    if (!dateString) return null;
    return String(dateString).substring(0, 10);
}

// Published as globals: the media plugins are loaded as classic scripts and
// call these by name (see the /* global */ header in each plugin-*.js).
window.t = t;
window.renderBarChart = renderBarChart;
window.renderStatCard = renderStatCard;
window.mediaFormatDate = mediaFormatDate;
