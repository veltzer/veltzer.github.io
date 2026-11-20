+++
title = "Colophon"
description = "How this site is made: the generator, the build, the checks and the hosting, and which commit the pages you are reading were built from."
template = "colophon.html"
+++

This site is static. Every page is a file, written ahead of time and served
as it is by GitHub Pages under `veltzer.org`; nothing runs on a server when you
read it.

- **Generator.** [rssite](https://github.com/veltzer/rssite), a static site
  generator I wrote in Rust, renders the Markdown posts and the Tera templates
  in both languages, along with the feeds, the sitemap and the search index.
- **Build.** [rsconstruct](https://github.com/veltzer/rsconstruct), my build
  tool, runs rssite together with the checks: the HTML is validated, the
  JavaScript, CSS, Python and shell are linted, the blog is spellchecked in
  English and in Hebrew, and the media data is checked against its sources.
  It rebuilds only what changed, and GitHub Actions runs it on every push.
- **Design.** The colours, fonts and themes come from a set of design tokens
  shared with my teaching sites.
- **Analytics.** [GoatCounter](https://veltzer.goatcounter.com), which sets no
  cookies; its dashboard is public.
- **Source.** Everything, including this page, is in
  [veltzer/veltzer.github.io](https://github.com/veltzer/veltzer.github.io).

The details of the build below change with every commit. They are on this
page rather than in the footer of every page, so that a commit that changes
one post rebuilds and redeploys that post, and every other page stays exactly
what it was.
