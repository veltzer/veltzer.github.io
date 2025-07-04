<%!
	import config.calendar
%><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/favicon.svg">
    <title>My Interactive Calendar</title>
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.5/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.5/main.min.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.5/locales-all.min.js'></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }
        h1 {
            color: #1a73e8;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 500;
        }
        #calendar {
            max-width: 100%;
            margin: 0 auto;
        }
        .setup-info {
            background: #e8f4f8;
            border-left: 4px solid #1a73e8;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }
        .setup-info h2 {
            margin-top: 0;
            color: #1a73e8;
            font-size: 18px;
        }
        .setup-info code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        }
        .fc-event {
            cursor: pointer;
            transition: transform 0.2s;
        }
        .fc-event:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>My Public Calendar</h1>
        <div id="calendar"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            
            // Configuration
            const CALENDAR_ID = '${config.calendar.ID}'; // Replace with your calendar ID
            const API_KEY = '${config.calendar.API_KEY}'; // Replace with your API key
            const TIMEZONE = 'Asia/Jerusalem'; // Your timezone
            
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
                },
                locale: 'en',
                timeZone: TIMEZONE,
                height: 'auto',
                
                // Google Calendar configuration
                googleCalendarApiKey: API_KEY,
                events: {
                    googleCalendarId: CALENDAR_ID,
                    className: 'gcal-event' // Optional CSS class for styling
                },
                
                // Event handling
                eventClick: function(info) {
                    // Prevent default browser navigation
                    info.jsEvent.preventDefault();
                    
                    // Open event details in a new tab
                    if (info.event.url) {
                        window.open(info.event.url, '_blank');
                    }
                },
                
                // Styling
                eventColor: '#1a73e8',
                eventTextColor: '#ffffff',
                
                // Loading indicator
                loading: function(bool) {
                    if (bool) {
                        calendarEl.style.opacity = '0.5';
                    } else {
                        calendarEl.style.opacity = '1';
                    }
                },
                
                // Error handling
                eventSourceFailure: function() {
                    alert('Failed to load calendar events. Please check your Calendar ID and API key.');
                }
            });
            
            calendar.render();
        });
    </script>
</body>
</html>
