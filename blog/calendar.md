---
hide:
  - toc
---

# My Public Calendar

<div id="calendar-error" style="display:none; background-color:#fef2f2; color:#dc2626; padding:1rem; border-radius:0.375rem; margin-bottom:1.25rem;"></div>
<div id="calendar" style="max-width:100%; margin:0 auto;"></div>

<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.20/index.global.min.js" integrity="sha384-cdgKlW4XCZfQ8yQFLScLHBujFrHf3sMYBPBjRimt2H/ut44fe4t/PUk3luazptar" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@fullcalendar/google-calendar@6.1.20/index.global.min.js" integrity="sha384-rIPPQ/9RkgMsV+B8X0s5dZLu2CKA38gLcRt62d9QkwznKY5C4Qagxmt8CEQHg/V9" crossorigin="anonymous"></script>
<script src="../keys.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        locale: 'en',
        timeZone: 'Asia/Jerusalem',
        height: 'auto',
        googleCalendarApiKey: API_KEY,
        events: {
            googleCalendarId: CALENDAR_ID,
            className: 'gcal-event'
        },
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            if (info.event.url) {
                window.open(info.event.url, '_blank', 'noopener,noreferrer');
            }
        },
        eventColor: '#1a73e8',
        eventTextColor: '#ffffff',
        loading: function(bool) {
            calendarEl.style.opacity = bool ? '0.5' : '1';
        },
        eventSourceFailure: function() {
            var errorEl = document.getElementById('calendar-error');
            errorEl.textContent = 'Failed to load calendar events. Please check your Calendar ID and API key.';
            errorEl.style.display = 'block';
        }
    });
    calendar.render();
    var refreshInterval = setInterval(function() {
        calendar.refetchEvents();
    }, 5 * 60 * 1000);
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        } else {
            calendar.refetchEvents();
            refreshInterval = setInterval(function() {
                calendar.refetchEvents();
            }, 5 * 60 * 1000);
        }
    });
});
</script>

<style>
.fc-event {
    cursor: pointer;
    transition: transform 0.2s;
}
.fc-event:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
</style>
