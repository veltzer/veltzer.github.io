/* global t, renderBarChart, renderStatCard, mediaFormatDate, countByYear, deviceCounts, hasReviewField, showPeople, toggleLine, mediaLinkLines */
window.collectionPlugins = window.collectionPlugins || {};

// The names of who watched with me are shown only when the page's showPeople
// flag is on (templates/data_collection.html): see showPeople() in the utils.

window.collectionPlugins['features'] = {
    file: 'data/video_features.json.gz',
    navTitle: t('movies_nav_title'),
    title: t('movies_title'),
    subtitle: t('movies_subtitle'),
    ratingScale: 10,
    searchPlaceholder: t('movies_search_placeholder'),
    searchFields: showPeople() ? ['name', 'review', 'location', 'with'] : ['name', 'review', 'location'],
    fields: [
        {field: 'name', label: t('movies_label_title'), type: 'string', filterable: false},
        {field: 'rating', label: t('movies_label_rating'), type: 'number', filterType: 'select'},
        {field: 'date_utcz', label: t('movies_label_date_watched'), type: 'string', filterType: 'year'},
        {field: 'device', label: t('movies_label_device'), type: 'string', filterType: 'select'},
        {field: 'location', label: t('movies_label_location'), type: 'string', filterType: 'select'},
        hasReviewField(t('movies_label_has_review'))
    ].concat(showPeople() ? [
        {field: 'with_others', label: t('movies_label_with_others'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return Boolean(item.with && item.with.length > 0); }
        }
    ] : []),
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'date', label: t('movies_label_date_watched'), default: true},
        {key: 'location', label: t('movies_label_location'), default: true},
        {key: 'with', label: t('movies_label_with'), default: false},
        {key: 'imdb', label: t('movies_toggle_imdb'), default: true},
        {key: 'wikidata', label: t('movies_toggle_wikidata'), default: true},
        {key: 'rottentomatoes', label: t('movies_toggle_rt'), default: true}
    ].filter(function(toggle) { return showPeople() || toggle.key !== 'with'; }),
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
            html += toggleLine('date', t('movies_label_date_watched') + ':', window.escapeHtml(date));
        }
        if (item.location) {
            html += toggleLine('location', t('movies_label_location') + ':', window.escapeHtml(item.location));
        }
        if (showPeople() && item.with && item.with.length > 0) {
            html += toggleLine('with', t('movies_label_with') + ':', window.escapeHtml(item.with.join(', ')));
        }
        return html + mediaLinkLines(item, 'movies');
    },
    renderStats: function(items) {
        const withCount = showPeople()
            ? items.filter(function(item) { return item.with && item.with.length > 0; }).length
            : 0;

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('movies_total')) + '</div>';
        if (showPeople()) {
            html += '<div>' + renderStatCard(withCount, t('movies_with_others')) + '</div>';
        }
        html += '</div>';
        html += renderBarChart(t('movies_device_distribution'), deviceCounts(items));
        html += renderBarChart(t('movies_per_year'), countByYear(items, function(item) { return item.date_utcz; }),
            {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
