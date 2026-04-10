/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['audible'] = {
    file: 'data/audible.yaml.gz',
    navTitle: 'Audible',
    title: 'Audible Library',
    subtitle: "A searchable list of my Audible books.",
    ratingScale: 5,
    searchPlaceholder: 'Search by title, author, narrator...',
    searchFields: ['name', 'title', 'authors', 'narrators'],
    fields: [
        {field: 'name', label: 'Title', type: 'string', filterable: false},
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'authors', label: 'Author', type: 'string', filterType: 'select'},
        {field: 'narrators', label: 'Narrator', type: 'string', sortable: false, filterType: 'select'},
        {field: 'date_added', label: 'Date Added', type: 'string', filterType: 'year'},
        {field: 'release_date', label: 'Year Released', type: 'string', sortable: false, filterType: 'year'},
        {field: 'runtime_length_min', label: 'Length', type: 'number',
            value: function(item) { return item.runtime_length_min || 0; },
            filterType: 'range', ranges: [
                {label: 'Short (< 2h)', min: 0, max: 120},
                {label: 'Medium (2-6h)', min: 120, max: 360},
                {label: 'Long (6-12h)', min: 360, max: 720},
                {label: 'Very Long (12-24h)', min: 720, max: 1440},
                {label: 'Epic (24h+)', min: 1440, max: null}
            ]
        },
        {field: 'status', label: 'Status', type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                if (item.is_finished) return 'Finished';
                if (item.percent_complete > 0) return 'In Progress';
                return 'Not Started';
            },
            match: function(item, val) {
                if (val === 'Finished') return !!item.is_finished;
                if (val === 'In Progress') return !item.is_finished && item.percent_complete > 0;
                return !item.is_finished && item.percent_complete <= 0;
            }
        },
        {field: 'genres', label: 'Genre', type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.genres || []; },
            match: function(item, val) { return item.genres && item.genres.indexOf(val) !== -1; }
        },
        {field: 'has_series', label: 'Part of Series', type: 'string', sortable: false,
            filterType: 'boolean',
            value: function(item) { return item.series_title && item.series_title.trim() !== ''; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'authors', label: 'Authors', default: true},
        {key: 'narrators', label: 'Narrators', default: true},
        {key: 'runtime', label: 'Runtime', default: true},
        {key: 'status', label: 'Status', default: true},
        {key: 'series', label: 'Series', default: true},
        {key: 'genres', label: 'Genres', default: false},
        {key: 'released', label: 'Released', default: false},
        {key: 'date_added', label: 'Date Added', default: true}
    ],
    renderImage: function(item) {
        if (!item.asin) return '';
        return 'images/audible-' + encodeURIComponent(item.asin) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.authors) {
            html += '<li class="py-2" data-toggle="authors"><strong>Author(s):</strong> ' + window.escapeHtml(item.authors) + '</li>';
        }
        if (item.narrators) {
            html += '<li class="py-2" data-toggle="narrators"><strong>Narrator(s):</strong> ' + window.escapeHtml(item.narrators) + '</li>';
        }
        if (item.runtime_length_min) {
            var hours = Math.floor(item.runtime_length_min / 60);
            var mins = item.runtime_length_min % 60;
            var runtime = hours > 0 ? hours + 'h ' + mins + 'm' : mins + 'm';
            html += '<li class="py-2" data-toggle="runtime"><strong>Runtime:</strong> ' + window.escapeHtml(runtime) + '</li>';
        }
        let status = 'Not Started';
        if (item.is_finished) {
            status = '<span class="font-bold text-green-600">Finished</span>';
        } else if (item.percent_complete > 0) {
            status = 'In Progress (' + window.escapeHtml(String(item.percent_complete)) + '%)';
        }
        html += '<li class="py-2" data-toggle="status"><strong>Status:</strong> ' + status + '</li>';
        if (item.series_title) {
            var series = item.series_title;
            if (item.series_sequence) series += ' #' + item.series_sequence;
            html += '<li class="py-2" data-toggle="series"><strong>Series:</strong> ' + window.escapeHtml(series) + '</li>';
        }
        if (item.genres && item.genres.length > 0) {
            html += '<li class="py-2" data-toggle="genres"><strong>Genres:</strong> ' + window.escapeHtml(item.genres.join(', ')) + '</li>';
        }
        var releaseDate = this.formatDate(item.release_date);
        if (releaseDate) {
            html += '<li class="py-2" data-toggle="released"><strong>Released:</strong> ' + window.escapeHtml(releaseDate) + '</li>';
        }
        var addedDate = this.formatDate(item.date_added);
        if (addedDate) {
            html += '<li class="py-2" data-toggle="date_added"><strong>Date Added:</strong> ' + window.escapeHtml(addedDate) + '</li>';
        }
        return html;
    },
    renderStats: function(items) {
        let finishedCount = 0;
        let inProgressCount = 0;
        const authorSet = new Set();
        const yearCounts = {};

        items.forEach(function(item) {
            if (item.is_finished) {
                finishedCount++;
            } else {
                inProgressCount++;
            }
            if (item.authors) {
                const authors = typeof item.authors === 'string' ? item.authors.split(',') : [item.authors];
                authors.forEach(function(author) { authorSet.add(author.trim()); });
            }
            const date = this.formatDate(item.date_added);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        const totalBooks = items.length;
        const finishedPct = totalBooks > 0 ? (finishedCount / totalBooks) * 100 : 0;
        const inProgressPct = totalBooks > 0 ? (inProgressCount / totalBooks) * 100 : 0;

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Books') + '</div>';
        html += '<div>' + renderStatCard(authorSet.size, 'Unique Authors') + '</div>';
        html += '</div>';

        html += '<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-4"><div class="px-4 py-3 border-b border-gray-200 font-semibold">Completion Status</div><div class="p-4">';
        html += '<div class="mb-3"><p class="mb-1"><strong>Finished:</strong> ' + finishedCount + ' books</p>';
        html += '<div class="w-full bg-gray-200 rounded-full h-5"><div class="bg-green-600 h-5 rounded-full text-xs text-white text-center leading-5" style="width: ' + finishedPct + '%;">' + Math.round(finishedPct) + '%</div></div></div>';
        html += '<div><p class="mb-1"><strong>In Progress / Unfinished:</strong> ' + inProgressCount + ' books</p>';
        html += '<div class="w-full bg-gray-200 rounded-full h-5"><div class="bg-cyan-500 h-5 rounded-full text-xs text-white text-center leading-5" style="width: ' + inProgressPct + '%;">' + Math.round(inProgressPct) + '%</div></div></div>';
        html += '</div></div>';

        html += renderBarChart('Books Added per Year', yearCounts, {unit: 'books', sort: 'reverse', barClass: 'bg-primary', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
