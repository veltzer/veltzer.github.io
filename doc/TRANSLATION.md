# Translation (Hebrew and Russian)

The state of the Hebrew version of the site: what is translated, how, and what
is deliberately left in English. Written 2026-11-08, after the footer, the
chess viewer and the calendar were translated. The status below is final
unless something changes: the remaining gaps are decided, not pending. (The
chess viewer was removed on 2026-11-20.)

## Translated

- **Every page.** Every page under `content/` has a Hebrew file
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

## Checked by the build

- **The Hebrew feeds and the share cards of Hebrew posts.** Read on
  2026-11-19, which found two things: every tag feed under `/he/tags/` was
  titled with the English site title, and every entry of every Hebrew feed
  named the author in English. Both were rssite's (fixed in 0.1.29: a
  section's or a term's feed uses the language's title, and a language can
  set its own `author`, which `rssite.toml` now does). The cards were
  clean: their text is the name from `home_title`, the post's title and its
  tags. `scripts/check_hebrew.py` now checks all of it on every build
  (`doc/SCRIPTS.md`), so neither needs reading by hand again.

## How it fits together

- **A page** has an `.en.md` and an `.he.md` file. Applications whose body
  exists once set `body_from = "en"` in the Hebrew file. If the app is
  translated (its strings come from i18n), the Hebrew file also sets
  `[extra] translated = true`, so `app_body.html` does not wrap the body as
  English.
- **An app's strings** are keys with a common prefix in both i18n files. The
  template sets `strings_prefix` and includes `page_strings.html`, which
  writes every matching key from `en.toml`, looked up with `trans()`, into
  `window.pageStrings`. `app.html` takes
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

## Russian (started 2026-11-21)

Russian is the third language of the site, and unlike Hebrew it is partial
by design: the posts are translated in batches, newest first, and `/ru/blog/`
lists only the ones done so far. Everything else is in place:
`i18n/ru.toml` (every key, with genitive month names for dates), the section
pages (the apps and the calendar take their body from English, like Hebrew),
the About page (the `_ru` fields of `profiles.yaml`), the share cards
(Liberation Sans, since Outfit has no Cyrillic), the root chooser and the
semantic search's vectors (`make_word_vectors.py --languages ru`, to rerun
after each batch).

What makes a partial language possible:

- No `require_translations` on the blog (it would demand all of them);
  `scripts/check_post_names.py` requires every post in English and Hebrew,
  and a Russian post to have its English original.
- A Russian post links to an untranslated one as `@/blog/<stem>.en.md`, which
  rssite resolves to the English page; `check_post_names.py` fails once the
  target has a `.ru.md`, so the link is switched to `@/blog/<stem>.md`.
- An untranslated page's language switcher falls back to the Russian home.

Not yet done: no aspell spellcheck for Russian (it needs `aspell-ru`) and no
`check_hebrew.py` counterpart for leftover English in Russian posts.

### Tag glossary

Tags pair by position across all three languages, so an English tag must
always become the same Russian tag. The ones used so far:

| en | ru | en | ru |
| --- | --- | --- | --- |
| politics | политика | religion | религия |
| philosophy | философия | epistemology | эпистемология |
| direct-democracy | прямая-демократия | opinion | мнение |
| history | история | science | наука |
| culture | культура | psychology | психология |
| ethics | этика | economics | экономика |
| statistics | статистика | atheism | атеизм |
| programming | программирование | bible | библия |
| game-theory | теория-игр | finance | финансы |
| education | образование | technology | технологии |
| neuroscience | нейронауки | security | безопасность |
| israel | израиль | command-line | командная-строка |
| law | право | media | медиа |
| sysadmin | системное-администрирование | probability | вероятность |
| open-source | открытый-код | music | музыка |
| self-hosting | самохостинг | hardware | аппаратное-обеспечение |
| markets | рынки | reference | справочник |
| literature | литература | video | видео |
| audio | аудио | climate | климат |
| blogging | блогинг | browser | браузер |
| archaeology | археология | database | базы-данных |
| theory | теория | embedded | встраиваемые-системы |
| performance | производительность | filesystem | файловые-системы |
| memory | память | fiction | художественная-литература |
| documentation | документация | keyboard | клавиатура |
| debugging | отладка | hebrew | иврит |

Product names stay as they are: linux, windows, ubuntu, debian, wordpress,
php, perl, mysql, java, git, ux.
