+++
title = "My Public Calendar"
template = "app.html"
+++

<div id="calendar-error" class="calendar-error"></div>
<div id="calendar" style="max-width:100%; margin:0 auto;"></div>

<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.20/index.global.min.js" integrity="sha384-cdgKlW4XCZfQ8yQFLScLHBujFrHf3sMYBPBjRimt2H/ut44fe4t/PUk3luazptar" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@fullcalendar/google-calendar@6.1.20/index.global.min.js" integrity="sha384-rIPPQ/9RkgMsV+B8X0s5dZLu2CKA38gLcRt62d9QkwznKY5C4Qagxmt8CEQHg/V9" crossorigin="anonymous"></script>
<script src="/keys.js"></script>
<script>
function themeToken(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

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
        // Event colours come from the theme rather than being hardcoded: read
        // the tokens off <html> so the calendar matches whatever theme is
        // selected. FullCalendar wants concrete colours here, not var().
        eventColor: themeToken('--accent', '#1a73e8'),
        eventTextColor: themeToken('--bg', '#ffffff'),
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

    // The theme switcher flips data-theme on <html>; the --fc-* variables in
    // the stylesheet follow automatically, but the event colours were passed to
    // FullCalendar as concrete values, so they need setting again.
    new MutationObserver(function () {
        calendar.setOption('eventColor', themeToken('--accent', '#1a73e8'));
        calendar.setOption('eventTextColor', themeToken('--bg', '#ffffff'));
    }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
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
/* FullCalendar 6 exposes its palette as --fc-* custom properties, so mapping
   them onto the site's theme tokens is all it takes for the calendar to follow
   the theme switcher -- no per-theme overrides, and it keeps working if a new
   theme is added to shared-themes. */
#calendar {
    --fc-page-bg-color: var(--bg);
    --fc-neutral-bg-color: var(--bg-surface);
    --fc-neutral-text-color: var(--text-secondary);
    --fc-border-color: var(--border);
    --fc-button-text-color: var(--text-primary);
    --fc-button-bg-color: var(--bg-elevated);
    --fc-button-border-color: var(--border);
    --fc-button-hover-bg-color: var(--bg-hover);
    --fc-button-hover-border-color: var(--accent);
    --fc-button-active-bg-color: var(--accent);
    --fc-button-active-border-color: var(--accent);
    --fc-today-bg-color: var(--bg-hover);
    --fc-event-bg-color: var(--accent);
    --fc-event-border-color: var(--accent);
    --fc-event-text-color: var(--bg);
    --fc-list-event-hover-bg-color: var(--bg-hover);
    color: var(--text-primary);
}

/* The active-view button uses --fc-button-active-bg-color, which is the accent,
   so its label needs the contrasting tone rather than the normal text colour. */
#calendar .fc-button-active { color: var(--bg); }

.fc-event {
    cursor: pointer;
    transition: transform 0.2s;
}
.fc-event:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

.calendar-error {
    display: none;
    background: var(--bg-surface);
    color: var(--danger, #dc2626);
    border: 1px solid var(--border);
    padding: 1rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1.25rem;
}
</style>
