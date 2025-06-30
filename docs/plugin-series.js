window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['videos'] = {
    file: 'data/video_series.yaml',
    navTitle: 'Video Series',
    title: 'Watched TV Series',
    subtitle: "A searchable list of TV series I've watched.",
    searchPlaceholder: 'Search by name, review, location...',
    searchFields: ['name', 'review', 'location'],
    renderDetails: function(item) {
        var seasons = item.seasons_seen ? item.seasons_seen.join(', ') : 'N/A';
        var html = '<li class="list-group-item"><strong>Seasons Seen:</strong> ' + seasons + '</li>';
        var date = this.formatDate(item.date_utcz);
        if (date) {
             html += '<li class="list-group-item"><strong>Date Watched:</strong> ' + date + '</li>';
        }
        if (item.location) {
            html += '<li class="list-group-item"><strong>Location:</strong> ' + item.location + '</li>';
        }
        if (item.imdb_id) {
            html += '<li class="list-group-item"><a href="https://www.imdb.com/title/tt' + item.imdb_id + '/" target="_blank">View on IMDb</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        var deviceCounts = {};
        var yearCounts = {};
        var totalSeasons = 0;
        items.forEach(function(item) {
            if (item.device) {
                deviceCounts[item.device] = (deviceCounts[item.device] || 0) + 1;
            }
            if (item.seasons_seen) {
                totalSeasons += item.seasons_seen.length;
            }
            var date = this.formatDate(item.date_utcz);
            if (date) {
                var year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        var statsHtml = '<div class="row g-4 mb-4">';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + items.length + '</span><span class="stat-label">Total Series</span></div></div></div>';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + totalSeasons + '</span><span class="stat-label">Total Seasons</span></div></div></div>';
        statsHtml += '</div>';

        var maxDeviceCount = Math.max.apply(null, Object.values(deviceCounts).length > 0 ? Object.values(deviceCounts) : [0]);
        statsHtml += '<div class="card mb-4"><div class="card-header"><strong>Device Distribution</strong></div><div class="card-body">';
        var colors = ['#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#198754', '#dc3545', '#ffc107'];
        var colorIndex = 0;
         Object.keys(deviceCounts).sort().forEach(function(device) {
            var count = deviceCounts[device];
            var percentage = maxDeviceCount > 0 ? (count / maxDeviceCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + device + '</strong> <span class="text-muted">(' + count + ' items)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar" role="progressbar" style="width: ' + percentage + '%; background-color:' + colors[colorIndex % colors.length] + ';" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
            colorIndex++;
        });
        statsHtml += '</div></div>';

        var maxYearCount = Math.max.apply(null, Object.values(yearCounts).length > 0 ? Object.values(yearCounts) : [0]);
        statsHtml += '<div class="card"><div class="card-header"><strong>Items per Year</strong></div><div class="card-body">';
        Object.keys(yearCounts).sort().reverse().forEach(function(year) {
            var count = yearCounts[year];
            var percentage = maxYearCount > 0 ? (count / maxYearCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + year + '</strong> <span class="text-muted">(' + count + ' items)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar bg-success" role="progressbar" style="width: ' + percentage + '%;" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
        });
        statsHtml += '</div></div>';

        return statsHtml;
    },
    formatDate: (dateString) => dateString ? dateString.substring(0, 10) : null
};
