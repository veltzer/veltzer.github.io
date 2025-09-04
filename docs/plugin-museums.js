window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['museums'] = {
    file: 'data/museums.yaml',
    navTitle: 'Museums',
    title: 'Visited Museums',
    subtitle: "A list of museums and exhibitions I've visited over the years.",
    searchPlaceholder: 'Search by name, city, review...',
    searchFields: ['name', 'city', 'review', 'with'],
    renderDetails: function(item) {
        let html = '';
        const date = item.date_utcz ? this.formatDate(item.date_utcz) : item.date_dmy;
        if (date) {
             html += '<li class="list-group-item"><strong>Date:</strong> ' + date + '</li>';
        }
        if (item.city) {
            html += '<li class="list-group-item"><strong>City:</strong> ' + item.city + '</li>';
        }
        if (item.with && item.with.length > 0) {
            html += '<li class="list-group-item"><strong>With:</strong> ' + item.with.join(', ') + '</li>';
        }
         if (item.remark) {
            html += '<li class="list-group-item"><strong>Remark:</strong> ' + item.remark + '</li>';
        }
        if (item.url) {
            html += '<li class="list-group-item"><a href="' + item.url + '" target="_blank">Visit Website</a></li>';
        }
        return html;
    },
    renderStats: function(items) {
        const cityCounts = {};
        const yearCounts = {};
        
        const getYear = (item) => {
            if (item.date_utcz) return item.date_utcz.substring(0, 4);
            if (item.date_dmy) return item.date_dmy.substring(6, 10);
            return null;
        };

        items.forEach(function(item) {
            if (item.city) {
                cityCounts[item.city] = (cityCounts[item.city] || 0) + 1;
            }
            const year = getYear(item);
            if (year) {
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        });

        let statsHtml = '<div class="row g-4 mb-4">';
        statsHtml += '<div class="col-md-12"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + items.length + '</span><span class="stat-label">Total Visits</span></div></div></div>';
        statsHtml += '</div>';

        const maxCityCount = Math.max.apply(null, Object.values(cityCounts).length > 0 ? Object.values(cityCounts) : [0]);
        statsHtml += '<div class="card mb-4"><div class="card-header"><strong>Visits per City</strong></div><div class="card-body">';
        const colors = ['#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#198754', '#dc3545', '#ffc107'];
        let colorIndex = 0;
        Object.keys(cityCounts).sort((a, b) => cityCounts[b] - cityCounts[a]).forEach(function(city) {
            const count = cityCounts[city];
            const percentage = maxCityCount > 0 ? (count / maxCityCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + city + '</strong> <span class="text-muted">(' + count + ' visits)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar" role="progressbar" style="width: ' + percentage + '%; background-color:' + colors[colorIndex % colors.length] + ';" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
            colorIndex++;
        });
        statsHtml += '</div></div>';
        
        const maxYearCount = Math.max.apply(null, Object.values(yearCounts).length > 0 ? Object.values(yearCounts) : [0]);
        statsHtml += '<div class="card"><div class="card-header"><strong>Visits per Year</strong></div><div class="card-body">';
        Object.keys(yearCounts).sort().reverse().forEach(function(year) {
            const count = yearCounts[year];
            const percentage = maxYearCount > 0 ? (count / maxYearCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + year + '</strong> <span class="text-muted">(' + count + ' visits)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar bg-success" role="progressbar" style="width: ' + percentage + '%;" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
        });
        statsHtml += '</div></div>';

        return statsHtml;
    },
    formatDate: (dateString) => dateString ? dateString.substring(0, 10) : null
};
