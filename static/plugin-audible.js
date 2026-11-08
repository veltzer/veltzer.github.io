/* global t, renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

window.collectionPlugins['audible'] = {
    file: 'data/audible.json.gz',
    navTitle: t('audible_nav_title'),
    title: t('audible_title'),
    subtitle: t('audible_subtitle'),
    ratingScale: 5,
    searchPlaceholder: t('audible_search_placeholder'),
    searchFields: ['name', 'title', 'authors', 'narrators'],
    fields: [
        {field: 'name', label: t('audible_f_title'), type: 'string', filterable: false},
        {field: 'rating', label: t('audible_f_rating'), type: 'number', filterType: 'select'},
        {field: 'authors', label: t('audible_f_author'), type: 'string', filterType: 'select'},
        {field: 'narrators', label: t('audible_f_narrator'), type: 'string', sortable: false, filterType: 'select'},
        {field: 'date_added', label: t('audible_f_date_added'), type: 'string', filterType: 'year'},
        {field: 'release_date', label: t('audible_f_year_released'), type: 'string', sortable: false, filterType: 'year'},
        {field: 'runtime_length_min', label: t('audible_f_length'), type: 'number',
            value: function(item) { return item.runtime_length_min || 0; },
            filterType: 'range', ranges: [
                {label: t('audible_len_short'), min: 0, max: 120},
                {label: t('audible_len_medium'), min: 120, max: 360},
                {label: t('audible_len_long'), min: 360, max: 720},
                {label: t('audible_len_very_long'), min: 720, max: 1440},
                {label: t('audible_len_epic'), min: 1440, max: null}
            ]
        },
        {field: 'status', label: t('audible_f_status'), type: 'string', sortable: false,
            filterType: 'custom',
            value: function(item) {
                if (item.is_finished) return t('audible_status_finished');
                if (item.percent_complete > 0) return t('audible_status_in_progress');
                return t('audible_status_not_started');
            },
            match: function(item, val) {
                if (val === t('audible_status_finished')) return !!item.is_finished;
                if (val === t('audible_status_in_progress')) return !item.is_finished && item.percent_complete > 0;
                return !item.is_finished && item.percent_complete <= 0;
            }
        },
        {field: 'genres', label: t('audible_f_genre'), type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.genres || []; },
            match: function(item, val) { return item.genres && item.genres.indexOf(val) !== -1; }
        },
        {field: 'has_series', label: t('audible_f_part_of_series'), type: 'string', sortable: false,
            filterType: 'boolean',
            value: function(item) { return item.series_title && item.series_title.trim() !== ''; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'authors', label: t('audible_tg_authors'), default: true},
        {key: 'narrators', label: t('audible_tg_narrators'), default: true},
        {key: 'runtime', label: t('audible_tg_runtime'), default: true},
        {key: 'status', label: t('audible_tg_status'), default: true},
        {key: 'series', label: t('audible_tg_series'), default: true},
        {key: 'genres', label: t('audible_tg_genres'), default: false},
        {key: 'released', label: t('audible_tg_released'), default: false},
        {key: 'date_added', label: t('audible_tg_date_added'), default: true}
    ],
    renderImage: function(item) {
        if (!item.asin) return '';
        return 'images/audible-' + encodeURIComponent(item.asin) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.authors) {
            html += '<li class="py-2" data-toggle="authors"><strong>' + t('audible_d_authors') + ':</strong> ' + window.escapeHtml(item.authors) + '</li>';
        }
        if (item.narrators) {
            html += '<li class="py-2" data-toggle="narrators"><strong>' + t('audible_d_narrators') + ':</strong> ' + window.escapeHtml(item.narrators) + '</li>';
        }
        if (item.runtime_length_min) {
            var hours = Math.floor(item.runtime_length_min / 60);
            var mins = item.runtime_length_min % 60;
            var runtime = hours > 0 ? t('audible_runtime_hm', {hours: hours, mins: mins}) : t('audible_runtime_m', {mins: mins});
            html += '<li class="py-2" data-toggle="runtime"><strong>' + t('audible_d_runtime') + ':</strong> ' + window.escapeHtml(runtime) + '</li>';
        }
        let status = t('audible_status_not_started');
        if (item.is_finished) {
            status = '<span class="font-bold text-green-600">' + t('audible_status_finished') + '</span>';
        } else if (item.percent_complete > 0) {
            status = window.escapeHtml(t('audible_status_in_progress_pct', {percent: String(item.percent_complete)}));
        }
        html += '<li class="py-2" data-toggle="status"><strong>' + t('audible_d_status') + ':</strong> ' + status + '</li>';
        if (item.series_title) {
            var series = item.series_title;
            if (item.series_sequence) series += ' #' + item.series_sequence;
            html += '<li class="py-2" data-toggle="series"><strong>' + t('audible_d_series') + ':</strong> ' + window.escapeHtml(series) + '</li>';
        }
        if (item.genres && item.genres.length > 0) {
            html += '<li class="py-2" data-toggle="genres"><strong>' + t('audible_d_genres') + ':</strong> ' + window.escapeHtml(item.genres.join(', ')) + '</li>';
        }
        var releaseDate = this.formatDate(item.release_date);
        if (releaseDate) {
            html += '<li class="py-2" data-toggle="released"><strong>' + t('audible_d_released') + ':</strong> ' + window.escapeHtml(releaseDate) + '</li>';
        }
        var addedDate = this.formatDate(item.date_added);
        if (addedDate) {
            html += '<li class="py-2" data-toggle="date_added"><strong>' + t('audible_d_date_added') + ':</strong> ' + window.escapeHtml(addedDate) + '</li>';
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
        html += '<div>' + renderStatCard(items.length, t('audible_stat_total_books')) + '</div>';
        html += '<div>' + renderStatCard(authorSet.size, t('audible_stat_unique_authors')) + '</div>';
        html += '</div>';

        html += '<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-4"><div class="px-4 py-3 border-b border-gray-200 font-semibold">' + t('audible_completion_status') + '</div><div class="p-4">';
        html += '<div class="mb-3"><p class="mb-1"><strong>' + t('audible_finished') + ':</strong> ' + t(finishedCount === 1 ? 'audible_books_count_one' : 'audible_books_count_other', {count: finishedCount}) + '</p>';
        html += '<div class="w-full bg-gray-200 rounded-full h-5"><div class="bg-green-600 h-5 rounded-full text-xs text-white text-center leading-5" style="width: ' + finishedPct + '%;">' + Math.round(finishedPct) + '%</div></div></div>';
        html += '<div><p class="mb-1"><strong>' + t('audible_in_progress_unfinished') + ':</strong> ' + t(inProgressCount === 1 ? 'audible_books_count_one' : 'audible_books_count_other', {count: inProgressCount}) + '</p>';
        html += '<div class="w-full bg-gray-200 rounded-full h-5"><div class="bg-blue-500 h-5 rounded-full text-xs text-white text-center leading-5" style="width: ' + inProgressPct + '%;">' + Math.round(inProgressPct) + '%</div></div></div>';
        html += '</div></div>';

        html += renderBarChart(t('audible_books_per_year'), yearCounts, {unit: t('audible_unit_books'), sort: 'reverse', barClass: 'bg-primary', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
