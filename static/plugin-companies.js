/* global renderBarChart, renderStatCard, t */
window.collectionPlugins = window.collectionPlugins || {};

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
    return item.map ? (window.collectionBasePath || './') + item.map : '';
}

function capitalize(text) {
    return text ? text.charAt(0).toUpperCase() + text.substring(1) : '';
}

// The YAML values for status, function and logo kind are identifiers: each is
// shown through its own translated string, and a value with no string yet
// falls back to the capitalized code rather than logging a missing key.
function enumLabel(prefix, code) {
    const key = 'companies_' + prefix + '_' + String(code).replace(/[^a-z0-9]+/g, '_');
    const strings = window.collectionStrings || {};
    return strings['app_' + key] !== undefined ? t(key) : capitalize(code);
}

function statusLabel(status) {
    return enumLabel('status', status);
}

function functionLabel(fn) {
    return enumLabel('function', fn);
}

// The line under a company's name: what happened to it (research notes in
// the data, English like the rest of it), or, when nothing did, a word on its
// status in the page's language.
function companyBlurb(item) {
    if (item.what_happened) {
        return item.what_happened;
    }
    const status = item.status || 'unknown';
    const strings = window.collectionStrings || {};
    if (strings['app_companies_blurb_' + status] !== undefined) {
        return t('companies_blurb_' + status);
    }
    return statusLabel(status) + '.';
}

// The logo kinds are sentences in the YAML; matched on their leading words.
function logoKindLabel(kind) {
    if (kind.indexOf('official vector') === 0) return t('companies_logo_kind_official');
    if (kind.indexOf('traced from original bitmap') === 0) return t('companies_logo_kind_traced');
    if (kind.indexOf('wordmark') === 0) return t('companies_logo_kind_wordmark');
    return capitalize(kind);
}

window.collectionPlugins['companies'] = {
    file: 'data/companies.json.gz',
    navTitle: t('companies_nav_title'),
    title: t('companies_title'),
    subtitle: t('companies_subtitle'),
    ratingScale: null,
    searchPlaceholder: t('companies_search_placeholder'),
    searchFields: ['name', 'location', 'israel_office', 'address', 'status', 'review', 'remark'],
    prepareItem: function(item) {
        item.review = companyBlurb(item);
    },
    fields: [
        {field: 'name', label: t('companies_field_name'), type: 'string', filterable: false},
        {field: 'status', label: t('companies_field_status'), type: 'string', filterType: 'select',
            value: function(item) { return item.status ? statusLabel(item.status) : ''; }
        },
        {field: 'functions', label: t('companies_field_function'), type: 'string', sortable: false,
            filterType: 'custom',
            extractValues: function(item) { return (item.functions || []).map(functionLabel); },
            match: function(item, val) { return (item.functions || []).map(functionLabel).indexOf(val) !== -1; }
        },
        {field: 'place', label: t('companies_field_place'), type: 'string', filterType: 'select', value: companyPlace},
        {field: 'country', label: t('companies_field_country'), type: 'string', filterType: 'select', value: companyCountry},
        {field: 'has_website', label: t('companies_field_has_website'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.website && item.website.trim() !== ''; }
        },
        {field: 'still_around', label: t('companies_field_still_around'), type: 'string', sortable: false,
            filterType: 'boolean', value: function(item) { return item.status === 'active'; }
        }
    ],
    defaultSort: {field: 'name', order: 'asc'},
    toggleFields: [
        {key: 'status', label: t('companies_toggle_status'), default: true},
        {key: 'functions', label: t('companies_toggle_functions'), default: true},
        {key: 'location', label: t('companies_toggle_headquarters'), default: true},
        {key: 'israel_office', label: t('companies_toggle_israel_office'), default: true},
        {key: 'address', label: t('companies_toggle_address'), default: true},
        {key: 'map', label: t('companies_toggle_map'), default: true},
        {key: 'website', label: t('companies_toggle_website'), default: true},
        {key: 'since', label: t('companies_toggle_since'), default: true},
        {key: 'remark', label: t('companies_toggle_remark'), default: false},
        {key: 'logo_credit', label: t('companies_toggle_logo_credit'), default: false}
    ],
    // Every logo sits on the same square transparent canvas, so it is shown
    // whole ('contain') on a light box: most of them are dark marks drawn for
    // a white page and would vanish against a dark theme's card surface.
    renderImage: function(item) {
        return item.logo || '';
    },
    imageFit: 'contain',
    imageBackground: 'light',
    // Data values are wrapped in <bdi>: on a Hebrew page an English address
    // such as "1704 Eaton Drive, Grand Haven" would otherwise be reordered
    // around the Hebrew label.
    renderDetails: function(item) {
        let html = '';
        if (item.status) {
            html += '<li class="py-2" data-toggle="status"><strong>' + t('companies_detail_status') + '</strong> ' +
                window.escapeHtml(statusLabel(item.status)) + '</li>';
        }
        if (item.functions && item.functions.length > 0) {
            html += '<li class="py-2" data-toggle="functions"><strong>' + t('companies_detail_functions') + '</strong> ' +
                window.escapeHtml(item.functions.map(functionLabel).join(', ')) + '</li>';
        }
        if (item.location) {
            html += '<li class="py-2" data-toggle="location"><strong>' + t('companies_detail_headquarters') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.location) + '</bdi></li>';
        }
        if (item.israel_office) {
            html += '<li class="py-2" data-toggle="israel_office"><strong>' + t('companies_detail_israel_office') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.israel_office) + '</bdi></li>';
        }
        if (item.address) {
            html += '<li class="py-2" data-toggle="address"><strong>' + t('companies_detail_address') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.address) + '</bdi></li>';
        }
        const mapUrl = companyMapUrl(item);
        if (mapUrl) {
            const mapImage = companyMapImage(item);
            html += '<li class="py-2" data-toggle="map">';
            if (mapImage) {
                html += '<a href="' + window.escapeHtml(mapUrl) + '" target="_blank" rel="noopener noreferrer">' +
                    '<img class="collection-card-map" src="' + window.escapeHtml(mapImage) +
                    '" alt="' + window.escapeHtml(t('companies_map_alt', {place: companyPlace(item)})) + '" loading="lazy"></a>';
            }
            html += '<a href="' + window.escapeHtml(mapUrl) +
                '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' +
                '&#x1F4CD; ' + window.escapeHtml(t('companies_on_google_maps', {place: '\u2068' + companyPlace(item) + '\u2069'})) + '</a>';
            if (mapImage) {
                html += '<span class="collection-card-map-credit">' + t('companies_map_credit', {
                    osm: '<a href="https://www.openstreetmap.org/copyright" target="_blank"' +
                        ' rel="noopener noreferrer" class="underline">OpenStreetMap</a>'}) + '</span>';
            }
            html += '</li>';
        }
        if (item.website) {
            html += '<li class="py-2" data-toggle="website"><a href="' + window.escapeHtml(item.website) +
                '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' +
                '&#x1F517; ' + window.escapeHtml(t('companies_visit_website')) + '</a></li>';
        }
        if (item.from_date) {
            html += '<li class="py-2" data-toggle="since"><strong>' + t('companies_detail_since') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.from_date) + '</bdi></li>';
        }
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>' + t('companies_detail_remark') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.remark) + '</bdi></li>';
        }
        if (item.logo_kind) {
            let credit = window.escapeHtml(logoKindLabel(item.logo_kind));
            if (item.logo_source) {
                credit += ' (<a href="' + window.escapeHtml(item.logo_source) +
                    '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' + window.escapeHtml(t('companies_logo_source')) + '</a>)';
            }
            if (item.logo_license) {
                credit += ', ' + window.escapeHtml(item.logo_license);
            }
            html += '<li class="py-2 text-sm text-gray-500" data-toggle="logo_credit"><strong>' + t('companies_detail_logo') + '</strong> ' + credit + '</li>';
        }
        return html;
    },
    renderStats: function(items) {
        const statusCounts = {};
        const functionCounts = {};
        const placeCounts = {};
        let stillAround = 0;

        items.forEach(function(item) {
            const status = statusLabel(item.status || 'unknown');
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            if (item.status === 'active') stillAround += 1;
            (item.functions || []).forEach(function(fn) {
                const label = functionLabel(fn);
                functionCounts[label] = (functionCounts[label] || 0) + 1;
            });
            const place = companyPlace(item);
            if (place) {
                placeCounts[place] = (placeCounts[place] || 0) + 1;
            }
        });

        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('companies_stat_organizations')) + '</div>';
        html += '<div>' + renderStatCard(stillAround, t('companies_stat_still_active')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('companies_chart_by_status'), statusCounts, {unit: t('companies_unit'), sort: 'desc'});
        html += renderBarChart(t('companies_chart_by_function'), functionCounts, {unit: t('companies_unit'), sort: 'desc', barClass: 'bg-success'});
        html += renderBarChart(t('companies_chart_by_place'), placeCounts, {unit: t('companies_unit'), sort: 'desc', limit: 25, last: true});
        return html;
    }
};

