window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['podcasts'] = {
    file: 'data/podcasts.yaml',
    navTitle: 'Podcasts',
    title: 'Listened Podcasts',
    subtitle: "A searchable list of podcasts I've listened to.",
    searchPlaceholder: 'Search by name, review, chapter...',
    searchFields: ['name', 'review', 'url'],
    renderDetails: function(item) {
        var html = '';
        if (item.url) {
            html += '<li class="list-group-item"><a href="' + item.url + '" target="_blank">Visit Podcast</a></li>';
        }
        if (item.chapters && item.chapters.length > 0) {
            html += '<li class="list-group-item"><strong>Chapters Listened:</strong> ' + item.chapters.length + '</li>';
            html += '<li class="list-group-item"><strong>Chapters:</strong><ul class="list-unstyled mb-0 mt-1">';
            item.chapters.forEach(function(ch) {
                var parts = ['<strong>' + ch.name + '</strong>'];
                if (ch.date_utcz) {
                    parts.push(ch.date_utcz.substring(0, 10));
                }
                if (ch.location) {
                    parts.push(ch.location);
                }
                if (ch.rating) {
                    parts.push(ch.rating + '/10');
                }
                html += '<li class="ms-3">- ' + parts.join(' &middot; ') + '</li>';
            });
            html += '</ul></li>';
        }
        return html;
    },
    renderStats: function(items) {
        var totalChapters = 0;
        var deviceCounts = {};
        var locationCounts = {};

        items.forEach(function(item) {
            if (item.chapters) {
                totalChapters += item.chapters.length;
                item.chapters.forEach(function(ch) {
                    if (ch.device) {
                        deviceCounts[ch.device] = (deviceCounts[ch.device] || 0) + 1;
                    }
                    if (ch.location) {
                        locationCounts[ch.location] = (locationCounts[ch.location] || 0) + 1;
                    }
                });
            }
        });

        var statsHtml = '<div class="row g-4 mb-4">';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + items.length + '</span><span class="stat-label">Total Podcasts</span></div></div></div>';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + totalChapters + '</span><span class="stat-label">Total Chapters Listened</span></div></div></div>';
        statsHtml += '</div>';

        var colors = ['#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#198754', '#dc3545', '#ffc107'];

        var maxDeviceCount = Math.max.apply(null, Object.values(deviceCounts).length > 0 ? Object.values(deviceCounts) : [0]);
        statsHtml += '<div class="card mb-4"><div class="card-header"><strong>Device Distribution</strong></div><div class="card-body">';
        var colorIndex = 0;
        Object.keys(deviceCounts).sort().forEach(function(device) {
            var count = deviceCounts[device];
            var percentage = maxDeviceCount > 0 ? (count / maxDeviceCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + device + '</strong> <span class="text-muted">(' + count + ' chapters)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar" role="progressbar" style="width: ' + percentage + '%; background-color:' + colors[colorIndex % colors.length] + ';" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
            colorIndex++;
        });
        statsHtml += '</div></div>';

        var maxLocationCount = Math.max.apply(null, Object.values(locationCounts).length > 0 ? Object.values(locationCounts) : [0]);
        statsHtml += '<div class="card"><div class="card-header"><strong>Listening Location</strong></div><div class="card-body">';
        colorIndex = 0;
        Object.keys(locationCounts).sort((a, b) => locationCounts[b] - locationCounts[a]).forEach(function(location) {
            var count = locationCounts[location];
            var percentage = maxLocationCount > 0 ? (count / maxLocationCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + location + '</strong> <span class="text-muted">(' + count + ' chapters)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar bg-success" role="progressbar" style="width: ' + percentage + '%;" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
            colorIndex++;
        });
        statsHtml += '</div></div>';

        return statsHtml;
    },
    formatDate: (dateString) => dateString ? dateString.substring(0, 10) : null
};
