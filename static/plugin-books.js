/* global t, renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

// Data comes flattened by scripts/import_books.py: one item per book with
// string fields for the card and search box (name, authors, review) and the
// small lists the filters and stats need (author_list, readings,
// languages_read, owned_languages). rating/last_read/review belong to the
// most recent dated reading; books migrated from the old xml catalog only
// carry `undated: true` readings and have none of the three.

function bookYear(item) {
    return item.last_read ? String(item.last_read).substring(0, 4) : null;
}

function bookReadingLine(reading) {
    let line = reading.language ? reading.language.charAt(0).toUpperCase() + reading.language.slice(1) : '?';
    if (reading.date) {
        line += ', ' + mediaFormatDate(reading.date);
    } else if (reading.undated) {
        line += ', ' + t('books_date_unknown');
    }
    if (reading.rating !== undefined && reading.rating !== null) {
        line += ' (' + reading.rating + '/10)';
    }
    return line;
}

window.collectionPlugins['books'] = {
    file: 'data/books.json.gz',
    navTitle: t('books_nav_title'),
    title: t('books_title'),
    subtitle: t('books_subtitle'),
    // Ratings live on readings and many books have none, so they are rendered
    // in renderDetails rather than by the generic "Rating: ? / 10" line.
    ratingScale: null,
    searchPlaceholder: t('books_search_placeholder'),
    searchFields: ['name', 'name_he', 'authors', 'review', 'remark'],
    fields: [
        {field: 'name', label: t('books_f_title'), type: 'string', filterable: false},
        {field: 'authors', label: t('books_f_author'), type: 'string',
            filterType: 'custom',
            extractValues: function(item) { return item.author_list || []; },
            match: function(item, val) { return item.author_list && item.author_list.indexOf(val) !== -1; }
        },
        {field: 'rating', label: t('books_f_rating'), type: 'number', filterType: 'select'},
        {field: 'last_read', label: t('books_f_date_read'), type: 'string', filterType: 'year'},
        {field: 'language', label: t('books_f_original_language'), type: 'string', filterType: 'select'},
        {field: 'languages_read', label: t('books_f_read_in'), type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.languages_read || []; },
            match: function(item, val) { return item.languages_read && item.languages_read.indexOf(val) !== -1; }
        },
        {field: 'read_count', label: t('books_f_times_read'), type: 'number', filterType: 'select'},
        {field: 'owned', label: t('books_f_owned'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.owned_languages && item.owned_languages.length > 0; }
        },
        {field: 'has_review', label: t('books_f_has_review'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'dated', label: t('books_f_has_date'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return !!item.last_read; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'authors', label: t('books_tg_authors'), default: true},
        {key: 'rating', label: t('books_tg_rating'), default: true},
        {key: 'language', label: t('books_tg_language'), default: true},
        {key: 'readings', label: t('books_tg_readings'), default: true},
        {key: 'owned', label: t('books_tg_owned'), default: true},
        {key: 'publisher', label: t('books_tg_publisher'), default: false},
        {key: 'remark', label: t('books_tg_remark'), default: true},
        {key: 'link', label: t('books_tg_link'), default: true}
    ],
    // Covers/posters are 2:3 portrait; see imageFit in data-collection-app.js.
    imageFit: 'contain',
    renderImage: function(item) {
        // No cover key means neither goodreads nor simania has an image for
        // the book (import_books.NO_COVER); show the placeholder rather than
        // an empty card top or a broken image.
        if (!item.cover) return 'images/book-no-cover.jpg';
        return 'images/book-' + encodeURIComponent(item.cover) + '.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.name_he) {
            html += '<li class="py-2" dir="rtl"><strong>' + window.escapeHtml(item.name_he) + '</strong></li>';
        }
        if (item.authors) {
            html += '<li class="py-2" data-toggle="authors"><strong>' + t('books_d_authors') + '</strong> ' + window.escapeHtml(item.authors) + '</li>';
        }
        if (item.rating !== undefined && item.rating !== null) {
            html += '<li class="py-2" data-toggle="rating"><strong>' + t('books_d_rating') + '</strong> <span class="inline-block bg-blue-600 text-white text-sm font-semibold px-2.5 py-0.5 rounded-full">' + window.escapeHtml(String(item.rating)) + ' / 10</span></li>';
        }
        if (item.language) {
            html += '<li class="py-2" data-toggle="language"><strong>' + t('books_d_original_language') + '</strong> ' + window.escapeHtml(item.language) + '</li>';
        }
        if (item.readings && item.readings.length > 0) {
            html += '<li class="py-2" data-toggle="readings"><strong>' + t('books_d_read') + '</strong> ' +
                item.readings.map(function(r) { return window.escapeHtml(bookReadingLine(r)); }).join('; ') + '</li>';
        }
        if (item.owned_languages && item.owned_languages.length > 0) {
            html += '<li class="py-2" data-toggle="owned"><strong>' + t('books_d_owned_in') + '</strong> ' + window.escapeHtml(item.owned_languages.join(', ')) + '</li>';
        }
        if (item.publisher) {
            html += '<li class="py-2" data-toggle="publisher"><strong>' + t('books_d_publisher') + '</strong> ' + window.escapeHtml(item.publisher) + '</li>';
        }
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>' + t('books_d_remark') + '</strong> ' + window.escapeHtml(item.remark) + '</li>';
        }
        if (item.url) {
            const site = item.simania_id ? 'simania' : 'goodreads';
            html += '<li class="py-2" data-toggle="link"><a href="' + window.escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; ' + t('books_view_on', {site: site}) + '</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const authorSet = new Set();
        const yearCounts = {};
        const languageCounts = {};
        const ratingCounts = {};
        const authorCounts = {};
        let readings = 0;
        let undated = 0;
        let owned = 0;

        items.forEach(function(item) {
            (item.author_list || []).forEach(function(author) {
                authorSet.add(author);
                authorCounts[author] = (authorCounts[author] || 0) + 1;
            });
            const year = bookYear(item);
            if (year) {
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            } else if (item.read_count > 0) {
                undated++;
            }
            if (item.language) {
                languageCounts[item.language] = (languageCounts[item.language] || 0) + 1;
            }
            if (item.rating !== undefined && item.rating !== null) {
                ratingCounts[item.rating] = (ratingCounts[item.rating] || 0) + 1;
            }
            readings += item.read_count || 0;
            if (item.owned_languages && item.owned_languages.length > 0) owned++;
        });

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('books_total_books')) + '</div>';
        html += '<div>' + renderStatCard(readings, t('books_total_readings')) + '</div>';
        html += '<div>' + renderStatCard(authorSet.size, t('books_unique_authors')) + '</div>';
        html += '<div>' + renderStatCard(owned, t('books_f_owned')) + '</div>';
        html += '</div>';

        html += renderBarChart(t('books_per_year', {undated: undated}), yearCounts, {unit: t('books_unit'), sort: 'reverse', barClass: 'bg-primary'});
        html += renderBarChart(t('books_by_language'), languageCounts, {unit: t('books_unit'), sort: 'desc'});
        html += renderBarChart(t('books_ratings'), ratingCounts, {unit: t('books_unit'), sort: 'alpha'});
        html += renderBarChart(t('books_top_authors'), authorCounts, {unit: t('books_unit'), sort: 'desc', limit: 15, barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