// The training companies I taught FOR (not clients: they hired me to teach
// their courses to their own customers): the same cards over the organizations
// whose functions include training-provider (scripts/import_companies.py
// writes one JSON per tab). The app derives sortFields and filters onto each
// plugin object, so this is a copy, not the same object under a second key.
// Both keys map to this file in the app's registry, which loads it once.
window.collectionPlugins['providers'] = Object.assign({}, window.collectionPlugins['companies'], {
    file: 'data/training_providers.json.gz',
    navTitle: t('companies_providers_nav_title'),
    title: t('companies_providers_title'),
    subtitle: t('companies_providers_subtitle')
});

// The companies I consulted for, on their own page (/consulting/):
// the same cards over the organizations whose functions include consulting.
// Unlike the two teaching tabs this one may share organizations with them,
// since I taught at some of the companies I consulted for.
window.collectionPlugins['consulting'] = Object.assign({}, window.collectionPlugins['companies'], {
    file: 'data/consulting.json.gz',
    navTitle: t('companies_consulting_nav_title'),
    title: t('companies_consulting_title'),
    subtitle: t('companies_consulting_subtitle')
});

// The publishers of the audiobooks, courses and radio I consumed, as a tab of
// the media page: the same cards over the organizations whose functions
// include publisher.
window.collectionPlugins['publishers'] = Object.assign({}, window.collectionPlugins['companies'], {
    file: 'data/publishers.json.gz',
    navTitle: t('companies_publishers_nav_title'),
    title: t('companies_publishers_title'),
    subtitle: t('companies_publishers_subtitle')
});

// The schools and universities I studied at, and the companies that
// certified me, as the two tabs of the education page (/training/education/).
window.collectionPlugins['education'] = Object.assign({}, window.collectionPlugins['companies'], {
    file: 'data/education.json.gz',
    navTitle: t('companies_education_nav_title'),
    title: t('companies_education_title'),
    subtitle: t('companies_education_subtitle')
});

window.collectionPlugins['certifications'] = Object.assign({}, window.collectionPlugins['companies'], {
    file: 'data/certifications.json.gz',
    navTitle: t('companies_certifications_nav_title'),
    title: t('companies_certifications_title'),
    subtitle: t('companies_certifications_subtitle')
});
