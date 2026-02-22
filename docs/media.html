<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Media Collection</title>

    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/favicon.svg">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" xintegrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>
    <style>
        /* Custom font and minor style adjustments */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa; 
        }
        .stat-card {
            text-align: center;
        }
        .stat-value {
            font-size: 1.875rem;
            font-weight: 700;
            color: #0d6efd;
        }
        .stat-label {
            font-size: 0.875rem;
            color: #6c757d;
            margin-top: 0.25rem;
        }
    </style>
</head>
<body class="antialiased">

    <div class="container my-5">
        
        <header class="text-center mb-5">
            <h1 id="page-title" class="display-4 fw-bold"></h1>
            <p id="page-subtitle" class="lead text-muted"></p>
        </header>

        <nav id="main-nav" class="nav nav-pills justify-content-center mb-5"></nav>

        <div id="search-container" class="mb-5 mx-auto" style="max-width: 40rem;">
             <input type="text" id="search-input" placeholder="Search..."
                   class="form-control form-control-lg rounded-pill">
        </div>
        
        <div id="status-message" class="text-center text-muted fs-5"></div>

        <main id="content-container">
            <section id="stats-container" class="mb-5"></section>

            <section id="items-container" class="row g-4"></section>
        </main>

    </div>

    <footer class="text-center text-muted mt-5 py-4 border-top">
        <p>Page Visits: <span id="visitor-count">Loading...</span></p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" xintegrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    <script src="plugin-museums.js"></script>
    <script src="plugin-movies.js"></script>
    <script src="plugin-series.js"></script>
    <script src="plugin-audio-courses.js"></script>
    <script src="plugin-audible.js"></script>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const itemsContainer = document.getElementById('items-container');
            const searchContainer = document.getElementById('search-container');
            const searchInput = document.getElementById('search-input');
            const statusMessage = document.getElementById('status-message');
            const pageTitle = document.getElementById('page-title');
            const pageSubtitle = document.getElementById('page-subtitle');
            const mainNav = document.getElementById('main-nav');
            const statsContainer = document.getElementById('stats-container');

            let allItems = []; // To store the fetched data
            let activeConfig = {}; // To store the config of the current view
            
            // --- Helper Function ---
            function formatDate(dateString) {
                if (!dateString) return null;
                // Extracts just the<x_bin_660>-MM-DD part from the UTC string
                return dateString.substring(0, 10);
            }
            
            // --- Master Configuration Object (populated by plugins) ---
            const dataSources = window.mediaPlugins || {};

            // --- Dynamically Generate Navigation ---
            function generateNav(activeDataType, showStatsOnly) {
                mainNav.innerHTML = ''; // Clear existing nav
                for (const [key, config] of Object.entries(dataSources)) {
                    const navLink = document.createElement('a');
                    navLink.href = '?data=' + key;
                    navLink.textContent = config.navTitle;
                    navLink.className = 'nav-link';
                    if (key === activeDataType) {
                        navLink.classList.add('active');
                    }
                    mainNav.appendChild(navLink);
                }
                
                const statsToggle = document.createElement('a');
                statsToggle.className = 'nav-link border rounded-pill ms-4';
                const currentParams = new URLSearchParams(window.location.search);

                if (showStatsOnly) {
                    statsToggle.textContent = '← Back to Full View';
                    currentParams.delete('stats');
                } else {
                    statsToggle.textContent = 'View Statistics';
                    currentParams.set('stats', 'true');
                }
                statsToggle.href = '?' + currentParams.toString();
                mainNav.appendChild(statsToggle);
            }

            // --- Fetch and Parse YAML Data ---
            async function loadData() {
                const urlParams = new URLSearchParams(window.location.search);
                const dataType = urlParams.get('data') || Object.keys(dataSources)[0]; 
                const showStatsOnly = urlParams.get('stats') === 'true';
                activeConfig = dataSources[dataType];

                if (!activeConfig) {
                    statusMessage.innerHTML = '<div class="alert alert-danger">Error: Invalid data type in URL or plugins not loaded.</div>';
                    return;
                }
                
                generateNav(dataType, showStatsOnly);

                pageTitle.textContent = activeConfig.title;
                pageSubtitle.textContent = showStatsOnly ? 'Statistics Overview' : activeConfig.subtitle;
                searchInput.placeholder = activeConfig.searchPlaceholder;
                document.title = activeConfig.title;
                
                if (showStatsOnly) {
                    searchContainer.style.display = 'none';
                    itemsContainer.style.display = 'none';
                    statsContainer.style.display = 'block';
                } else {
                    searchContainer.style.display = 'block';
                    itemsContainer.style.display = 'flex';
                    statsContainer.style.display = 'none';
                }

                try {
                    statusMessage.textContent = 'Loading ' + activeConfig.title + '...';
                    const response = await fetch('./' + activeConfig.file);
                    
                    if (!response.ok) {
                        throw new Error('HTTP error! status: ' + response.status + ". Make sure '" + activeConfig.file + "' is accessible.");
                    }

                    const yamlText = await response.text();
                    const data = jsyaml.load(yamlText);
                    // Rename 'title' to 'name' for consistency if it exists
                    allItems = (data.items || []).map(item => {
                        if (item.title && typeof item.name === 'undefined') {
                            item.name = item.title;
                        }
                        return item;
                    });
                    allItems.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
                    
                    if (showStatsOnly) {
                        statsContainer.innerHTML = activeConfig.renderStats(allItems);
                    } else {
                        renderItems(allItems);
                    }
                    statusMessage.textContent = '';

                } catch (error) {
                    console.error('Error loading or parsing YAML file:', error);
                    itemsContainer.innerHTML = '';
                    statsContainer.innerHTML = '';
                    statusMessage.innerHTML = '<div class="alert alert-danger" role="alert"><strong>Loading Failed:</strong> ' + error.message + '</div>';
                }
            }

            // --- Render Item Cards to the DOM (Generic) ---
            function renderItems(itemList) {
                itemsContainer.innerHTML = '';
                if (itemList.length === 0) {
                    statusMessage.textContent = 'No items found matching your search.';
                    return;
                }

                itemList.forEach(item => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 col-lg-4';
                    
                    const specificDetails = activeConfig.renderDetails(item);

                    col.innerHTML =
                        '<div class="card h-100">' +
                            '<div class="card-body d-flex flex-column">' +
                                '<h5 class="card-title fs-4 fw-bold">' + (item.name || 'No Title') + '</h5>' +
                                '<p class="card-text mb-4">' + (item.review || item.subtitle || 'No description.') + '</p>' +
                                '<ul class="list-group list-group-flush mt-auto">' +
                                    '<li class="list-group-item"><strong>Rating:</strong> <span class="badge bg-primary rounded-pill fs-6">' + (item.rating || '?') + ' / 10</span></li>' +
                                    '<li class="list-group-item"><strong>Device:</strong> ' + (item.device || 'N/A') + '</li>' +
                                    specificDetails +
                                '</ul>' +
                            '</div>' +
                        '</div>';
                    itemsContainer.appendChild(col);
                });
            }

            // --- Handle Search Input ---
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase().trim();
                const filteredItems = allItems.filter(item => {
                    return activeConfig.searchFields.some(field => {
                        const fieldValue = item[field];
                        if (!fieldValue) return false;
                        return fieldValue.toString().toLowerCase().includes(searchTerm);
                    });
                });
                renderItems(filteredItems);
            });

            // --- Visitor Counter ---
            function updateVisitorCount() {
                const namespace = window.location.hostname || 'local-file-viewer';
                const key = 'main-viewer-counter';
                const apiUrl = 'https://api.counterapi.dev/v1/' + namespace + '/' + key + '/up';

                fetch(apiUrl)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    const countElement = document.getElementById('visitor-count');
                    if (countElement) {
                        countElement.textContent = data.count; 
                    }
                })
                .catch(function(error) {
                    console.error('Error fetching visitor count:', error);
                    const countElement = document.getElementById('visitor-count');
                    if (countElement) {
                        countElement.textContent = 'N/A';
                    }
                });
            }

            // --- Initial Load ---
            loadData();
            updateVisitorCount();
        });
    </script>
</body>
</html>
