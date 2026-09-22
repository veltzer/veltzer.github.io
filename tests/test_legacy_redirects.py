"""The map of retired URLs that build_site.py turns into redirect stubs.

Every entry is a URL that shipped once and that Google still requests. A
wrong entry is invisible at build time -- the stub is written either way --
and only shows up as a Search Console 404 weeks later, so the shape of the
map is checked here rather than trusted.

What cannot be checked here is that each target is a real page: that depends
on the built output, and write_legacy_redirects() already refuses to
overwrite one. These are the invariants that hold without a build.
"""

import build_site


class TestLegacyRedirects:
    def test_sources_are_relative_paths(self):
        """Sources are joined onto the output root, so a leading slash would
        escape it and an absolute URL would create a directory named http:."""
        for source in build_site.LEGACY_REDIRECTS:
            assert not source.startswith("/"), source
            assert "://" not in source, source

    def test_sources_have_no_trailing_slash(self):
        """A trailing slash would make Path() emit the stub one level deep."""
        for source in build_site.LEGACY_REDIRECTS:
            assert not source.endswith("/"), source

    def test_targets_are_rooted_and_prefixed(self):
        """Targets are site-absolute and language-prefixed. Neither language
        owns the root any more, so an unprefixed target is a dead link."""
        for source, target in build_site.LEGACY_REDIRECTS.items():
            assert target.startswith("/"), source
            assert target.startswith(("/en/", "/he/")), source

    def test_directory_targets_end_in_a_slash(self):
        """Zola writes every page as <dir>/index.html, so its URL ends in a
        slash. Only a file target -- the public key -- may not."""
        for source, target in build_site.LEGACY_REDIRECTS.items():
            if not target.rsplit("/", 1)[-1]:
                continue
            assert "." in target.rsplit("/", 1)[-1], source

    def test_no_source_redirects_to_itself(self):
        """A stub at its own target would overwrite the page it points at."""
        for source, target in build_site.LEGACY_REDIRECTS.items():
            assert target.strip("/") != source.strip("/"), source

    def test_no_target_is_also_a_source(self):
        """A target that is itself retired would chain one stub into another,
        and a meta-refresh chain is a link Google may decline to follow."""
        sources = {source.strip("/") for source in build_site.LEGACY_REDIRECTS}
        for source, target in build_site.LEGACY_REDIRECTS.items():
            assert target.strip("/") not in sources, source
