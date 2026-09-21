"""The tag-translation table gen_stats.py derives from the posts.

A post and its translation list the same tags in the same order, so position
N in one is position N in the other. The table is what lets a tag page link
to the same tag in the other language, and a wrong row would send a reader
to an unrelated tag, so the derivation must refuse anything that is not a
clean bijection.
"""

import gen_stats
import pytest

POST = """+++
title = "x"
date = 2026-01-01

[taxonomies]
tags = [{tags}]
+++
body
"""


def write_pair(blog_dir, stem, en_tags, he_tags):
    for lang, tags in (("en", en_tags), ("he", he_tags)):
        quoted = ", ".join(f'"{tag}"' for tag in tags)
        (blog_dir / f"{stem}.{lang}.md").write_text(POST.format(tags=quoted), encoding="utf-8")


class TestTagPairs:
    def test_pairs_by_position_across_posts(self, tmp_path):
        write_pair(tmp_path, "a", ["religion", "ethics"], ["דת", "אתיקה"])
        write_pair(tmp_path, "b", ["ethics", "linux"], ["אתיקה", "לינוקס"])
        assert gen_stats.tag_pairs(tmp_path) == [
            ("ethics", "אתיקה"),
            ("linux", "לינוקס"),
            ("religion", "דת"),
        ]

    def test_index_files_and_untagged_posts_are_ignored(self, tmp_path):
        (tmp_path / "_index.en.md").write_text("+++\ntitle = \"Blog\"\n+++\n", encoding="utf-8")
        (tmp_path / "_index.he.md").write_text("+++\ntitle = \"בלוג\"\n+++\n", encoding="utf-8")
        write_pair(tmp_path, "a", [], [])
        assert gen_stats.tag_pairs(tmp_path) == []

    def test_length_mismatch_fails(self, tmp_path):
        write_pair(tmp_path, "a", ["religion", "ethics"], ["דת"])
        with pytest.raises(SystemExit):
            gen_stats.tag_pairs(tmp_path)

    def test_inconsistent_translation_fails(self, tmp_path):
        # "ethics" lines up with two different Hebrew tags across posts:
        # some post has its lists in a different order.
        write_pair(tmp_path, "a", ["religion", "ethics"], ["דת", "אתיקה"])
        write_pair(tmp_path, "b", ["ethics", "religion"], ["דת", "אתיקה"])
        with pytest.raises(SystemExit):
            gen_stats.tag_pairs(tmp_path)

    def test_render_is_toml_rows_in_order(self):
        text = gen_stats.render_tag_translations([("ethics", "אתיקה"), ("religion", "דת")])
        assert text.count("[[terms]]") == 2
        assert 'en = "ethics"\nhe = "אתיקה"' in text
        assert text.index("ethics") < text.index("religion")
