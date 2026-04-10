/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

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

window.mediaPlugins['podcasts'] = {
    file: 'data/podcasts.yaml.gz',
    navTitle: 'Podcasts',
    title: 'Listened Podcasts',
    subtitle: "A searchable list of podcasts I've listened to.",
    ratingScale: 10,
    searchPlaceholder: 'Search by name, review, chapter...',
    searchFields: ['name', 'review', 'url'],
    fields: [
        {field: 'name', label: 'Name', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'chapter_count', label: 'Chapters Listened', type: 'number', value: getChapterCount,
            filterType: 'range', ranges: [
                {label: '1\u20135', min: 1, max: 6},
                {label: '6\u201320', min: 6, max: 21},
                {label: '21\u201350', min: 21, max: 51},
                {label: '51+', min: 51, max: null}
            ]
        },
        {field: 'first_listened', label: 'First Listened', type: 'string', value: getFirstListened, filterType: 'year'},
        {field: 'last_listened', label: 'Last Listened', type: 'string', value: getLastListened, filterType: 'year'},
        {field: 'has_chapters', label: 'Has Chapters', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.chapters && item.chapters.length > 0; }
        },
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'has_url', label: 'Has URL', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.url && item.url.trim() !== ''; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'link', label: 'Podcast Link', default: true},
        {key: 'chapters', label: 'Chapters Info', default: true}
    ],
    renderImage: function(item) {
        if (!item.internal_id) return '';
        return 'images/podcast-' + encodeURIComponent(item.internal_id) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.url) {
            html += '<li class="py-2" data-toggle="link"><a href="' + window.escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; Visit Podcast</a></li>';
        }
        if (item.chapters && item.chapters.length > 0) {
            html += '<li class="py-2" data-toggle="chapters"><strong>Chapters Listened:</strong> ' + item.chapters.length + '</li>';
            const dates = getChapterDates(item);
            if (dates.length > 0) {
                html += '<li class="py-2" data-toggle="chapters"><strong>First Listened:</strong> ' + dates[0].substring(0, 10) + '</li>';
                html += '<li class="py-2" data-toggle="chapters"><strong>Last Listened:</strong> ' + dates[dates.length - 1].substring(0, 10) + '</li>';
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
                    if (ch.device) {
                        deviceCounts[ch.device] = (deviceCounts[ch.device] || 0) + 1;
                    }
                    if (ch.location) {
                        locationCounts[ch.location] = (locationCounts[ch.location] || 0) + 1;
                    }
                });
            }
        });

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Podcasts') + '</div>';
        html += '<div>' + renderStatCard(totalChapters, 'Total Chapters Listened') + '</div>';
        html += '</div>';
        html += renderBarChart('Device Distribution', deviceCounts, {unit: 'chapters'});
        html += renderBarChart('Listening Location', locationCounts, {unit: 'chapters', sort: 'desc', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};

})();
