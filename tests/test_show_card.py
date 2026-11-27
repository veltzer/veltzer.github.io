"""Tests for show_card.py, the script that shows a post's share card."""

from PIL import Image

import show_card

# The head as rssite writes it: minified, the attributes unquoted.
HEAD = (
    "<!doctype html><html lang=en><head><title>A Post</title>"
    "<meta content=https://veltzer.org/en/blog/a-post/ property=og:url>"
    '<meta content="A Post" property=og:title>'
    '<meta content="What the post argues." property=og:description>'
    "<meta content=https://veltzer.org/images/og/2026-01-01-a-post.en.jpg property=og:image>"
    "<meta content=1200 property=og:image:width>"
    "<meta content=630 property=og:image:height>"
    "<meta content=summary_large_image name=twitter:card>"
    "<meta content=https://veltzer.org/second.jpg property=og:image>"
    "</head><body></body></html>"
)


def test_meta_tags_reads_unquoted_attributes() -> None:
    tags = show_card.meta_tags(HEAD)
    assert tags["og:title"] == "A Post"
    assert tags["og:url"] == "https://veltzer.org/en/blog/a-post/"
    assert tags["twitter:card"] == "summary_large_image"


def test_meta_tags_keeps_the_first_of_a_repeated_tag() -> None:
    assert show_card.meta_tags(HEAD)["og:image"] == "https://veltzer.org/images/og/2026-01-01-a-post.en.jpg"


def test_a_sound_card_has_no_problems() -> None:
    picture = Image.new("RGB", show_card.CARD_SIZE)
    assert show_card.problems(show_card.meta_tags(HEAD), b"x", "image/jpeg", picture) == []


def test_problems_names_what_is_wrong() -> None:
    tags = show_card.meta_tags(HEAD)
    del tags["og:description"]
    picture = Image.new("RGB", (600, 600))
    found = show_card.problems(tags, b"x" * (show_card.MAX_BYTES + 1), "text/html", picture)
    assert len(found) == 5
    assert "og:description is missing" in found


def test_clipped_marks_the_cut() -> None:
    assert show_card.clipped(["one", "two"], 2) == ["one", "two"]
    assert show_card.clipped(["one", "two,", "three"], 2) == ["one", "two…"]


def test_local_path_maps_a_url_into_the_site() -> None:
    page = show_card.local_path(show_card.base_url() + "/en/blog/a-post/")
    assert page == show_card.SITE / "en" / "blog" / "a-post" / "index.html"
    picture = show_card.local_path(show_card.base_url() + "/images/og/a.jpg?h=1")
    assert picture == show_card.SITE / "images" / "og" / "a.jpg"
