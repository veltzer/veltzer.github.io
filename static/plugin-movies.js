/* global t, renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

window.collectionPlugins['features'] = {
    file: 'data/video_features.json.gz',
    navTitle: t('movies_nav_title'),
    title: t('movies_title'),
    subtitle: t('movies_subtitle'),
    ratingScale: 10,
    searchPlaceholder: t('movies_search_placeholder'),
    searchFields: ['name', 'review', 'location'],
    fields: [
        {field: 'name', label: t('movies_label_title'), type: 'string', filterable: false},
        {field: 'rating', label: t('movies_label_rating'), type: 'number', filterType: 'select'},
        {field: 'date_utcz', label: t('movies_label_date_watched'), type: 'string', filterType: 'year'},
        {field: 'device', label: t('movies_label_device'), type: 'string', filterType: 'select'},
        {field: 'location', label: t('movies_label_location'), type: 'string', filterType: 'select'},
        {field: 'has_review', label: t('movies_label_has_review'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'with_others', label: t('movies_label_with_others'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.with && item.with.length > 0; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'date', label: t('movies_label_date_watched'), default: true},
        {key: 'location', label: t('movies_label_location'), default: true},
        {key: 'with', label: t('movies_label_with'), default: false},
        {key: 'imdb', label: t('movies_toggle_imdb'), default: true},
        {key: 'wikidata', label: t('movies_toggle_wikidata'), default: true},
        {key: 'rottentomatoes', label: t('movies_toggle_rt'), default: true}
    ],
    // Covers/posters are 2:3 portrait; see imageFit in data-collection-app.js.
    imageFit: 'contain',
    renderImage: function(item) {
        if (!item.imdb_id) return '';
        return 'images/movie-' + encodeURIComponent(item.imdb_id) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        const date = this.formatDate(item.date_utcz);
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>' + t('movies_label_date_watched') + ':</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>' + t('movies_label_location') + ':</strong> ' + window.escapeHtml(item.location) + '</li>';
        }
        if (item.with && item.with.length > 0) {
            html += '<li class="py-2" data-toggle="with"><strong>' + t('movies_label_with') + ':</strong> ' + window.escapeHtml(item.with.join(', ')) + '</li>';
        }
        if (item.imdb_id) {
            html += '<li class="py-2" data-toggle="imdb"><a href="https://www.imdb.com/title/tt' + window.escapeHtml(item.imdb_id) + '/" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('movies_view_imdb') + '</a></li>';
        }
        if (item.wikidata_id) {
            html += '<li class="py-2" data-toggle="wikidata"><a href="https://www.wikidata.org/wiki/' + window.escapeHtml(item.wikidata_id) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('movies_view_wikidata') + '</a></li>';
        }
        if (item.rotten_tomatoes_id) {
            html += '<li class="py-2" data-toggle="rottentomatoes"><a href="https://www.rottentomatoes.com/' + window.escapeHtml(item.rotten_tomatoes_id) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('movies_view_rt') + '</a></li>';
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
            if (window.collectionFeatureFlags && window.collectionFeatureFlags.showPeople && item.with && item.with.length > 0) {
                withCount++;
            }
            const date = this.formatDate(item.date_utcz);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('movies_total')) + '</div>';
        if (window.collectionFeatureFlags && window.collectionFeatureFlags.showPeople) {
            html += '<div>' + renderStatCard(withCount, t('movies_with_others')) + '</div>';
        }
        html += '</div>';
        html += renderBarChart(t('movies_device_distribution'), deviceCounts);
        html += renderBarChart(t('movies_per_year'), yearCounts, {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
