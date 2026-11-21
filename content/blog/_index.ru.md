+++
title = "Блог"
description = "Эссе Марка Вельцера о программировании, Linux, философии, религии, политике и экономике, которые он пишет с 2010 года на английском и иврите, в переводе на русский."
sort_by = "date"
paginate_by = 10
template = "blog.html"
page_template = "page.html"
generate_feeds = true
# One listing per year at blog/<year>/, the pages the archive table links to.
year_archives = true
# Every post exists in every language: a missing translation fails the build.
require_translations = true

# Every post's share card, drawn by scripts/make_post_cards.py: templates
# read it as page.image and the post's structured data carries it.
[cascade]
image = "images/og/{stem}.{lang}.jpg"
+++
