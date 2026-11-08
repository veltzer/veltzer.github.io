/* global t, renderBarChart, renderStatCard, mediaFormatDate */
window.collectionPlugins = window.collectionPlugins || {};

// The certifications I hold, the Certifications tab of the education page
// (/training/education/): one card per certification, not per company.
// scripts/import_certifications.py joins certifications.yaml with the issuing
// organization in organizations.yaml, so each item carries the issuer's name,
// logo and website as issuer_* fields beside its own name, kind, date and remark.

function certificationYear(item) {
    return item.date && /^\d{4}/.test(item.date) ? item.date.substring(0, 4) : '';
}

// kind is an identifier (instructor / professional), shown through its string.
function certificationKind(item) {
    return item.kind ? t('certifications_kind_' + item.kind) : '';
}

window.collectionPlugins['certifications'] = {
    file: 'data/certifications.json.gz',
    navTitle: t('certifications_nav_title'),
    title: t('certifications_title'),
    subtitle: t('certifications_subtitle'),
    ratingScale: null,
    searchPlaceholder: t('certifications_search_placeholder'),
    searchFields: ['name', 'issuer_name', 'remark'],
    // The line under the name: the kind of certification and who issued it,
    // in the page's language (the app shows item.subtitle there).
    prepareItem: function(item) {
        if (item.kind && item.issuer_name) {
            item.subtitle = t('certifications_line_' + item.kind, {issuer: '\u2068' + item.issuer_name + '\u2069'});
        }
    },
    // Sort fields are given rather than derived from `fields`, so that an
    // undated certification sorts after the dated ones instead of before them
    // (the filters still come from `fields`, where the year filter must not
    // see that placeholder).
    sortFields: [
        {field: 'date', label: t('certifications_field_date'), type: 'string',
            value: function(item) { return item.date || '\uffff'; }
        },
        {field: 'name', label: t('certifications_field_name'), type: 'string'},
        {field: 'issuer_name', label: t('certifications_field_issuer'), type: 'string'},
        {field: 'kind', label: t('certifications_field_kind'), type: 'string', value: certificationKind}
    ],
    fields: [
        {field: 'name', label: t('certifications_field_name'), type: 'string', filterable: false},
        {field: 'issuer_name', label: t('certifications_field_issuer'), type: 'string', filterType: 'select'},
        {field: 'kind', label: t('certifications_field_kind'), type: 'string', filterType: 'select',
            value: certificationKind
        },
        {field: 'date', label: t('certifications_field_date'), type: 'string', filterType: 'year'}
    ],
    defaultSort: {field: 'date', order: 'asc'},
    toggleFields: [
        {key: 'issuer', label: t('certifications_toggle_issuer'), default: true},
        {key: 'kind', label: t('certifications_toggle_kind'), default: true},
        {key: 'date', label: t('certifications_toggle_date'), default: true},
        {key: 'remark', label: t('certifications_toggle_remark'), default: true},
        {key: 'website', label: t('certifications_toggle_website'), default: true}
    ],
    // The issuer's logo, on the same light box the organization cards use:
    // the logos are dark marks drawn for a white page.
    renderImage: function(item) {
        return item.logo || '';
    },
    imageFit: 'contain',
    imageBackground: 'light',
    // Data values are English, so they sit in <bdi> on a Hebrew page.
    renderDetails: function(item) {
        let html = '';
        if (item.issuer_name) {
            html += '<li class="py-2" data-toggle="issuer"><strong>' + t('certifications_detail_issuer') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.issuer_name) + '</bdi></li>';
        }
        if (item.kind) {
            html += '<li class="py-2" data-toggle="kind"><strong>' + t('certifications_detail_kind') + '</strong> ' +
                window.escapeHtml(certificationKind(item)) + '</li>';
        }
        const date = this.formatDate(item.date || '');
        html += '<li class="py-2" data-toggle="date"><strong>' + t('certifications_detail_date') + '</strong> ' +
            (date ? window.escapeHtml(date) : window.escapeHtml(t('certifications_date_unknown'))) + '</li>';
        if (item.remark) {
            html += '<li class="py-2" data-toggle="remark"><strong>' + t('certifications_detail_remark') + '</strong> ' +
                '<bdi>' + window.escapeHtml(item.remark) + '</bdi></li>';
        }
        if (item.issuer_website) {
            html += '<li class="py-2" data-toggle="website"><a href="' + window.escapeHtml(item.issuer_website) +
                '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' +
                '&#x1F517; ' + window.escapeHtml(t('certifications_visit_issuer', {issuer: '⁨' + item.issuer_name + '⁩'})) + '</a></li>';
        }
        return html;
    },
    formatDate: mediaFormatDate,
    renderStats: function(items) {
        const issuerCounts = {};
        const kindCounts = {};
        const yearCounts = {};
        items.forEach(function(item) {
            if (item.issuer_name) issuerCounts[item.issuer_name] = (issuerCounts[item.issuer_name] || 0) + 1;
            const kind = certificationKind(item);
            if (kind) kindCounts[kind] = (kindCounts[kind] || 0) + 1;
            const year = certificationYear(item);
            if (year) yearCounts[year] = (yearCounts[year] || 0) + 1;
        });
        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('certifications_stat_certifications')) + '</div>';
        html += '<div>' + renderStatCard(Object.keys(issuerCounts).length, t('certifications_stat_issuers')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('certifications_chart_by_issuer'), issuerCounts, {unit: t('certifications_unit'), sort: 'desc'});
        html += renderBarChart(t('certifications_chart_by_kind'), kindCounts, {unit: t('certifications_unit'), sort: 'desc', barClass: 'bg-success'});
        html += renderBarChart(t('certifications_chart_by_year'), yearCounts, {unit: t('certifications_unit'), last: true});
        return html;
    }
};
