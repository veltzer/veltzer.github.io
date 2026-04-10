/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['museums'] = {
    file: 'data/museums.yaml.gz',
    navTitle: 'Museums',
    title: 'Visited Museums',
    subtitle: "A list of museums and exhibitions I've visited over the years.",
    ratingScale: 10,
    searchPlaceholder: 'Search by name, city, review...',
    searchFields: (window.mediaFeatureFlags && window.mediaFeatureFlags.showPeople) ? ['name', 'city', 'review', 'with'] : ['name', 'city', 'review'],
    fields: [
        {field: 'name', label: 'Name', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'city', label: 'City', type: 'string', filterType: 'select'},
        {field: 'date_utcz', label: 'Date Visited', type: 'string', filterType: 'year'},
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'has_url', label: 'Has Website', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.url && item.url.trim() !== ''; }
        },
        {field: 'with_others', label: 'Visited With Others', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.with && item.with.length > 0; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'date', label: 'Date', default: true},
        {key: 'city', label: 'City', default: true},
        {key: 'with', label: 'With', default: false},
        {key: 'remark', label: 'Remark', default: true},
        {key: 'website', label: 'Website Link', default: true}
    ],
    renderImage: function(item) {
        if (!item.internal_id) return '';
        return 'images/museum-' + encodeURIComponent(item.internal_id) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        const date = item.date_utcz ? this.formatDate(item.date_utcz) : item.date_ymd;
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>Date:</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.city) {
            html += '<li class="py-2" data-toggle="city"><strong>City:</strong> ' + window.escapeHtml(item.city) + '</li>';
        }
        if (item.with && item.with.length > 0) {
            html += '<li class="py-2" data-toggle="with"><strong>With:</strong> ' + window.escapeHtml(item.with.join(', ')) + '</li>';
        }
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>Remark:</strong> ' + window.escapeHtml(item.remark) + '</li>';
        }
        if (item.url) {
            html += '<li class="py-2" data-toggle="website"><a href="' + window.escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; Visit Website</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const cityCounts = {};
        const yearCounts = {};

        const getYear = (item) => {
            if (item.date_utcz) return item.date_utcz.substring(0, 4);
            if (item.date_dmy) { const parts = item.date_dmy.split('-'); return parts.length === 3 ? parts[2] : null; }
            return null;
        };

        items.forEach(function(item) {
            if (item.city) {
                cityCounts[item.city] = (cityCounts[item.city] || 0) + 1;
            }
            const year = getYear(item);
            if (year) {
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        });

        let html = '<div class="grid grid-cols-1 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Visits') + '</div>';
        html += '</div>';
        html += renderBarChart('Visits per City', cityCounts, {unit: 'visits', sort: 'desc'});
        html += renderBarChart('Visits per Year', yearCounts, {unit: 'visits', sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
