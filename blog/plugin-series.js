/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['videos'] = {
    file: 'data/video_series.yaml.gz',
    navTitle: 'Video Series',
    title: 'Watched TV Series',
    subtitle: "A searchable list of TV series I've watched.",
    ratingScale: 10,
    searchPlaceholder: 'Search by name, review, location...',
    searchFields: ['name', 'review', 'location'],
    fields: [
        {field: 'name', label: 'Title', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'date_utcz', label: 'Date Watched', type: 'string', filterType: 'year'},
        {field: 'device', label: 'Device', type: 'string', filterType: 'select'},
        {field: 'location', label: 'Location', type: 'string', filterType: 'select'},
        {field: 'seasons_count', label: 'Seasons Count', type: 'number',
            value: function(item) { return item.seasons_seen ? item.seasons_seen.length : 0; },
            filterType: 'range', ranges: [
                {label: '1 season', min: 0, max: 2},
                {label: '2-3 seasons', min: 2, max: 4},
                {label: '4-6 seasons', min: 4, max: 7},
                {label: '7+ seasons', min: 7, max: null}
            ]
        },
        {field: 'completed', label: 'Completed', type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                return (!item.seasons_not_seen || item.seasons_not_seen.length === 0) ? 'Fully Watched' : 'Has Unwatched Seasons';
            },
            match: function(item, val) {
                var hasUnwatched = item.seasons_not_seen && item.seasons_not_seen.length > 0;
                return val === 'Fully Watched' ? !hasUnwatched : hasUnwatched;
            }
        },
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'seasons', label: 'Seasons Seen', default: true},
        {key: 'date', label: 'Date Watched', default: true},
        {key: 'location', label: 'Location', default: true},
        {key: 'imdb', label: 'IMDb Link', default: true}
    ],
    renderImage: function(item) {
        if (!item.imdb_id) return '';
        return 'images/series-' + encodeURIComponent(item.imdb_id) + '.jpg';
    },
    renderDetails: function(item) {
        const seasons = item.seasons_seen ? item.seasons_seen.join(', ') : 'N/A';
        let html = '<li class="py-2" data-toggle="seasons"><strong>Seasons Seen:</strong> ' + window.escapeHtml(seasons) + '</li>';
        const date = this.formatDate(item.date_utcz);
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>Date Watched:</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>Location:</strong> ' + window.escapeHtml(item.location) + '</li>';
        }
        if (item.imdb_id) {
            html += '<li class="py-2" data-toggle="imdb"><a href="https://www.imdb.com/title/tt' + window.escapeHtml(item.imdb_id) + '/" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; View on IMDb</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const deviceCounts = {};
        const yearCounts = {};
        let totalSeasons = 0;
        items.forEach(function(item) {
            if (item.device) {
                deviceCounts[item.device] = (deviceCounts[item.device] || 0) + 1;
            }
            if (item.seasons_seen) {
                totalSeasons += item.seasons_seen.length;
            }
            const date = this.formatDate(item.date_utcz);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Series') + '</div>';
        html += '<div>' + renderStatCard(totalSeasons, 'Total Seasons') + '</div>';
        html += '</div>';
        html += renderBarChart('Device Distribution', deviceCounts);
        html += renderBarChart('Items per Year', yearCounts, {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
