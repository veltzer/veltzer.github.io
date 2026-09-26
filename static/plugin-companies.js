/* global renderBarChart, renderStatCard */
window.mediaPlugins = window.mediaPlugins || {};

// The one map point per company, chosen by hand in organizations.yaml (see
// scripts/organizations_pick_geo.py). Its place string ends in the country,
// "Ra'anana, Israel", which is what the country filter and chart read.
function companyPlace(item) {
    return item.geo && item.geo.place ? item.geo.place : '';
}

function companyCountry(item) {
    const place = companyPlace(item);
    const comma = place.lastIndexOf(',');
    return comma === -1 ? place : place.substring(comma + 1).trim();
}

// Google Maps URL for a point, per the Maps URLs API: a plain link, so it
// needs no API key and opens the visitor's own maps app on a phone.
function companyMapUrl(item) {
    if (!item.geo) return '';
    return 'https://www.google.com/maps/search/?api=1&query=' +
        encodeURIComponent(item.geo.lat + ',' + item.geo.lon);
}

// The small map on the card is a static image of the same point, rendered
// once from OpenStreetMap tiles by scripts/organizations_fetch_maps.py and
// committed (item.map, one file per distinct point). It replaced a Google
// Maps iframe per card, which loaded a whole maps application for a link
// that is rarely clicked; doc/DECISIONS.md has the comparison. OSM's tile
// policy asks for visible attribution, hence the credit line under it.
function companyMapImage(item) {
    return item.map ? (window.mediaBasePath || './') + item.map : '';
}

function capitalize(text) {
    return text ? text.charAt(0).toUpperCase() + text.substring(1) : '';
}

window.mediaPlugins['companies'] = {
    file: 'data/companies.json.gz',
    navTitle: 'Companies',
    title: 'Companies I Taught At',
    subtitle: 'The organizations I have taught courses at, with where they are and what became of them.',
    ratingScale: null,
    searchPlaceholder: 'Search by name, place, status...',
    searchFields: ['name', 'location', 'israel_office', 'status', 'review', 'remark'],
    fields: [
        {field: 'name', label: 'Name', type: 'string', filterable: false},
        {field: 'status', label: 'Status', type: 'string', filterType: 'select',
            value: function(item) { return capitalize(item.status || ''); }
        },
        {field: 'functions', label: 'Function', type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return (item.functions || []).map(capitalize); },
            match: function(item, val) { return (item.functions || []).map(capitalize).indexOf(val) !== -1; }
        },
        {field: 'place', label: 'Place', type: 'string', filterType: 'select', value: companyPlace},
        {field: 'country', label: 'Country', type: 'string', filterType: 'select', value: companyCountry},
        {field: 'has_website', label: 'Has Website', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.website && item.website.trim() !== ''; }
        },
        {field: 'still_around', label: 'Still Around', type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.status === 'active'; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'status', label: 'Status', default: true},
        {key: 'functions', label: 'Functions', default: true},
        {key: 'location', label: 'Headquarters', default: true},
        {key: 'israel_office', label: 'Israel Office', default: true},
        {key: 'map', label: 'Map', default: true},
        {key: 'website', label: 'Website Link', default: true},
        {key: 'since', label: 'Since', default: true},
        {key: 'remark', label: 'Remark', default: false},
        {key: 'logo_credit', label: 'Logo Credit', default: false}
    ],
    // Every logo sits on the same square transparent canvas, so it is shown
    // whole ('contain') on a light box: most of them are dark marks drawn for
    // a white page and would vanish against a dark theme's card surface.
    renderImage: function(item) {
        return item.logo || '';
    },
    imageFit: 'contain',
    imageBackground: 'light',
    renderDetails: function(item) {
        let html = '';
        if (item.status) {
            html += '<li class="py-2" data-toggle="status"><strong>Status:</strong> ' +
                window.escapeHtml(capitalize(item.status)) + '</li>';
        }
        if (item.functions && item.functions.length > 0) {
            html += '<li class="py-2" data-toggle="functions"><strong>Functions:</strong> ' +
                window.escapeHtml(item.functions.map(capitalize).join(', ')) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>Headquarters:</strong> ' +
                window.escapeHtml(item.location) + '</li>';
        }
        if (item.israel_office) {
            html += '<li class="py-2" data-toggle="israel_office"><strong>Israel office:</strong> ' +
                window.escapeHtml(item.israel_office) + '</li>';
        }
        const mapUrl = companyMapUrl(item);
        if (mapUrl) {
            const mapImage = companyMapImage(item);
            html += '<li class="py-2" data-toggle="map">';
            if (mapImage) {
                html += '<a href="' + window.escapeHtml(mapUrl) + '" target="_blank" rel="noopener noreferrer">' +
                    '<img class="media-card-map" src="' + window.escapeHtml(mapImage) +
                    '" alt="Map of ' + window.escapeHtml(companyPlace(item)) + '" loading="lazy"></a>';
            }
            html += '<a href="' + window.escapeHtml(mapUrl) +
                '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' +
                '&#x1F4CD; ' + window.escapeHtml(companyPlace(item)) + ' on Google Maps</a>';
            if (mapImage) {
                html += '<span class="media-card-map-credit">Map &copy; <a href="https://www.openstreetmap.org/copyright"' +
                    ' target="_blank" rel="noopener noreferrer" class="underline">OpenStreetMap</a> contributors</span>';
            }
            html += '</li>';
        }
        if (item.website) {
            html += '<li class="py-2" data-toggle="website"><a href="' + window.escapeHtml(item.website) +
                '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' +
                '&#x1F517; Visit Website</a></li>';
        }
        if (item.from_date) {
            html += '<li class="py-2" data-toggle="since"><strong>Since:</strong> ' +
                window.escapeHtml(item.from_date) + '</li>';
        }
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>Remark:</strong> ' +
                window.escapeHtml(item.remark) + '</li>';
        }
        if (item.logo_kind) {
            let credit = window.escapeHtml(capitalize(item.logo_kind));
            if (item.logo_source) {
                credit += ' (<a href="' + window.escapeHtml(item.logo_source) +
                    '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">source</a>)';
            }
            if (item.logo_license) {
                credit += ', ' + window.escapeHtml(item.logo_license);
            }
            html += '<li class="py-2 text-sm text-gray-500" data-toggle="logo_credit"><strong>Logo:</strong> ' + credit + '</li>';
        }
        return html;
    },
    renderStats: function(items) {
        const statusCounts = {};
        const functionCounts = {};
        const placeCounts = {};
        let stillAround = 0;

        items.forEach(function(item) {
            const status = capitalize(item.status || 'unknown');
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            if (item.status === 'active') stillAround += 1;
            (item.functions || []).forEach(function(fn) {
                const label = capitalize(fn);
                functionCounts[label] = (functionCounts[label] || 0) + 1;
            });
            const place = companyPlace(item);
            if (place) {
                placeCounts[place] = (placeCounts[place] || 0) + 1;
            }
        });

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Companies') + '</div>';
        html += '<div>' + renderStatCard(stillAround, 'Still Active') + '</div>';
        html += '</div>';
        html += renderBarChart('By Status', statusCounts, {unit: 'companies', sort: 'desc'});
        html += renderBarChart('By Function', functionCounts, {unit: 'companies', sort: 'desc', barClass: 'bg-success'});
        html += renderBarChart('By Place', placeCounts, {unit: 'companies', sort: 'desc', limit: 25, last: true});
        return html;
    }
};
