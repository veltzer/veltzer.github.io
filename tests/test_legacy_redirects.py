"""The retired URLs that rssite.toml's [[redirects]] turn into redirect stubs.

Every entry is a URL that shipped once and that Google still requests.
rssite already refuses a target that is not a file the build writes and a
source that would overwrite a real page; these are the invariants it does
not know about.
"""

from check_redirects import LEGACY_REDIRECTS


class TestLegacyRedirects:
    def test_sources_are_site_paths(self):
        """A source is a path below the site root, never a URL."""
        for source in LEGACY_REDIRECTS:
            assert "://" not in source, source

    def test_targets_are_rooted_and_prefixed(self):
        """Targets are site-absolute and language-prefixed. Neither language
        owns the root any more, so an unprefixed target is a dead link."""
        for source, target in LEGACY_REDIRECTS.items():
            assert target.startswith(("/en/", "/he/")), source

    def test_directory_targets_end_in_a_slash(self):
        """rssite writes every page as <dir>/index.html, so its URL ends in a
        slash; a target without one would only resolve to a file."""
        for source, target in LEGACY_REDIRECTS.items():
            last = target.rsplit("/", 1)[-1]
            assert not last or "." in last, source

    def test_no_source_redirects_to_itself(self):
        """A stub at its own target would overwrite the page it points at."""
        for source, target in LEGACY_REDIRECTS.items():
            assert target.strip("/") != source, source

    def test_no_target_is_also_a_source(self):
        """A target that is itself retired would chain one stub into another,
        and a meta-refresh chain is a link Google may decline to follow."""
        for source, target in LEGACY_REDIRECTS.items():
            assert target.strip("/") not in LEGACY_REDIRECTS, source
