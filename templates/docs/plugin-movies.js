window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['features'] = {
    file: 'data/video_features.yaml',
    navTitle: 'Movies',
    title: 'Watched Movies',
    subtitle: "A searchable list of movies I've watched.",
    searchPlaceholder: 'Search by title, review, location...',
    searchFields: ['name', 'review', 'location'],
    renderDetails: function(item) {
        let html = '';
        const date = this.formatDate(item.date_utcz);
        if (date) {
             html += '<li class="list-group-item"><strong>Date Watched:</strong> ' + date + '</li>';
        }
        if (item.location) {
            html += '<li class="list-group-item"><strong>Location:</strong> ' + item.location + '</li>';
        }
        if (item.with && item.with.length > 0) {
            html += '<li class="list-group-item"><strong>With:</strong> ' + item.with.join(', ') + '</li>';
        }
        if (item.imdb_id) {
            html += '<li class="list-group-item"><a href="https://www.imdb.com/title/tt' + item.imdb_id + '/" target="_blank">View on IMDb</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const deviceCounts = {};
        const yearCounts = {};
        let withCount = 0;
        items.forEach(function(item) {
            if (item.device) {
                deviceCounts[item.device] = (deviceCounts[item.device] || 0) + 1;
            }
            if (item.with && item.with.length > 0) {
                withCount++;
            }
            const date = this.formatDate(item.date_utcz);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let statsHtml = '<div class="row g-4 mb-4">';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + items.length + '</span><span class="stat-label">Total Movies</span></div></div></div>';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + withCount + '</span><span class="stat-label">Movies Watched with Others</span></div></div></div>';
        statsHtml += '</div>';

        const maxDeviceCount = Math.max.apply(null, Object.values(deviceCounts).length > 0 ? Object.values(deviceCounts) : [0]);
        statsHtml += '<div class="card mb-4"><div class="card-header"><strong>Device Distribution</strong></div><div class="card-body">';
        const colors = ['#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#198754', '#dc3545', '#ffc107'];
        let colorIndex = 0;
         Object.keys(deviceCounts).sort().forEach(function(device) {
            const count = deviceCounts[device];
            const percentage = maxDeviceCount > 0 ? (count / maxDeviceCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + device + '</strong> <span class="text-muted">(' + count + ' items)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar" role="progressbar" style="width: ' + percentage + '%; background-color:' + colors[colorIndex % colors.length] + ';" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
            colorIndex++;
        });
        statsHtml += '</div></div>';

        const maxYearCount = Math.max.apply(null, Object.values(yearCounts).length > 0 ? Object.values(yearCounts) : [0]);
        statsHtml += '<div class="card"><div class="card-header"><strong>Items per Year</strong></div><div class="card-body">';
        Object.keys(yearCounts).sort().reverse().forEach(function(year) {
            const count = yearCounts[year];
            const percentage = maxYearCount > 0 ? (count / maxYearCount) * 100 : 0;
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
