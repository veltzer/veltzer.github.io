"""Tests for make_logo.py, the one definition of the site's logo.

The header draws the logo inline in templates/base.html (so its colours can
come from the theme), which makes that markup a second copy of the
geometry. These tests fail when the two drift apart, and when the committed
favicon.svg is not what the script would write.
"""

import re
from pathlib import Path

import make_logo

BASE_HTML = (make_logo.REPO_ROOT / "templates" / "base.html").read_text(encoding="utf-8")


def test_header_logo_matches_the_geometry():
    match = re.search(r'<svg class="site-logo"[^>]*>(.*?)</svg>', BASE_HTML)
    assert match, "no inline logo in templates/base.html"
    inner = match.group(1)
    assert f'viewBox="0 0 {make_logo.GRID} {make_logo.GRID}"' in match.group(0)
    assert f'rx="{make_logo.RADIUS}"' in inner
    assert f'd="{make_logo.PATH}"' in inner


def test_path_data_matches_the_points():
    chevron = " L".join(f"{x} {y}" for x, y in make_logo.CHEVRON)
    (cx, cy), (ex, _) = make_logo.CURSOR
    assert make_logo.PATH == f"M{chevron} M{cx} {cy} H{ex}"


def test_committed_favicon_is_current():
    committed = Path(make_logo.STATIC / "favicon.svg").read_text(encoding="utf-8")
    assert committed == make_logo.svg()


def test_mark_has_the_requested_size():
    assert make_logo.mark(48).size == (48, 48)
