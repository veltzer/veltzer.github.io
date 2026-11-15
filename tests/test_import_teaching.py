"""Tests for import_teaching.py's stylesheet scoping.

The teaching sites' CSS is pasted into this site's pages, so every rule must be
confined to the wrapper id. The cases here are the selector shapes that a
naive split-on-comma, prefix-with-wrapper approach gets wrong.
"""

import import_teaching

W = "app"


def scope(selector):
    return import_teaching.scope_selector(selector, W)


class TestSplitSelectors:
    def test_plain_list(self):
        assert import_teaching.split_selectors("a, b ,c") == ["a", "b", "c"]

    def test_commas_inside_parentheses_do_not_split(self):
        assert import_teaching.split_selectors(":is(a, b) .x, .y") == [":is(a, b) .x", ".y"]

    def test_commas_inside_brackets_and_strings_do_not_split(self):
        assert import_teaching.split_selectors('a[title="x,y"], b[c=d]') == ['a[title="x,y"]', "b[c=d]"]


class TestScopeSelector:
    def test_document_selectors_become_the_wrapper(self):
        assert scope(":root") == "#app"
        assert scope("body") == "#app"

    def test_plain_selector_is_prefixed(self):
        assert scope(".card") == "#app .card"

    def test_data_theme_stays_an_ancestor(self):
        assert scope("[data-theme=dark] .card") == "[data-theme=dark] #app .card"

    def test_html_and_root_attribute_prefixes_stay_an_ancestor(self):
        assert scope("html[data-theme=dark] .card") == "html[data-theme=dark] #app .card"
        assert scope(":root[data-theme=dark]") == ":root[data-theme=dark] #app"

    def test_other_attribute_selector_on_an_element_is_scoped_inside(self):
        assert scope("[hidden]") == "#app [hidden]"


class TestScopeCss:
    def test_is_list_stays_one_selector(self):
        out = import_teaching.scope_css(":is(a, b) .x { color: red; }", W)
        assert out.startswith("#app :is(a, b) .x {")

    def test_each_top_level_selector_is_scoped(self):
        out = import_teaching.scope_css("a, b { color: red; }", W)
        assert out == "#app a, #app b { color: red; }"

    def test_media_block_is_scoped_inside(self):
        out = import_teaching.scope_css("@media (max-width: 600px) { .x { top: 0; } }", W)
        assert "#app .x" in out
        assert out.startswith("@media (max-width: 600px) {")
