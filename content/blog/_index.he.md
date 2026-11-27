+++
description = "מאמרים של מארק ולצר על תכנות, לינוקס, פילוסופיה, דת, פוליטיקה וכלכלה, נכתבים מאז 2010 באנגלית ובעברית."
generate_feeds = true
page_template = "page.html"
paginate_by = 10
# Every post exists in every language: a missing translation fails the build.
require_translations = true
sort_by = "date"
template = "blog.html"
title = "בלוג"
# One listing per year at blog/<year>/, the pages the archive table links to.
year_archives = true

# Every post's share card, drawn by scripts/make_post_cards.py: templates
# read it as page.image and the post's structured data carries it.
[cascade]
image = "images/og/{stem}.{lang}.jpg"
+++
