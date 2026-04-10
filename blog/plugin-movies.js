/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['features'] = {
    file: 'data/video_features.yaml.gz',
    navTitle: 'Movies',
    title: 'Watched Movies',
    subtitle: "A searchable list of movies I've watched.",
    ratingScale: 10,
    searchPlaceholder: 'Search by title, review, location...',
    searchFields: ['name', 'review', 'location'],
    fields: [
        {field: 'name', label: 'Title', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'date_utcz', label: 'Date Watched', type: 'string', filterType: 'year'},
        {field: 'device', label: 'Device', type: 'string', filterType: 'select'},
        {field: 'location', label: 'Location', type: 'string', filterType: 'select'},
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'with_others', label: 'Watched With Others', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.with && item.with.length > 0; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'date', label: 'Date Watched', default: true},
        {key: 'location', label: 'Location', default: true},
        {key: 'with', label: 'With', default: false},
        {key: 'imdb', label: 'IMDb Link', default: true}
    ],
    renderImage: function(item) {
        if (!item.imdb_id) return '';
        return 'images/movie-' + encodeURIComponent(item.imdb_id) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        const date = this.formatDate(item.date_utcz);
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>Date Watched:</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>Location:</strong> ' + window.escapeHtml(item.location) + '</li>';
        }
        if (item.with && item.with.length > 0) {
            html += '<li class="py-2" data-toggle="with"><strong>With:</strong> ' + window.escapeHtml(item.with.join(', ')) + '</li>';
        }
        if (item.imdb_id) {
            html += '<li class="py-2" data-toggle="imdb"><a href="https://www.imdb.com/title/tt' + window.escapeHtml(item.imdb_id) + '/" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; View on IMDb</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const deviceCounts = {};
        const yearCounts = {};
        let withCount = 0;
        items.forEach(function(item) {
            if (item.device) {
                deviceCounts[item.device] = (deviceCounts[item.device] || 0) + 1;
            }
            if (window.mediaFeatureFlags && window.mediaFeatureFlags.showPeople && item.with && item.with.length > 0) {
                withCount++;
            }
            const date = this.formatDate(item.date_utcz);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Movies') + '</div>';
        if (window.mediaFeatureFlags && window.mediaFeatureFlags.showPeople) {
            html += '<div>' + renderStatCard(withCount, 'Movies Watched with Others') + '</div>';
        }
        html += '</div>';
        html += renderBarChart('Device Distribution', deviceCounts);
        html += renderBarChart('Items per Year', yearCounts, {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
