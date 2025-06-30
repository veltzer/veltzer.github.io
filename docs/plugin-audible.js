window.mediaPlugins = window.mediaPlugins || {};

window.mediaPlugins['audible'] = {
    file: 'audible.yaml',
    navTitle: 'Audible',
    title: 'Audible Library',
    subtitle: "A searchable list of my Audible books.",
    searchPlaceholder: 'Search by title, author, narrator...',
    searchFields: ['title', 'authors', 'narrators'],
    renderDetails: function(item) {
        let html = '';
        if (item.authors) {
            html += '<li class="list-group-item"><strong>Author(s):</strong> ' + item.authors + '</li>';
        }
        if (item.narrators) {
            html += '<li class="list-group-item"><strong>Narrator(s):</strong> ' + item.narrators + '</li>';
        }
        let status = 'Not Started';
        if (item.is_finished) {
            status = '<span class="fw-bold text-success">Finished</span>';
        } else if (parseFloat(item.percent_complete) > 0) {
            status = 'In Progress (' + item.percent_complete + '%)';
        }
        html += '<li class="list-group-item"><strong>Status:</strong> ' + status + '</li>';
         var date = this.formatDate(item.date_added);
        if (date) {
             html += '<li class="list-group-item"><strong>Date Added:</strong> ' + date + '</li>';
        }
        return html;
    },
    renderStats: function(items) {
        let finishedCount = 0;
        let inProgressCount = 0;
        const authorSet = new Set();
        const yearCounts = {};

        items.forEach(function(item) {
            if (item.is_finished) {
                finishedCount++;
            } else {
                inProgressCount++;
            }
            if (item.authors) {
                const authors = typeof item.authors === 'string' ? item.authors.split(',') : [item.authors];
                authors.forEach(author => authorSet.add(author.trim()));
            }
            const date = this.formatDate(item.date_added);
            if (date) {
                const year = date.substring(0, 4);
                yearCounts[year] = (yearCounts[year] || 0) + 1;
            }
        }.bind(this));

        let statsHtml = '<div class="row g-4 mb-4">';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + items.length + '</span><span class="stat-label">Total Books</span></div></div></div>';
        statsHtml += '<div class="col-md-6"><div class="card stat-card h-100"><div class="card-body"><span class="stat-value">' + authorSet.size + '</span><span class="stat-label">Unique Authors</span></div></div></div>';
        statsHtml += '</div>';

        statsHtml += '<div class="card mb-4"><div class="card-header"><strong>Completion Status</strong></div><div class="card-body">';
        const totalBooks = items.length;
        const finishedPercentage = (totalBooks > 0) ? (finishedCount / totalBooks) * 100 : 0;
        const inProgressPercentage = (totalBooks > 0) ? (inProgressCount / totalBooks) * 100 : 0;
        statsHtml += '<div class="mb-3"><p class="mb-1"><strong>Finished:</strong> ' + finishedCount + ' books</p><div class="progress" style="height: 20px;"><div class="progress-bar bg-success" role="progressbar" style="width: ' + finishedPercentage + '%;" aria-valuenow="' + finishedPercentage + '" aria-valuemin="0" aria-valuemax="100">' + Math.round(finishedPercentage) + '%</div></div></div>';
        statsHtml += '<div><p class="mb-1"><strong>In Progress / Unfinished:</strong> ' + inProgressCount + ' books</p><div class="progress" style="height: 20px;"><div class="progress-bar bg-info" role="progressbar" style="width: ' + inProgressPercentage + '%;" aria-valuenow="' + inProgressPercentage + '" aria-valuemin="0" aria-valuemax="100">' + Math.round(inProgressPercentage) + '%</div></div></div>';
        statsHtml += '</div></div>';
        
        const maxYearCount = Math.max.apply(null, Object.values(yearCounts).length > 0 ? Object.values(yearCounts) : [0]);
        statsHtml += '<div class="card"><div class="card-header"><strong>Books Added per Year</strong></div><div class="card-body">';
        Object.keys(yearCounts).sort().reverse().forEach(function(year) {
            const count = yearCounts[year];
            const percentage = maxYearCount > 0 ? (count / maxYearCount) * 100 : 0;
            statsHtml += '<div class="mb-3">';
            statsHtml += '   <p class="mb-1"><strong>' + year + '</strong> <span class="text-muted">(' + count + ' books)</span></p>';
            statsHtml += '   <div class="progress" style="height: 20px;">';
            statsHtml += '       <div class="progress-bar bg-primary" role="progressbar" style="width: ' + percentage + '%;" aria-valuenow="' + percentage + '" aria-valuemin="0" aria-valuemax="100"></div>';
            statsHtml += '   </div></div>';
        });
        statsHtml += '</div></div>';

        return statsHtml;
    },
    formatDate: (dateString) => dateString ? dateString.substring(0, 10) : null
};
