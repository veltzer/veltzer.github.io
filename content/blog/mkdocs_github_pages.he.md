+++
title = "MkDocs עם GitHub Pages: מבנה קבצים שעובד"
date = 2026-03-21

[taxonomies]
tags = ["תיעוד"]
+++

אם אתם משתמשים ב־MkDocs כדי לבנות אתר המתארח ב־GitHub Pages, ויש לכם גם קבצים סטטיים
(HTML,‏ JS,‏ CSS) שאינם חלק מהבלוג, מבנה הקבצים הנכון יכול להיות מסובך. הנה מה שלמדתי.

## הבעיה

‏MkDocs **מוחק** את תיקיית הפלט שלו (`site_dir`) בכל בנייה. אם תשימו את הקבצים הסטטיים שלכם
ישירות ב־`docs/` (שורש ברירת המחדל של GitHub Pages), `mkdocs build` ימחק אותם.

## הפתרון

שימו הכול בתיקיית המקור של MkDocs‏ (`docs_dir`). ‏MkDocs מעתיק קבצים שאינם Markdown כמות שהם.

ה־`mkdocs.yml` שלי:

```yaml
docs_dir: "blog"
site_dir: "docs"
```

המבנה שלי:

```text
blog/               # MkDocs source (docs_dir)
  index.md          # Blog home page
  about.md
  posts/            # Blog posts (Markdown)
  media.html        # Static HTML page (passed through)
  calendar.html     # Static HTML page (passed through)
  keys.js           # Static JS (passed through)
  data/             # Static data files (passed through)
docs/               # MkDocs output (site_dir) - don't edit manually
```

ב־`mkdocs build`, כל מה שנמצא ב־`blog/` מגיע ל־`docs/`. קובצי Markdown עוברים רינדור עם ערכת
הנושא. קובצי HTML,‏ JS,‏ CSS ואחרים מועתקים ללא שינוי. ‏GitHub Pages משרת את `docs/`.

## נקודות עיקריות

- לעולם אל תערכו ידנית קבצים ב־`docs/` — הם יידרסו בבנייה הבאה.
- שימו את כל הנכסים הסטטיים ב־`blog/` לצד ה־Markdown שלכם.
- הוסיפו קובץ `.nojekyll` ב־`blog/` כדי למנוע מגיטהאב להריץ את Jekyll.
- הפנו לדפים סטטיים ב־`nav` בלי לוכסן מוביל:

```yaml
nav:
  - 'Home': 'index.md'
  - 'Media': 'media.html'
  - 'Calendar': 'calendar.html'
```

שימוש בלוכסן `/` מוביל גורם ל־MkDocs להתייחס לנתיב ככתובת חיצונית, והוא לא יאמת שהקובץ קיים.
