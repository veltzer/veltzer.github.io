+++
title = "My Public Calendar"
description = "Mark Veltzer's public Google calendar, with month, week and day views."
template = "app.html"

[extra]
strings_prefix = "calendar_"
+++

<div id="calendar-error" class="calendar-error"></div>
<div id="calendar" style="max-width:100%; margin:0 auto;"></div>

<!-- FullCalendar 6.1.20 (MIT), vendored in static/vendor/fullcalendar/: the
     files the jsDelivr URLs served, byte for byte (same SRI hashes). -->
<script src="/vendor/fullcalendar/fullcalendar.global.min.js"></script>
<script src="/vendor/fullcalendar/google-calendar.global.min.js"></script>
<script src="/keys.js"></script>
<script>
function themeToken(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

// The calendar in the page's language and direction. The strings are the
// calendar_* keys of i18n/<lang>.toml (templates/page_strings.html), handed
// to FullCalendar as a locale object rather than vendoring its locale files;
// month and day names come from Intl under the same code.
function pageLocale() {
    var s = window.pageStrings || {};
    var html = document.documentElement;
    return {
        code: html.lang || 'en',
        direction: getComputedStyle(html).direction === 'rtl' ? 'rtl' : 'ltr',
        buttonText: {
            prev: s.calendar_prev, next: s.calendar_next, today: s.calendar_today,
            month: s.calendar_month, week: s.calendar_week, day: s.calendar_day,
            list: s.calendar_list
        },
        weekText: s.calendar_week,
        allDayText: s.calendar_all_day,
        moreLinkText: s.calendar_more,
        noEventsText: s.calendar_no_events
    };
}

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var locale = pageLocale();
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        locales: [locale],
        locale: locale.code,
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
            errorEl.textContent = (window.pageStrings || {}).calendar_error;
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
    --fc-button-bg-color: var(--bg);
    --fc-button-border-color: var(--border);
    --fc-button-hover-bg-color: var(--bg);
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

/* The buttons drawn like the site's .control (sass/style.scss): its font,
   size, padding, corner and focus outline, rather than FullCalendar's own. */
#calendar .fc-button {
    font: inherit;
    font-size: 0.85rem;
    padding: 0.25rem 0.6rem;
    border-radius: var(--radius-xs);
    box-shadow: none;
    transition: border-color var(--transition);
}
#calendar .fc-button:focus,
#calendar .fc-button:active { box-shadow: none; }
#calendar .fc-button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
#calendar .fc-button-group > .fc-button { border-radius: 0; }
#calendar .fc-button-group > .fc-button:first-child { border-start-start-radius: var(--radius-xs); border-end-start-radius: var(--radius-xs); }
#calendar .fc-button-group > .fc-button:last-child { border-start-end-radius: var(--radius-xs); border-end-end-radius: var(--radius-xs); }
#calendar .fc-toolbar-title { font-size: 1.35rem; }
/* Phones: the toolbar's three groups wrap onto their own lines instead of
   pushing the view buttons past the edge of the screen. */
@media (max-width: 40rem) {
    #calendar .fc-header-toolbar { flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
    #calendar .fc-toolbar-title { font-size: 1.1rem; }
}

.fc-event {
    cursor: pointer;
    transition: transform 0.2s;
}
.fc-event:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

/* The site's .notice-error look (sass/style.scss), hidden until a load fails. */
.calendar-error {
    display: none;
    background: var(--danger-dim);
    color: var(--danger);
    border: 1px solid var(--danger);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1.25rem;
}
</style>
