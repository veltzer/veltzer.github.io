/* global renderBarChart, renderStatCard, mediaFormatDate, t, countBy, countByYear, linkLine, toggleLine */
window.collectionPlugins = window.collectionPlugins || {};

window.collectionPlugins['youtube'] = {
    file: 'data/youtube.json.gz',
    navTitle: t('youtube_nav_title'),
    title: t('youtube_title'),
    subtitle: t('youtube_subtitle'),
    ratingScale: null,
    searchPlaceholder: t('youtube_search_placeholder'),
    searchFields: ['name', 'channel', 'categories'],
    fields: [
        {field: 'title', label: t('youtube_field_title'), type: 'string', filterable: false},
        {field: 'channel', label: t('youtube_field_channel'), type: 'string', filterType: 'select'},
        {field: 'upload_date', label: t('youtube_field_upload_date'), type: 'string', filterType: 'year'},
        {field: 'duration', label: t('youtube_field_duration'), type: 'number',
            filterType: 'range', ranges: [
                {label: t('youtube_range_short'), min: 0, max: 300},
                {label: t('youtube_range_medium'), min: 300, max: 1200},
                {label: t('youtube_range_long'), min: 1200, max: 3600},
                {label: t('youtube_range_very_long'), min: 3600, max: null}
            ]
        },
        {field: 'view_count', label: t('youtube_field_views'), type: 'number',
            filterType: 'range', ranges: [
                {label: t('youtube_views_lt_1k'), min: 0, max: 1000},
                {label: t('youtube_views_1k_10k'), min: 1000, max: 10000},
                {label: t('youtube_views_10k_100k'), min: 10000, max: 100000},
                {label: t('youtube_views_100k_1m'), min: 100000, max: 1000000},
                {label: t('youtube_views_1m_plus'), min: 1000000, max: null}
            ]
        },
        {field: 'categories', label: t('youtube_field_category'), type: 'string', filterType: 'select'},
        // Videos whose metadata could not be fetched are hidden unless asked for:
        // there are thousands of them and they all render the same placeholder card.
        {field: 'status', label: t('youtube_field_metadata'), type: 'string', sortable: false,
            filterType: 'select', defaultValue: t('youtube_available'),
            value: function(item) { return item.status === 'missing' ? t('youtube_unavailable') : t('youtube_available'); }
        }
    ],
    defaultSort: {field: 'title', order: 'asc'},
    toggleFields: [
        {key: 'channel', label: t('youtube_field_channel'), default: true},
        {key: 'category', label: t('youtube_field_category'), default: false},
        {key: 'uploaded', label: t('youtube_field_upload_date'), default: true},
        {key: 'duration', label: t('youtube_field_duration'), default: true},
        {key: 'views', label: t('youtube_field_views'), default: false},
        {key: 'link', label: t('youtube_link_toggle'), default: true}
    ],
    renderImage: function(item) {
        let videoId = item.video_id;
        if (!videoId && item.webpage_url) {
            const match = item.webpage_url.match(/[?&]v=([^&]+)/);
            if (match) videoId = match[1];
        }
        if (!videoId) return '';
        return 'https://i.ytimg.com/vi/' + encodeURIComponent(videoId) + '/mqdefault.jpg';
    },
    renderDetails: function(item) {
        let html = '';
        if (item.status === 'missing') {
            html += '<li class="py-2 text-gray-500"><em>' + t('youtube_metadata_unavailable') + '</em></li>';
        }
        if (item.channel) {
            html += toggleLine('channel', t('youtube_detail_channel'), window.escapeHtml(item.channel));
        }
        if (item.categories) {
            html += toggleLine('category', t('youtube_detail_category'), window.escapeHtml(item.categories));
        }
        const date = this.formatDate(item.upload_date);
        if (date) {
            html += toggleLine('uploaded', t('youtube_detail_uploaded'), window.escapeHtml(date));
        }
        if (item.duration) {
            const mins = Math.floor(item.duration / 60);
            const secs = item.duration % 60;
            const durationStr = mins + ':' + (secs < 10 ? '0' : '') + secs;
            html += toggleLine('duration', t('youtube_detail_duration'), window.escapeHtml(durationStr));
        }
        if (item.view_count) {
            html += toggleLine('views', t('youtube_detail_views'), window.escapeHtml(item.view_count.toLocaleString()));
        }
        if (item.webpage_url) {
            html += linkLine('link', item.webpage_url, t('youtube_watch'));
        }
        return html;
    },
    renderStats: function(items) {
        const channelCounts = countBy(items, function(item) { return item.channel; });
        const categoryCounts = countBy(items, function(item) { return item.categories; });
        let totalDuration = 0;
        let missingCount = 0;

        items.forEach(function(item) {
            if (item.status === 'missing') {
                missingCount++;
            }
            if (item.duration) {
                totalDuration += item.duration;
            }
        });

        const totalHours = Math.round(totalDuration / 3600);

        let html = '<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">';
        html += '<div>' + renderStatCard(items.length, t('youtube_stat_total')) + '</div>';
        html += '<div>' + renderStatCard(Object.keys(channelCounts).length, t('youtube_stat_channels')) + '</div>';
        html += '<div>' + renderStatCard(t('youtube_hours', {hours: totalHours.toLocaleString()}), t('youtube_stat_watch_time')) + '</div>';
        html += '<div>' + renderStatCard(missingCount, t('youtube_stat_missing')) + '</div>';
        html += '</div>';
        html += renderBarChart(t('youtube_chart_categories'), categoryCounts, {unit: t('youtube_unit_videos'), sort: 'desc'});
        html += renderBarChart(t('youtube_chart_top_channels'), channelCounts, {unit: t('youtube_unit_videos'), sort: 'desc', limit: 20});
        html += renderBarChart(t('youtube_chart_per_year'), countByYear(items, function(item) { return item.upload_date; }), {unit: t('youtube_unit_videos'), sort: 'reverse', barClass: 'bg-danger', last: true});
        return html;
    },
    formatDate: mediaFormatDate
};
