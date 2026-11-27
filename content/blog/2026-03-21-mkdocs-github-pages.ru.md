+++
date = 2026-03-21
description = "MkDocs стирает выходной каталог при каждой сборке, поэтому HTML, JS и CSS, положенные в docs/, исчезают. Держите их в docs_dir, и MkDocs скопирует их сам."
slug = "mkdocs-github-pages"
title = "MkDocs и GitHub Pages: работающая структура файлов"

[taxonomies]
tags = ["документация"]
+++

Если вы собираете с помощью MkDocs сайт, размещённый на GitHub Pages, и у
вас есть ещё и статические файлы (HTML, JS, CSS), не входящие в блог,
правильно разложить файлы может оказаться непросто. Вот что я выяснил.

## Проблема

MkDocs **стирает** свой выходной каталог (`site_dir`) при каждой сборке. Если
положить статические файлы прямо в `docs/` (корень GitHub Pages по умолчанию),
`mkdocs build` их удалит.

## Решение

Кладите всё в исходный каталог MkDocs (`docs_dir`). Файлы, не являющиеся
Markdown, MkDocs копирует как есть.

Мой `mkdocs.yml`:

```yaml
docs_dir: "blog"
site_dir: "docs"
```

Моя структура:

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

При `mkdocs build` всё из `blog/` оказывается в `docs/`. Файлы Markdown
отрисовываются с темой. HTML, JS, CSS и прочие файлы копируются без изменений.
GitHub Pages раздаёт `docs/`.

## Главное

- Никогда не правьте файлы в `docs/` вручную — при следующей сборке они будут
  перезаписаны.
- Кладите все статические ресурсы в `blog/` рядом с Markdown.
- Добавьте файл `.nojekyll` в `blog/`, чтобы GitHub не запускал Jekyll.
- Ссылайтесь на статические страницы в `nav` без ведущей косой черты:

```yaml
nav:
  - 'Home': 'index.md'
  - 'Media': 'media.html'
  - 'Calendar': 'calendar.html'
```

С ведущей `/` MkDocs считает путь внешним URL и не проверяет, существует ли
файл.
