/* exported renderBarChart, renderStatCard, mediaFormatDate */
// Shared utilities for media plugins

const CHART_COLORS = ['#2563eb', '#7c3aed', '#db2777', '#ea580c', '#16a34a', '#dc2626', '#ca8a04'];

// Map color keys to Tailwind background classes
const COLOR_CLASS_MAP = {
    'bg-primary': 'bg-blue-600',
    'bg-success': 'bg-green-600',
    'bg-info': 'bg-cyan-500',
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
    const unit = opts.unit || 'items';
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

    let html = '<div class="bg-white rounded-lg shadow-sm border border-gray-200' + (last ? '' : ' mb-4') + '">' +
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
    return '<div class="bg-white rounded-lg shadow-sm border border-gray-200 stat-card h-full"><div class="p-4">' +
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
