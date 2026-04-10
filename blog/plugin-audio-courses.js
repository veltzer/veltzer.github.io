/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

(function() {
    function getDate(item) {
        return item.date_utcz || item.date_ended_utcz || item.date_started_utcz || '';
    }

window.mediaPlugins['audio'] = {
    file: 'data/audio_courses.yaml.gz',
    navTitle: 'Audio Courses',
    title: 'Listened to Audio Courses',
    subtitle: "A searchable list of audio courses I've listened to.",
    ratingScale: 10,
    searchPlaceholder: 'Search by name, review, lecturer...',
    searchFields: ['name', 'review', 'lecturers', 'location'],
    fields: [
        {field: 'name', label: 'Name', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'location', label: 'Location', type: 'string', filterType: 'select'},
        {field: 'date', label: 'Date', type: 'string', value: getDate, filterType: 'year'},
        {field: 'device', label: 'Device', type: 'string', filterType: 'select'},
        {field: 'progress', label: 'Progress', type: 'string', filterType: 'select'},
        {field: 'lecturers', label: 'Lecturer', type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.lecturers || []; },
            match: function(item, val) { return item.lecturers && item.lecturers.some(function(l) { return l === val; }); }
        },
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'source', label: 'Source', type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                if (item.great_courses_id) return 'Great Courses';
                if (item.audible_asin) return 'Audible';
                return 'Other';
            },
            match: function(item, val) {
                if (val === 'Great Courses') return !!item.great_courses_id;
                if (val === 'Audible') return !!item.audible_asin;
                return !item.great_courses_id && !item.audible_asin;
            }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'lecturers', label: 'Lecturers', default: true},
        {key: 'date', label: 'Date', default: true},
        {key: 'location', label: 'Location', default: true},
        {key: 'progress', label: 'Progress', default: true},
        {key: 'links', label: 'Links', default: true}
    ],
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
        return '';
    },
    renderDetails: function(item) {
        const lecturers = item.lecturers ? item.lecturers.join(', ') : 'N/A';
        let html = '<li class="py-2" data-toggle="lecturers"><strong>Lecturer(s):</strong> ' + window.escapeHtml(lecturers) + '</li>';
        const date = this.formatDate(item.date_utcz || item.date_ended_utcz || item.date_started_utcz);
        if (date) {
            html += '<li class="py-2" data-toggle="date"><strong>Date:</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>Location:</strong> ' + window.escapeHtml(item.location) + '</li>';
        }
        if (item.progress) {
            html += '<li class="py-2" data-toggle="progress"><strong>Progress:</strong> ' + window.escapeHtml(item.progress) + '</li>';
        }
        if (item.great_courses_slug) {
            html += '<li class="py-2" data-toggle="links"><a href="https://shop.thegreatcourses.com/' + window.escapeHtml(item.great_courses_slug) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; View on The Great Courses</a></li>';
        }
        if (item.audible_asin) {
            html += '<li class="py-2" data-toggle="links"><a href="https://www.audible.com/pd/' + window.escapeHtml(item.audible_asin) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; View on Audible</a></li>';
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
        html += '<div>' + renderStatCard(items.length, 'Total Courses') + '</div>';
        html += '<div>' + renderStatCard(lecturerSet.size, 'Unique Lecturers') + '</div>';
        html += '</div>';
        html += renderBarChart('Device Distribution', deviceCounts);
        html += renderBarChart('Items per Year', yearCounts, {sort: 'reverse', barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};

})();
