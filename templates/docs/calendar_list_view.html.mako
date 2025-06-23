<%!
	import config.calendar
%><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/favicon.svg">
    <title>My Calendar Events</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        h1 {
            color: #1a73e8;
            margin-bottom: 30px;
            text-align: center;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .event {
            border-left: 4px solid #1a73e8;
            padding: 15px 20px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 0 5px 5px 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .event:hover {
            transform: translateX(5px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .event-title {
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 5px;
            color: #1a73e8;
        }
        .event-time {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .event-location {
            color: #555;
            font-size: 14px;
            margin-top: 5px;
        }
        .event-description {
            color: #555;
            font-size: 14px;
            margin-top: 10px;
            white-space: pre-wrap;
        }
        .all-day {
            background: #4285f4;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            display: inline-block;
        }
        .date-header {
            font-weight: 600;
            color: #666;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }
        .setup-note {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .error-list {
            margin: 10px 0;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upcoming Events</h1>
        <div id="loading" class="loading">Loading calendar events...</div>
        <div id="error" class="error" style="display: none;"></div>
        <div id="events"></div>
    </div>

    <script>
        // Configuration
        const CALENDAR_ID = '${config.calendar.ID}'; // Replace this
        const API_KEY = '${config.calendar.API_KEY}'; // Replace this
        const MAX_RESULTS = 20; // Number of events to show
        
        // Create element with text content (safe from XSS)
        function createElement(tag, className, textContent) {
            const element = document.createElement(tag);
            if (className) element.className = className;
            if (textContent) element.textContent = textContent;
            return element;
        }
        
        // Format date/time
        function formatDateTime(dateTime) {
            const date = new Date(dateTime);
            const options = {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            return date.toLocaleString('en-US', options);
        }
        
        function formatDate(dateTime) {
            const date = new Date(dateTime);
            const options = {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            };
            return date.toLocaleString('en-US', options);
        }
        
        // Group events by date
        function groupEventsByDate(events) {
            const grouped = {};
            events.forEach(event => {
                const date = event.start.dateTime || event.start.date;
                const dateKey = new Date(date).toDateString();
                if (!grouped[dateKey]) {
                    grouped[dateKey] = [];
                }
                grouped[dateKey].push(event);
            });
            return grouped;
        }
        
        // Create event element
        function createEventElement(event) {
            const eventDiv = createElement('div', 'event');
            
            // Title
            const titleDiv = createElement('div', 'event-title', event.summary || 'Untitled Event');
            eventDiv.appendChild(titleDiv);
            
            // Time
            const timeDiv = createElement('div', 'event-time');
            if (event.start.dateTime) {
                let timeText = formatDateTime(event.start.dateTime);
                if (event.end.dateTime) {
                    const endTime = new Date(event.end.dateTime).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    timeText += ' - ' + endTime;
                }
                timeDiv.textContent = timeText;
            } else {
                const allDaySpan = createElement('span', 'all-day', 'All Day');
                timeDiv.appendChild(allDaySpan);
            }
            eventDiv.appendChild(timeDiv);
            
            // Location
            if (event.location) {
                const locationDiv = createElement('div', 'event-location', '📍 ' + event.location);
                eventDiv.appendChild(locationDiv);
            }
            
            // Description
            if (event.description) {
                const descDiv = createElement('div', 'event-description', event.description);
                eventDiv.appendChild(descDiv);
            }
            
            return eventDiv;
        }
        
        // Fetch events from Google Calendar
        async function fetchEvents() {
            const now = new Date().toISOString();
            const url = 'https://www.googleapis.com/calendar/v3/calendars/' + CALENDAR_ID + '/events?key=' + API_KEY + '&timeMin=' + now + '&maxResults=' + MAX_RESULTS + '&singleEvents=true&orderBy=startTime';
            
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }
                const data = await response.json();
                return data.items || [];
            } catch (error) {
                throw error;
            }
        }
        
        // Display events
        function displayEvents(events) {
            const container = document.getElementById('events');
            // Clear existing content
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
            
            if (events.length === 0) {
                const noEventsP = createElement('p', null, 'No upcoming events found.');
                noEventsP.style.textAlign = 'center';
                noEventsP.style.color = '#666';
                container.appendChild(noEventsP);
                return;
            }
            
            const groupedEvents = groupEventsByDate(events);
            
            Object.keys(groupedEvents).forEach(dateKey => {
                // Add date header
                const dateHeader = createElement('div', 'date-header', formatDate(dateKey));
                container.appendChild(dateHeader);
                
                // Add events for this date
                groupedEvents[dateKey].forEach(event => {
                    const eventElement = createEventElement(event);
                    container.appendChild(eventElement);
                });
            });
        }
        
        // Display error
        function displayError(message) {
            const errorEl = document.getElementById('error');
            // Clear existing content
            while (errorEl.firstChild) {
                errorEl.removeChild(errorEl.firstChild);
            }
            
            const errorTitle = createElement('strong', null, 'Error loading calendar:');
            errorEl.appendChild(errorTitle);
            errorEl.appendChild(document.createElement('br'));
            errorEl.appendChild(document.createTextNode(message));
            errorEl.appendChild(document.createElement('br'));
            errorEl.appendChild(document.createElement('br'));
            errorEl.appendChild(document.createTextNode('Please check that:'));
            
            const errorList = createElement('ul', 'error-list');
            const checks = [
                'Your calendar is set to public',
                'You\'ve replaced YOUR_CALENDAR_ID and YOUR_API_KEY',
                'The Google Calendar API is enabled for your API key'
            ];
            
            checks.forEach(check => {
                const li = createElement('li', null, check);
                errorList.appendChild(li);
            });
            
            errorEl.appendChild(errorList);
            errorEl.style.display = 'block';
        }
        
        // Initialize
        async function init() {
            const loadingEl = document.getElementById('loading');
            const errorEl = document.getElementById('error');
            const setupNote = document.getElementById('setup-note');
            
            try {
                const events = await fetchEvents();
                loadingEl.style.display = 'none';
                setupNote.style.display = 'none';
                errorEl.style.display = 'none';
                displayEvents(events);
            } catch (error) {
                loadingEl.style.display = 'none';
                displayError(error.message);
            }
        }
        
        // Start when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        // Refresh every 5 minutes
        setInterval(init, 5 * 60 * 1000);
    </script>
</body>
</html>
