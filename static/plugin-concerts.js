/* global t, renderBarChart, renderStatCard */
window.collectionPlugins = window.collectionPlugins || {};

// Concerts and live shows I saw, the Concerts tab of the media page (/media/),
// from data/yaml/concerts.yaml. A show is dated as precisely as the source
// knew it: date_utcz (a full timestamp), date_ymd, date_my (MM-YYYY) or date_y,
// and some have no date at all.

// The date as a sortable ISO prefix: YYYY-MM-DD, YYYY-MM or YYYY ('' when unknown).
function concertDate(item) {
    if (item.date_utcz) return item.date_utcz.substring(0, 10);
    if (item.date_ymd) return item.date_ymd;
    if (item.date_my) return item.date_my.substring(3) + '-' + item.date_my.substring(0, 2);
    return item.date_y || '';
}

function concertYear(item) {
    return concertDate(item).substring(0, 4);
}

// genre is an identifier (jazz, rock, ...), shown through its string.
function concertGenre(item) {
    return item.genre ? t('concerts_genre_' + item.genre) : '';
}

function showPeople() {
    return Boolean(window.collectionFeatureFlags && window.collectionFeatureFlags.showPeople);
}

window.collectionPlugins['concerts'] = {
    file: 'data/concerts.json.gz',
    navTitle: t('concerts_nav_title'),
    title: t('concerts_title'),
    subtitle: t('concerts_subtitle'),
    ratingScale: null,
    searchPlaceholder: t('concerts_search_placeholder'),
    searchFields: showPeople() ? ['name', 'performers', 'event', 'venue', 'review', 'remark', 'with']
        : ['name', 'performers', 'event', 'venue', 'review', 'remark'],
    // The line under the name: the venue and city.
    prepareItem: function(item) {
        const where = [item.venue, item.city].filter(Boolean);
        if (where.length) item.subtitle = where.join(', ');
    },
    // Sort fields are given rather than derived from `fields`, so that an
    // undated show sorts after the dated ones.
    sortFields: [
        {field: 'date', label: t('concerts_field_date'), type: 'string',
            value: function(item) { return concertDate(item) || '￿'; }
        },
        {field: 'name', label: t('concerts_field_name'), type: 'string'},
        {field: 'city', label: t('concerts_field_city'), type: 'string'},
        {field: 'genre', label: t('concerts_field_genre'), type: 'string', value: concertGenre}
    ],
    fields: [
        {field: 'name', label: t('concerts_field_name'), type: 'string', filterable: false},
        {field: 'genre', label: t('concerts_field_genre'), type: 'string', filterType: 'select', value: concertGenre},
        {field: 'city', label: t('concerts_field_city'), type: 'string', filterType: 'select'},
        {field: 'country', label: t('concerts_field_country'), type: 'string', filterType: 'select'},
        {field: 'date', label: t('concerts_field_date'), type: 'string', filterType: 'year', value: concertDate},
        {field: 'broadcast', label: t('concerts_field_broadcast'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return Boolean(item.broadcast); }
        },
        {field: 'has_review', label: t('concerts_field_has_review'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return Boolean(item.review); }
        }
    ],
    defaultSort: {field: 'date', order: 'asc'},
    toggleFields: [
        {key: 'performers', label: t('concerts_toggle_performers'), default: true},
        {key: 'event', label: t('concerts_toggle_event'), default: true},
        {key: 'genre', label: t('concerts_toggle_genre'), default: true},
        {key: 'date', label: t('concerts_toggle_date'), default: true},
        {key: 'review', label: t('concerts_toggle_review'), default: true},
        {key: 'remark', label: t('concerts_toggle_remark'), default: true},
        {key: 'credit', label: t('concerts_toggle_credit'), default: true}
    ],
    // One image per show, static/images/concert-<internal_id>.jpg: the
    // performer where Wikipedia has a free photo of them, otherwise the venue
    // or the instrument. image_source/license/author credit it below.
    renderImage: function(item) {
        return item.internal_id ? 'images/concert-' + encodeURIComponent(item.internal_id) + '.jpg' : '';
    },
    // Data values are English, so they sit in <bdi> on a Hebrew page.
    renderDetails: function(item) {
        const bdi = function(text) { return '<bdi>' + window.escapeHtml(text) + '</bdi>'; };
        const line = function(toggle, label, html) {
            return '<li class="py-2" data-toggle="' + toggle + '"><strong>' + label + '</strong> ' + html + '</li>';
        };
        let html = '';
        if (item.performers && item.performers.length) {
            html += line('performers', t('concerts_detail_performers'), item.performers.map(bdi).join(', '));
        }
        if (item.event) html += line('event', t('concerts_detail_event'), bdi(item.event));
        if (item.genre) html += line('genre', t('concerts_detail_genre'), window.escapeHtml(concertGenre(item)));
        const date = concertDate(item);
        html += line('date', t('concerts_detail_date'),
            '<bdi dir="ltr">' + window.escapeHtml(date || t('concerts_date_unknown')) + '</bdi>' +
            (item.broadcast ? ' (' + window.escapeHtml(t('concerts_on_tv')) + ')' : ''));
        if (showPeople() && item.with && item.with.length) {
            html += line('with', t('concerts_detail_with'), item.with.map(bdi).join(', '));
        }
        if (item.review) html += line('review', t('concerts_detail_review'), bdi(item.review));
        if (item.remark) html += line('remark', t('concerts_detail_remark'), bdi(item.remark));
        if (item.image_source) {
            const credit = [item.image_author, item.image_license].filter(Boolean).join(', ');
            html += '<li class="py-2 text-sm" data-toggle="credit">' + window.escapeHtml(t('concerts_image_credit')) + ' ' +
                '<a href="' + window.escapeHtml(item.image_source) + '" target="_blank" rel="noopener noreferrer"' +
                ' class="text-blue-600 hover:text-blue-800 underline">' + bdi(credit || t('concerts_image_source')) + '</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const genreCounts = {};
        const cityCounts = {};
        const yearCounts = {};
        const performerCounts = {};
        items.forEach(function(item) {
            const genre = concertGenre(item);
            if (genre) genreCounts[genre] = (genreCounts[genre] || 0) + 1;
            if (item.city) cityCounts[item.city] = (cityCounts[item.city] || 0) + 1;
            const year = concertYear(item);
            if (year) yearCounts[year] = (yearCounts[year] || 0) + 1;
            (item.performers || []).forEach(function(name) {
                performerCounts[name] = (performerCounts[name] || 0) + 1;
            });
        });
        // Only performers seen more than once: the rest is a long tail of ones.
        const repeated = {};
        Object.keys(performerCounts).forEach(function(name) {
            if (performerCounts[name] > 1) repeated[name] = performerCounts[name];
        });
        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('concerts_stat_shows')) + '</div>';
        html += '<div>' + renderStatCard(Object.keys(performerCounts).length, t('concerts_stat_performers')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('concerts_chart_by_genre'), genreCounts, {unit: t('concerts_unit'), sort: 'desc'});
        html += renderBarChart(t('concerts_chart_by_performer'), repeated, {unit: t('concerts_unit'), sort: 'desc'});
        html += renderBarChart(t('concerts_chart_by_city'), cityCounts, {unit: t('concerts_unit'), sort: 'desc', barClass: 'bg-success'});
        html += renderBarChart(t('concerts_chart_by_year'), yearCounts, {unit: t('concerts_unit'), last: true});
        return html;
    }
};
