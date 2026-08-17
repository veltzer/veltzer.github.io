"""Guard the templates against reintroducing non-reproducible output.

zola's `page.translations` comes out in a different order on different runs of
identical input -- three consecutive builds emitted the two hreflang alternates
as "he en", "he en", then "en he". Any template that iterates that list
directly and emits one line per item therefore makes the build
non-byte-reproducible, which in turn makes it impossible to validate a build
change by diffing output.

The fix in both places was to loop `config.extra.languages`, which is a fixed
list in config.toml, and look each language up in page.translations. This test
asserts that shape rather than re-running zola twice: a build takes seconds and
needs zola on PATH, while the property that actually matters is visible in the
template source.
"""

import re
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# `{% for x in page.translations %}` in any spacing/whitespace-control form.
DIRECT_LOOP = re.compile(
    r"\{%-?\s*for\s+\w+\s+in\s+page\.translations\s*-?%\}"
)
LANGUAGES_LOOP = re.compile(
    r"\{%-?\s*for\s+\w+\s+in\s+config\.extra\.languages\s*-?%\}"
)
ENDFOR = re.compile(r"\{%-?\s*endfor\s*-?%\}")


def templates_with_translations():
    """Every template that mentions page.translations at all."""
    return [
        path for path in sorted(TEMPLATES.glob("*.html"))
        if "page.translations" in path.read_text(encoding="utf-8")
    ]


class TestTranslationOrdering:
    def test_some_template_uses_translations(self):
        # Guards the test itself: if the templates stop mentioning
        # page.translations entirely, the checks below would pass vacuously.
        assert templates_with_translations()

    def test_every_translations_loop_has_a_stable_outer_loop(self):
        """Each `for ... in page.translations` must be nested inside a
        `for ... in config.extra.languages`.

        Checked per occurrence, not per file: base.html contains two such loops
        and an unrelated languages loop, so a file-level check passes even with
        one of them broken. Verified by reintroducing the bug -- a file-level
        assertion did not catch it.
        """
        offenders = []
        for path in templates_with_translations():
            text = path.read_text(encoding="utf-8")
            for match in DIRECT_LOOP.finditer(text):
                before = text[:match.start()]
                # The nearest enclosing loop must be over the config list. Count
                # unclosed `for` blocks by walking backwards from this loop.
                opens = [m for m in LANGUAGES_LOOP.finditer(before)]
                if not opens:
                    offenders.append(f"{path.name}:{before.count(chr(10)) + 1}")
                    continue
                between = text[opens[-1].end():match.start()]
                if ENDFOR.search(between):
                    offenders.append(f"{path.name}:{before.count(chr(10)) + 1}")
        assert not offenders, (
            "These `for ... in page.translations` loops are not nested inside "
            "a loop over config.extra.languages, so their output order varies "
            f"between builds: {offenders}"
        )

    def test_inner_loop_is_filtered_by_language_code(self):
        # The outer loop only helps if the inner one selects the matching
        # language rather than emitting every translation per entry.
        for path in templates_with_translations():
            text = path.read_text(encoding="utf-8")
            if not DIRECT_LOOP.search(text):
                continue
            assert "translation.lang == entry.code" in text, (
                f"{path.name} loops config.extra.languages and "
                "page.translations but never matches them up"
            )
