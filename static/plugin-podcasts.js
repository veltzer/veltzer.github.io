/* global t, renderBarChart, renderStatCard, mediaFormatDate, hasReviewField, linkLine, tally, toggleLine */
window.collectionPlugins = window.collectionPlugins || {};

(function() {
    function getChapterDates(item) {
        if (!item.chapters || item.chapters.length === 0) return [];
        return item.chapters
            .map(function(ch) { return ch.date_utcz; })
            .filter(function(d) { return d; })
            .sort();
    }

    function getFirstListened(item) {
        var dates = getChapterDates(item);
        return dates.length > 0 ? dates[0] : '';
    }

    function getLastListened(item) {
        var dates = getChapterDates(item);
        return dates.length > 0 ? dates[dates.length - 1] : '';
    }

    function getChapterCount(item) {
        return item.chapters ? item.chapters.length : 0;
    }

window.collectionPlugins['podcasts'] = {
    file: 'data/podcasts.json.gz',
    navTitle: t('podcasts_nav_title'),
    title: t('podcasts_title'),
    subtitle: t('podcasts_subtitle'),
    ratingScale: 10,
    searchPlaceholder: t('podcasts_search_placeholder'),
    searchFields: ['name', 'review', 'url'],
    fields: [
        {field: 'name', label: t('podcasts_name'), type: 'string', filterable: false},
        {field: 'rating', label: t('podcasts_rating'), type: 'number', filterType: 'select'},
        {field: 'chapter_count', label: t('podcasts_chapters_listened'), type: 'number', value: getChapterCount,
            filterType: 'range', ranges: [
                {label: '1\u20135', min: 1, max: 6},
                {label: '6\u201320', min: 6, max: 21},
                {label: '21\u201350', min: 21, max: 51},
                {label: t('podcasts_range_51_plus'), min: 51, max: null}
            ]
        },
        {field: 'first_listened', label: t('podcasts_first_listened'), type: 'string', value: getFirstListened, filterType: 'year'},
        {field: 'last_listened', label: t('podcasts_last_listened'), type: 'string', value: getLastListened, filterType: 'year'},
        {field: 'has_chapters', label: t('podcasts_has_chapters'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.chapters && item.chapters.length > 0; }
        },
        hasReviewField(t('podcasts_has_review')),
        {field: 'has_url', label: t('podcasts_has_url'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.url && item.url.trim() !== ''; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'link', label: t('podcasts_toggle_link'), default: true},
        {key: 'chapters', label: t('podcasts_toggle_chapters'), default: true}
    ],
    renderImage: function(item) {
        if (!item.internal_id) return '';
        return 'images/podcast-' + encodeURIComponent(item.internal_id) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.url) {
            html += linkLine('link', item.url, t('podcasts_visit'));
        }
        if (item.chapters && item.chapters.length > 0) {
            html += toggleLine('chapters', t('podcasts_d_chapters'), item.chapters.length);
            const dates = getChapterDates(item);
            if (dates.length > 0) {
                html += toggleLine('chapters', t('podcasts_d_first'), dates[0].substring(0, 10));
                html += toggleLine('chapters', t('podcasts_d_last'), dates[dates.length - 1].substring(0, 10));
            }
        }
        return html;
    },
    renderStats: function(items) {
        let totalChapters = 0;
        const deviceCounts = {};
        const locationCounts = {};

        items.forEach(function(item) {
            if (item.chapters) {
                totalChapters += item.chapters.length;
                item.chapters.forEach(function(ch) {
                    tally(deviceCounts, ch.device);
                    tally(locationCounts, ch.location);
                });
            }
        });

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('podcasts_total')) + '</div>';
        html += '<div>' + renderStatCard(totalChapters, t('podcasts_total_chapters')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('podcasts_devices'), deviceCounts, {unit: t('podcasts_unit_chapters')});
        html += renderBarChart(t('podcasts_locations'), locationCounts, {unit: t('podcasts_unit_chapters'), sort: 'desc', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};

})();
