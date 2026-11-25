// The colophon's build and deploy times, in UTC and in the reader's own time
// zone (templates/colophon.html).
//
// The build time is in the page: data-time on its row, RFC 3339 in UTC, as
// rssite wrote it. The deploy time is not known when the page is built; it is
// the Last-Modified header GitHub Pages sends for this page, which is when the
// deploy uploaded it. A HEAD request for the page itself reads it. Where the
// server sends no such header, the deploy row stays hidden.
//
// The table is hidden in the HTML and shown here, so a reader without
// JavaScript sees only the UTC build time in the list above it.
(function () {
  'use strict';
  const table = document.querySelector('.colophon-times');
  if (!table) {
    return;
  }
  const lang = document.documentElement.lang || undefined;
  const style = { dateStyle: 'full', timeStyle: 'long' };
  const inUtc = new Intl.DateTimeFormat(lang, Object.assign({ timeZone: 'UTC' }, style));
  const inLocal = new Intl.DateTimeFormat(lang, style);

  function fill(row, date) {
    if (Number.isNaN(date.getTime())) {
      return false;
    }
    const iso = date.toISOString();
    const cells = [[row.querySelector('.utc'), inUtc], [row.querySelector('.local'), inLocal]];
    cells.forEach(function (pair) {
      const time = document.createElement('time');
      time.dateTime = iso;
      time.textContent = pair[1].format(date);
      pair[0].replaceChildren(time);
    });
    row.hidden = false;
    return true;
  }

  const buildRow = table.querySelector('.build-time');
  if (buildRow && fill(buildRow, new Date(buildRow.dataset.time))) {
    table.hidden = false;
  }

  const deployRow = table.querySelector('.deploy-time');
  if (!deployRow) {
    return;
  }
  fetch(location.pathname, { method: 'HEAD', cache: 'no-store' })
    .then(function (response) {
      const header = response.headers.get('Last-Modified');
      if (response.ok && header && fill(deployRow, new Date(header))) {
        table.hidden = false;
      }
    })
    .catch(function () { /* offline or blocked: leave the row hidden */ });
}());
