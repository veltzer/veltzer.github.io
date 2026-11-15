+++
title = "My Public Calendar"
description = "Mark Veltzer's public Google calendar, with month, week and day views."
template = "app.html"

[extra]
strings_prefix = "calendar_"
+++

<div id="calendar-error" class="calendar-error" role="alert"></div>
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
