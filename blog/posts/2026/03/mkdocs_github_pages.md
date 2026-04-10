---
tags:
  - mkdocs
  - github-pages
  - documentation
date: 2026-03-21
---

# MkDocs with GitHub Pages: File Layout That Works

If you use MkDocs to build a site hosted on GitHub Pages, and you also
have static files (HTML, JS, CSS) that aren't part of the blog, getting
the file layout right can be tricky. Here's what I learned.

## The Problem

MkDocs **wipes** its output directory (`site_dir`) on every build. If you
put your static files directly in `docs/` (the default GitHub Pages root),
`mkdocs build` deletes them.

## The Solution

Put everything in the MkDocs source directory (`docs_dir`). MkDocs copies
non-Markdown files through as-is.

My `mkdocs.yml`:

```yaml
docs_dir: "blog"
site_dir: "docs"
```

My layout:

```
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

On `mkdocs build`, everything in `blog/` ends up in `docs/`. Markdown
files get rendered with the theme. HTML, JS, CSS, and other files are
copied unchanged. GitHub Pages serves `docs/`.

## Key Points

- Never manually edit files in `docs/` — they'll be overwritten on next build.
- Put all static assets in `blog/` alongside your Markdown.
- Add a `.nojekyll` file in `blog/` to prevent GitHub from running Jekyll.
- Reference static pages in `nav` without a leading slash:

```yaml
nav:
  - 'Home': 'index.md'
  - 'Media': 'media.html'
  - 'Calendar': 'calendar.html'
```

Using a leading `/` makes MkDocs treat the path as an external URL and
it won't validate the file exists.
