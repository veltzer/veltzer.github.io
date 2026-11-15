/* global renderBarChart, renderStatCard, mediaFormatDate, t, countByYear, deviceCounts, hasReviewField, toggleLine, mediaLinkLines */
window.collectionPlugins = window.collectionPlugins || {};

window.collectionPlugins['videos'] = {
    file: 'data/video_series.json.gz',
    navTitle: t('series_nav_title'),
    title: t('series_title'),
    subtitle: t('series_subtitle'),
    ratingScale: 10,
    searchPlaceholder: t('series_search_placeholder'),
    searchFields: ['name', 'review', 'location'],
    fields: [
        {field: 'name', label: t('series_f_title'), type: 'string', filterable: false},
        {field: 'rating', label: t('series_f_rating'), type: 'number', filterType: 'select'},
        {field: 'date_utcz', label: t('series_f_date'), type: 'string', filterType: 'year'},
        {field: 'device', label: t('series_f_device'), type: 'string', filterType: 'select'},
        {field: 'location', label: t('series_f_location'), type: 'string', filterType: 'select'},
        {field: 'seasons_count', label: t('series_f_seasons_count'), type: 'number',
            value: function(item) { return item.seasons_seen ? item.seasons_seen.length : 0; },
            filterType: 'range', ranges: [
                {label: t('series_range_1'), min: 0, max: 2},
                {label: t('series_range_2_3'), min: 2, max: 4},
                {label: t('series_range_4_6'), min: 4, max: 7},
                {label: t('series_range_7'), min: 7, max: null}
            ]
        },
        {field: 'completed', label: t('series_f_completed'), type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                return (!item.seasons_not_seen || item.seasons_not_seen.length === 0) ? t('series_fully_watched') : t('series_has_unwatched');
            },
            match: function(item, val) {
                var hasUnwatched = item.seasons_not_seen && item.seasons_not_seen.length > 0;
                return val === t('series_fully_watched') ? !hasUnwatched : hasUnwatched;
            }
        },
        hasReviewField(t('series_f_has_review'))
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'seasons', label: t('series_t_seasons'), default: true},
        {key: 'date', label: t('series_t_date'), default: true},
        {key: 'location', label: t('series_t_location'), default: true},
        {key: 'imdb', label: t('series_t_imdb'), default: true},
        {key: 'wikidata', label: t('series_t_wikidata'), default: true},
        {key: 'rottentomatoes', label: t('series_t_rt'), default: true}
    ],
    // Covers/posters are 2:3 portrait; see imageFit in data-collection-app.js.
    imageFit: 'contain',
    renderImage: function(item) {
        if (!item.imdb_id) return '';
        return 'images/series-' + encodeURIComponent(item.imdb_id) + '.jpg';
    },
    renderDetails: function(item) {
        const seasons = item.seasons_seen ? item.seasons_seen.join(', ') : t('series_na');
        let html = toggleLine('seasons', t('series_f_seasons_seen') + ':', window.escapeHtml(seasons));
        const date = this.formatDate(item.date_utcz);
        if (date) {
            html += toggleLine('date', t('series_f_date') + ':', window.escapeHtml(date));
        }
        if (item.location) {
            html += toggleLine('location', t('series_f_location') + ':', window.escapeHtml(item.location));
        }
        return html + mediaLinkLines(item, 'series');
    },
    renderStats: function(items) {
        const totalSeasons = items.reduce(function(sum, item) {
            return sum + (item.seasons_seen ? item.seasons_seen.length : 0);
        }, 0);

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('series_total_series')) + '</div>';
        html += '<div>' + renderStatCard(totalSeasons, t('series_total_seasons')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('series_device_dist'), deviceCounts(items));
        html += renderBarChart(t('series_per_year'), countByYear(items, function(item) { return item.date_utcz; }),
            {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
