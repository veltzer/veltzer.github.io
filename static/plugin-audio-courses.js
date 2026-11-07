/* global t, renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

(function() {
    function getDate(item) {
        return item.date_utcz || item.date_ended_utcz || item.date_started_utcz || '';
    }

window.collectionPlugins['audio'] = {
    file: 'data/audio_courses.json.gz',
    navTitle: t('audio_nav_title'),
    title: t('audio_title'),
    subtitle: t('audio_subtitle'),
    ratingScale: 10,
    searchPlaceholder: t('audio_search_placeholder'),
    searchFields: ['name', 'review', 'lecturers', 'location'],
    fields: [
        {field: 'name', label: t('audio_f_name'), type: 'string', filterable: false},
        {field: 'rating', label: t('audio_f_rating'), type: 'number', filterType: 'select'},
        {field: 'location', label: t('audio_f_location'), type: 'string', filterType: 'select'},
        {field: 'date', label: t('audio_f_date'), type: 'string', value: getDate, filterType: 'year'},
        {field: 'device', label: t('audio_f_device'), type: 'string', filterType: 'select'},
        {field: 'progress', label: t('audio_f_progress'), type: 'string', filterType: 'select'},
        {field: 'lecturers', label: t('audio_f_lecturer'), type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.lecturers || []; },
            match: function(item, val) { return item.lecturers && item.lecturers.some(function(l) { return l === val; }); }
        },
        {field: 'has_review', label: t('audio_f_has_review'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'source', label: t('audio_f_source'), type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                if (item.great_courses_id) return t('audio_source_great_courses');
                if (item.audible_asin) return t('audio_source_audible');
                return t('audio_source_other');
            },
            match: function(item, val) {
                if (val === t('audio_source_great_courses')) return !!item.great_courses_id;
                if (val === t('audio_source_audible')) return !!item.audible_asin;
                return !item.great_courses_id && !item.audible_asin;
            }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'lecturers', label: t('audio_tg_lecturers'), default: true},
        {key: 'date', label: t('audio_tg_date'), default: true},
        {key: 'location', label: t('audio_tg_location'), default: true},
        {key: 'progress', label: t('audio_tg_progress'), default: true},
        {key: 'links', label: t('audio_tg_links'), default: true}
    ],
    // Shown when a course has no id to name an image by, and by data-collection-app.js
    // when the named file turns out not to exist (a course added to the YAML
    // before scripts/fetch_audiocourse_images.py has been run for it).
    placeholderImage: 'images/audiocourse-no-cover.jpg',
    renderImage: function(item) {
        if (item.great_courses_id) {
            return 'images/audiocourse-gc-' + encodeURIComponent(item.great_courses_id) + '.jpg';
        }
        if (item.audible_asin) {
            return 'images/audiocourse-audible-' + encodeURIComponent(item.audible_asin) + '.jpg';
        }
        if (item.internal_id) {
            return 'images/audiocourse-internal-' + encodeURIComponent(item.internal_id) + '.jpg';
        }
        return this.placeholderImage;
    },
    renderDetails: function(item) {
        const lecturers = item.lecturers ? item.lecturers.join(', ') : t('audio_na');
        let html = '<li class="py-2" data-toggle="lecturers"><strong>' + t('audio_d_lecturers') + '</strong> ' + window.escapeHtml(lecturers) + '</li>';
        const date = this.formatDate(item.date_utcz || item.date_ended_utcz || item.date_started_utcz);
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>' + t('audio_d_date') + '</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>' + t('audio_d_location') + '</strong> ' + window.escapeHtml(item.location) + '</li>';
        }
        if (item.progress) {
            html += '<li class="py-2" data-toggle="progress"><strong>' + t('audio_d_progress') + '</strong> ' + window.escapeHtml(item.progress) + '</li>';
        }
        if (item.great_courses_slug) {
            html += '<li class="py-2" data-toggle="links"><a href="https://shop.thegreatcourses.com/' + window.escapeHtml(item.great_courses_slug) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('audio_view_great_courses') + '</a></li>';
        }
        if (item.audible_asin) {
            html += '<li class="py-2" data-toggle="links"><a href="https://www.audible.com/pd/' + window.escapeHtml(item.audible_asin) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('audio_view_audible') + '</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const deviceCounts = {};
        const yearCounts = {};
        const lecturerSet = new Set();
        items.forEach(function(item) {
            if (item.device) {
                deviceCounts[item.device] = (deviceCounts[item.device] || 0) + 1;
            }
            if (item.lecturers) {
                item.lecturers.forEach(function(lecturer) {
                    lecturerSet.add(lecturer);
                });
            }
            const date = this.formatDate(item.date_utcz || item.date_ended_utcz || item.date_started_utcz);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('audio_total_courses')) + '</div>';
        html += '<div>' + renderStatCard(lecturerSet.size, t('audio_unique_lecturers')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('audio_device_distribution'), deviceCounts);
        html += renderBarChart(t('audio_items_per_year'), yearCounts, {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};

})();
