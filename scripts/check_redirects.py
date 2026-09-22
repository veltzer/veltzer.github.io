#!/usr/bin/env python

"""Check the deployed site still serves every retired URL.

Search Console reports an indexing problem weeks after it appears, so this
answers the smaller question that does not need Google: is the fix still
live? It reads LEGACY_REDIRECTS from build_site.py -- the same map the build
generates stubs from -- and requests each source against the real site, so
the list cannot drift out of step with what is deployed.

What it deliberately does not do is read a validation verdict. That lives
behind a Google login, there is no API key for this property, and inventing
a verdict would be worse than not having one. See doc/SEO.md for where to
read it by hand.

Exits non-zero if anything fails, so it can gate a deploy or run from cron.
"""

import sys
import urllib.error
import urllib.parse
import urllib.request

from build_site import LEGACY_REDIRECTS, base_url

# Hosts that must each collapse to the canonical one in a single hop. A chain
# or a 200 here splits ranking across hostnames.
ALTERNATE_HOSTS = [
    "http://veltzer.org/",
    "http://www.veltzer.org/",
    "https://www.veltzer.org/",
]

TIMEOUT = 30


def fetch_status(url, follow):
    """Return (status, location) for url, without raising on 3xx or 4xx."""

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    handlers = [] if follow else [NoRedirect]
    opener = urllib.request.build_opener(*handlers)
    request = urllib.request.Request(url, method="GET")
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            return response.status, response.headers.get("Location")
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Location")
    except (urllib.error.URLError, TimeoutError) as error:
        return None, str(error)


def check_redirects(site):
    """Every source in the map must serve a page, not a 404."""
    failures = []
    for source in sorted(LEGACY_REDIRECTS):
        # The map holds raw characters; a Hebrew slug has to go out encoded.
        url = site + "/" + urllib.parse.quote(source)
        if not source.rsplit("/", 1)[-1].count("."):
            url += "/"
        status, _ = fetch_status(url, follow=True)
        if status != 200:
            failures.append(f"{status} {url}")
    return failures


def check_hosts():
    """Each non-canonical host redirects once to the canonical one."""
    failures = []
    for url in ALTERNATE_HOSTS:
        status, location = fetch_status(url, follow=False)
        if status != 301:
            failures.append(f"{status} (want 301) {url}")
        elif location != "https://veltzer.org/":
            failures.append(f"301 -> {location} (want https://veltzer.org/) {url}")
    return failures


def check_sitemap(site):
    """The sitemap lists real pages only: no paginator redirect stubs."""
    status, _ = fetch_status(site + "/sitemap.xml", follow=True)
    if status != 200:
        return [f"{status} {site}/sitemap.xml"], 0
    with urllib.request.urlopen(site + "/sitemap.xml", timeout=TIMEOUT) as response:
        body = response.read().decode("utf-8")
    entries = body.count("<loc>")
    stubs = body.count("/page/1/</loc>")
    failures = []
    if stubs:
        failures.append(f"{stubs} /page/1/ entries in the sitemap (want 0)")
    if not entries:
        failures.append("sitemap lists no URLs at all")
    return failures, entries


def main():
    site = base_url().rstrip("/")
    print(f"checking {site}\n")

    redirects = check_redirects(site)
    print(f"retired URLs: {len(LEGACY_REDIRECTS)} checked, {len(redirects)} failed")

    hosts = check_hosts()
    print(f"host variants: {len(ALTERNATE_HOSTS)} checked, {len(hosts)} failed")

    sitemap, entries = check_sitemap(site)
    print(f"sitemap: {entries} URLs, {len(sitemap)} problems")

    failures = redirects + hosts + sitemap
    if failures:
        print("\nFAILED:")
        for failure in failures:
            print(f"  {failure}")
        print("\nThis is a regression in this repo, and would explain a failed")
        print("Search Console validation. See doc/SEO.md.")
        return 1

    print("\nAll good. The deployed fix is intact.")
    print("The validation verdict itself must be read while logged in:")
    print("https://search.google.com/search-console/index?resource_id=sc-domain%3Aveltzer.org")
    return 0


if __name__ == "__main__":
    sys.exit(main())
