/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

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
        line += ', date unknown';
    }
    if (reading.rating !== undefined && reading.rating !== null) {
        line += ' (' + reading.rating + '/10)';
    }
    return line;
}

window.mediaPlugins['books'] = {
    file: 'data/books.json.gz',
    navTitle: 'Books',
    title: 'Books Read',
    subtitle: "The books I've read, and a few I own and have not got to yet.",
    // Ratings live on readings and many books have none, so they are rendered
    // in renderDetails rather than by the generic "Rating: ? / 10" line.
    ratingScale: null,
    searchPlaceholder: 'Search by title, author, review...',
    searchFields: ['name', 'name_he', 'authors', 'review', 'remark'],
    fields: [
        {field: 'name', label: 'Title', type: 'string', filterable: false},
        {field: 'authors', label: 'Author', type: 'string',
            filterType: 'custom',
            extractValues: function(item) { return item.author_list || []; },
            match: function(item, val) { return item.author_list && item.author_list.indexOf(val) !== -1; }
        },
        {field: 'rating', label: 'Rating', type: 'number', filterType: 'select'},
        {field: 'last_read', label: 'Date Read', type: 'string', filterType: 'year'},
        {field: 'language', label: 'Original Language', type: 'string', filterType: 'select'},
        {field: 'languages_read', label: 'Read In', type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return item.languages_read || []; },
            match: function(item, val) { return item.languages_read && item.languages_read.indexOf(val) !== -1; }
        },
        {field: 'read_count', label: 'Times Read', type: 'number', filterType: 'select'},
        {field: 'owned', label: 'Owned', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.owned_languages && item.owned_languages.length > 0; }
        },
        {field: 'has_review', label: 'Has Review', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.review && item.review.trim() !== ''; }
        },
        {field: 'dated', label: 'Has Date', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return !!item.last_read; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'authors', label: 'Authors', default: true},
        {key: 'rating', label: 'Rating', default: true},
        {key: 'language', label: 'Language', default: true},
        {key: 'readings', label: 'Readings', default: true},
        {key: 'owned', label: 'Owned', default: true},
        {key: 'publisher', label: 'Publisher', default: false},
        {key: 'remark', label: 'Remark', default: true},
        {key: 'link', label: 'Link', default: true}
    ],
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
            html += '<li class="py-2" data-toggle="authors"><strong>Author(s):</strong> ' + window.escapeHtml(item.authors) + '</li>';
        }
        if (item.rating !== undefined && item.rating !== null) {
            html += '<li class="py-2" data-toggle="rating"><strong>Rating:</strong> <span class="inline-block bg-blue-600 text-white text-sm font-semibold px-2.5 py-0.5 rounded-full">' + window.escapeHtml(String(item.rating)) + ' / 10</span></li>';
        }
        if (item.language) {
            html += '<li class="py-2" data-toggle="language"><strong>Original language:</strong> ' + window.escapeHtml(item.language) + '</li>';
        }
        if (item.readings && item.readings.length > 0) {
            html += '<li class="py-2" data-toggle="readings"><strong>Read:</strong> ' +
                item.readings.map(function(r) { return window.escapeHtml(bookReadingLine(r)); }).join('; ') + '</li>';
        }
        if (item.owned_languages && item.owned_languages.length > 0) {
            html += '<li class="py-2" data-toggle="owned"><strong>Owned in:</strong> ' + window.escapeHtml(item.owned_languages.join(', ')) + '</li>';
        }
        if (item.publisher) {
            html += '<li class="py-2" data-toggle="publisher"><strong>Publisher:</strong> ' + window.escapeHtml(item.publisher) + '</li>';
        }
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>Remark:</strong> ' + window.escapeHtml(item.remark) + '</li>';
        }
        if (item.url) {
            const site = item.simania_id ? 'simania' : 'goodreads';
            html += '<li class="py-2" data-toggle="link"><a href="' + window.escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; View on ' + site + '</a></li>';
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
        html += '<div>' + renderStatCard(items.length, 'Total Books') + '</div>';
        html += '<div>' + renderStatCard(readings, 'Total Readings') + '</div>';
        html += '<div>' + renderStatCard(authorSet.size, 'Unique Authors') + '</div>';
        html += '<div>' + renderStatCard(owned, 'Owned') + '</div>';
        html += '</div>';

        html += renderBarChart('Books Read per Year (' + undated + ' read before dates were kept)', yearCounts, {unit: 'books', sort: 'reverse', barClass: 'bg-primary'});
        html += renderBarChart('By Original Language', languageCounts, {unit: 'books', sort: 'desc'});
        html += renderBarChart('Ratings', ratingCounts, {unit: 'books', sort: 'alpha'});
        html += renderBarChart('Most Read Authors', authorCounts, {unit: 'books', sort: 'desc', limit: 15, barClass: 'bg-success', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
