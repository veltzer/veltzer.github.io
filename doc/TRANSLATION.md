# Hebrew Translation

The state of the Hebrew version of the site: what is translated, how, and what
is deliberately left in English. Written 2026-11-08, after the footer, the
chess viewer and the calendar were translated. The status below is final
unless something changes: the remaining gaps are decided, not pending.

## Translated

- **Every page.** All 436 pages under `content/` have a Hebrew file
  (`*.he.md` beside each `*.en.md`), and none of the Hebrew files has English
  body text. That covers the blog posts, training, consulting, education,
  about and the section pages.
- **The site's own strings.** Every key in `i18n/en.toml` has a value in
  `i18n/he.toml`; a missing key fails the build. That covers the nav, the
  language and theme pickers, dates, the footer and the blog search. The
  only keys whose Hebrew is the same as the English are brand names
  (Audible, The Great Courses) and view-count bands ("1K–10K").
- **The data collection apps** (media and teaching data): their interface
  strings are the `app_*` keys, written into the page as
  `window.collectionStrings` by `templates/data_collection.html` and read
  with `t()`. The app runs right to left in Hebrew.
- **The footer.** The two provenance lines are `footer_*` keys
  (`templates/base.html`). Names, the version and the address sit in `<bdi>`
  so they do not reorder the Hebrew sentence.
- **The chess viewer** (`content/chess/_index.en.md`). Its strings are the
  `chess_*` keys, written into the page as `window.pageStrings` by
  `templates/page_strings.html`. In Hebrew it runs right to left, except the
  board, which stays left to right. Number ranges ("1996–2026") are wrapped in
  Unicode isolates, or Hebrew text would show them reversed. The arrows on the
  move buttons are swapped for right to left. The « » on the game buttons are
  not swapped, because the browser already mirrors them.
- **The calendar** (`content/calendar/_index.en.md`). It uses the `calendar_*`
  keys, handed to FullCalendar as an inline locale object instead of
  vendoring FullCalendar's locale files. Month and day names come from `Intl`
  under the page's language code, and the direction follows the page.

## Not translated, by decision

- **Syllabi, Slides and Animations.** These are generated from the teaching
  repositories by `scripts/import_teaching.py`. Their Hebrew pages
  (`body_from = "en"`) reuse the English body inside a `dir="ltr" lang="en"`
  wrapper (`templates/app_body.html`), so only the title, nav and footer around
  them are Hebrew. Translating them means adding translations in the teaching
  repositories, a large job (syllabi alone is ~390KB). Decided 2026-11-08: not
  worth doing.
- **The data itself.** Book, movie, course and podcast titles, reviews and
  company names in the collections are content, not interface. Translating
  them would mean keeping a Hebrew copy of the data.
- **Proper names.** Theme names (Azure, Paper, Midnight, Nord, Solarized, Rosé
  Pine), brand and account names on the About page, technical tag names
  (`php`, `mysql`), and English titles of cited books and papers in posts.
- **The 404 page.** GitHub Pages serves one `/404.html` for every language, so
  it cannot know the reader's language. It shows both languages.

## Not verified

- The Hebrew Atom feed (`/he/atom.xml`) and the social-sharing images of Hebrew
  posts (`images/og/`) were not checked for English text.

## How it fits together

- **A page** has an `.en.md` and an `.he.md` file. Applications whose body
  exists once set `body_from = "en"` in the Hebrew file. If the app is
  translated (its strings come from i18n), the Hebrew file also sets
  `[extra] translated = true`, so `app_body.html` does not wrap the body as
  English.
- **An app's strings** are keys with a common prefix in both i18n files. The
  template sets `strings_prefix` and includes `page_strings.html`, which
  writes every matching key from `en.toml`, looked up with `trans()`, into
  `window.pageStrings`. `chess.html` sets the prefix itself; `app.html` takes
  it from `[extra] strings_prefix` in the page's front matter. Placeholders
  are `{name}`, filled in by the app's `t(key, values)`.
- **Adding a string**: add the key to both `i18n/en.toml` and `i18n/he.toml`.
  A key missing from `he.toml` fails the build.

## How the audit was done

Checked on 2026-11-08 by:

- **Files and keys.** Checking that every `.en.md` has an `.he.md` and that
  `en.toml` and `he.toml` have the same keys.
- **Hebrew page text.** Measuring the share of Hebrew letters in each `.he.md`
  body (code blocks, tags and URLs left out).
- **Built pages.** Parsing every built page under `_site/he/` for visible
  English text (scripts, styles, code and `lang="en"` blocks left out).
- **Script strings.** Grepping the page scripts and `static/*.js` for
  hard-coded English.
- **In the browser.** Opening the Hebrew chess, calendar and footer, plus the
  English chess page, to confirm nothing changed in English.

Repeat these checks after adding an app or a page template.
