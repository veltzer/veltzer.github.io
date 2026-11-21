+++
title = "Blog"
description = "Essays by Mark Veltzer on programming, Linux, philosophy, religion, politics and economics, written since 2010 in English and Hebrew."
sort_by = "date"
paginate_by = 10
template = "blog.html"
page_template = "page.html"
generate_feeds = true
# One listing per year at blog/<year>/, the pages the archive table links to.
year_archives = true
# Every post exists in English and Hebrew, which scripts/check_post_names.py
# enforces. Not require_translations: the generator would demand every post in
# Russian too, which is still being translated (see _index.ru.md).

# Every post's share card, drawn by scripts/make_post_cards.py: templates
# read it as page.image and the post's structured data carries it.
[cascade]
image = "images/og/{stem}.{lang}.jpg"
+++
