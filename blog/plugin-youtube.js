/* global renderBarChart, renderStatCard, mediaFormatDate */
window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['youtube'] = {
    file: 'data/youtube.yaml.gz',
    navTitle: 'YouTube',
    title: 'Watched YouTube Videos',
    subtitle: "A searchable list of YouTube videos I've watched.",
    ratingScale: null,
    searchPlaceholder: 'Search by title, channel, category...',
    searchFields: ['name', 'channel', 'categories'],
    fields: [
        {field: 'title', label: 'Title', type: 'string', filterable: false},
        {field: 'channel', label: 'Channel', type: 'string', filterType: 'select'},
        {field: 'upload_date', label: 'Upload Date', type: 'string', filterType: 'year'},
        {field: 'duration', label: 'Duration', type: 'number',
            filterType: 'range', ranges: [
                {label: 'Short (< 5 min)', min: 0, max: 300},
                {label: 'Medium (5-20 min)', min: 300, max: 1200},
                {label: 'Long (20-60 min)', min: 1200, max: 3600},
                {label: 'Very Long (60+ min)', min: 3600, max: null}
            ]
        },
        {field: 'view_count', label: 'Views', type: 'number',
            filterType: 'range', ranges: [
                {label: '< 1K', min: 0, max: 1000},
                {label: '1K - 10K', min: 1000, max: 10000},
                {label: '10K - 100K', min: 10000, max: 100000},
                {label: '100K - 1M', min: 100000, max: 1000000},
                {label: '1M+', min: 1000000, max: null}
            ]
        },
        {field: 'categories', label: 'Category', type: 'string', filterType: 'select'}
    ],
    defaultSort: {field: 'title', order: 'asc'},
    toggleFields: [
        {key: 'channel', label: 'Channel', default: true},
        {key: 'category', label: 'Category', default: false},
        {key: 'uploaded', label: 'Upload Date', default: true},
        {key: 'duration', label: 'Duration', default: true},
        {key: 'views', label: 'Views', default: false},
        {key: 'link', label: 'YouTube Link', default: true}
    ],
    renderImage: function(item) {
        if (!item.webpage_url) return '';
        const match = item.webpage_url.match(/[?&]v=([^&]+)/);
        if (!match) return '';
        return 'https://i.ytimg.com/vi/' + encodeURIComponent(match[1]) + '/mqdefault.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.channel) {
            html += '<li class="py-2" data-toggle="channel"><strong>Channel:</strong> ' + window.escapeHtml(item.channel) + '</li>';
        }
        if (item.categories) {
            html += '<li class="py-2" data-toggle="category"><strong>Category:</strong> ' + window.escapeHtml(item.categories) + '</li>';
        }
        const date = this.formatDate(item.upload_date);
        if (date) {
            html += '<li class="py-2" data-toggle="uploaded"><strong>Uploaded:</strong> ' + window.escapeHtml(date) + '</li>';
        }
        if (item.duration) {
            const mins = Math.floor(item.duration / 60);
            const secs = item.duration % 60;
            const durationStr = mins + ':' + (secs < 10 ? '0' : '') + secs;
            html += '<li class="py-2" data-toggle="duration"><strong>Duration:</strong> ' + window.escapeHtml(durationStr) + '</li>';
        }
        if (item.view_count) {
            html += '<li class="py-2" data-toggle="views"><strong>Views:</strong> ' + window.escapeHtml(item.view_count.toLocaleString()) + '</li>';
        }
        if (item.webpage_url) {
            html += '<li class="py-2" data-toggle="link"><a href="' + window.escapeHtml(item.webpage_url) + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">&#x1F517; Watch on YouTube</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const channelCounts = {};
        const categoryCounts = {};
        const yearCounts = {};
        let totalDuration = 0;

        items.forEach(function(item) {
            if (item.channel) {
                channelCounts[item.channel] = (channelCounts[item.channel] || 0) + 1;
            }
            if (item.categories) {
                categoryCounts[item.categories] = (categoryCounts[item.categories] || 0) + 1;
            }
            if (item.duration) {
                totalDuration += item.duration;
            }
            const date = this.formatDate(item.upload_date);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        const totalHours = Math.round(totalDuration / 3600);

        let html = '<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, 'Total Videos') + '</div>';
        html += '<div>' + renderStatCard(Object.keys(channelCounts).length, 'Unique Channels') + '</div>';
        html += '<div>' + renderStatCard(totalHours.toLocaleString() + 'h', 'Total Watch Time') + '</div>';
        html += '</div>';
        html += renderBarChart('Categories', categoryCounts, {unit: 'videos', sort: 'desc'});
        html += renderBarChart('Top 20 Channels', channelCounts, {unit: 'videos', sort: 'desc', limit: 20});
        html += renderBarChart('Videos per Upload Year', yearCounts, {unit: 'videos', sort: 'reverse', barClass: 'bg-danger', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
