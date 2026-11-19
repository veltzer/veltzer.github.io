"""Tests for check_hebrew.py, the check that the Hebrew feeds and share
cards carry no untranslated text."""

import check_hebrew

POST = """+++
title = "{title}"
description = "{description}"
date = 2026-01-01
slug = "a-post"

[taxonomies]
tags = {tags}
+++

גוף.
"""

FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="he">
  <title>{feed_title}</title>
  <generator uri="https://github.com/veltzer/rssite">rssite</generator>
  <id>https://veltzer.org/he/atom.xml</id>
  <updated>2026-01-01T00:00:00+00:00</updated>
  <entry xml:lang="he">
    <title>MkDocs עם GitHub Pages</title>
    <author><name>{author}</name></author>
    <id>https://veltzer.org/he/blog/a-post/</id>
    <content type="html">English inside a body is not this check's job</content>
  </entry>
  <entry xml:lang="he">
    <title>פוסט</title>
    <author><name>{author}</name></author>
    <id>https://veltzer.org/he/blog/b-post/</id>
  </entry>
</feed>
"""


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_a_translated_post_passes(tmp_path):
    text = POST.format(title="MkDocs עם GitHub Pages", description="תיאור.", tags='["לינוקס", "php"]')
    assert check_hebrew.problems(write(tmp_path, "2026-01-01-a-post.he.md", text)) == []


def test_an_untranslated_title_description_or_tag_is_reported(tmp_path):
    text = POST.format(title="A title", description="A description.", tags='["linux", "mysql"]')
    found = check_hebrew.problems(write(tmp_path, "2026-01-01-a-post.he.md", text))
    assert len(found) == 3
    assert "title" in found[0]
    assert "description" in found[1]
    assert "'linux'" in found[2]


def test_a_hebrew_feed_passes(tmp_path):
    text = FEED.format(feed_title="האתר האישי של מארק ולצר - mysql", author="מארק ולצר")
    assert check_hebrew.problems(write(tmp_path, "atom.xml", text)) == []


def test_english_in_a_feed_is_reported_once_per_string(tmp_path):
    text = FEED.format(feed_title="Mark Veltzer's personal site - mysql", author="Mark Veltzer")
    found = check_hebrew.problems(write(tmp_path, "atom.xml", text))
    assert found == [
        "<name> has no Hebrew in it: 'Mark Veltzer'",
        "<title> has no Hebrew in it: \"Mark Veltzer's personal site - mysql\"",
    ]


def test_the_card_name_must_be_hebrew(tmp_path):
    assert check_hebrew.problems(write(tmp_path, "he.toml", 'home_title = "מארק ולצר – מהנדס"\n')) == []
    assert check_hebrew.problems(write(tmp_path, "he.toml", 'home_title = "Mark Veltzer – מהנדס"\n'))
