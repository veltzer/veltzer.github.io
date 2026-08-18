#!/usr/bin/env python

"""
Check that the profile URLs in ../data/yaml/profiles.yaml still resolve.

Those ~30 links are rendered into content/about/ here and into README.md in the
../veltzer repository. They are exactly the kind of URL that dies quietly: a
service shuts down, a username changes, a profile goes private, and nothing
notices because no build step ever requests them.

Deliberately NOT part of `rsconstruct build`. A third-party outage must not fail
a site build, and the check needs the network, which the build otherwise does
not. Run it on demand:

    scripts/check_profile_links.py

Exit status is 1 if anything is reported, so it can still gate a release script
if that is ever wanted.

On what counts as a failure: only connection errors and 4xx are reported as
broken. Several of these hosts answer a bare HEAD or an unknown client with 403
or 405 while serving the page perfectly well in a browser, so the checker
retries with GET, sends a browser User-Agent, and reports 403/429 separately as
"blocked" rather than dead. That distinction is the whole difficulty here --
without it the report is mostly false positives and gets ignored, which is worse
than no checker.
"""

import argparse
import concurrent.futures
import logging
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = REPO_ROOT.parent / "data" / "yaml" / "profiles.yaml"

# A browser UA. Several of these sites (goodreads, imdb, udemy) return 403 to
# anything that identifies itself as a script, so the default urllib agent makes
# the check useless.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
TIMEOUT = 20

# Reported, but as "blocked" rather than "broken": the host is up and answering,
# it just will not serve an automated client. A human following the link is
# unaffected, so these are not actionable the way a 404 is.
BLOCKED_STATUSES = {401, 403, 405, 429, 999}

logger = logging.getLogger(__name__)


def die(message):
    """Print an error to stderr and exit non-zero."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_links():
    """Every (label, url) in the file, including the nested children."""
    if not YAML_PATH.is_file():
        die(f"Missing {YAML_PATH}. Clone the data repo alongside this one.")
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    groups = data.get("groups")
    if not groups:
        die(f"{YAML_PATH} has no 'groups' key")

    links = []
    for group in groups:
        for item in group["items"]:
            links.append((item["name"], item["url"]))
            for child in item.get("children", []):
                links.append((child["name"], child["url"]))
    return links


def request(url, method):
    """Return the HTTP status for one request, or an error string."""
    req = urllib.request.Request(url, method=method)
    req.add_header("User-Agent", USER_AGENT)
    # Some hosts vary their response on these; sending them makes the request
    # look less like a bare script.
    req.add_header("Accept", "text/html,application/xhtml+xml,*/*;q=0.8")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return response.status, None
    except urllib.error.HTTPError as error:
        # An HTTP error is still an answer from the server.
        return error.code, None
    except (urllib.error.URLError, OSError, ValueError) as error:
        return None, str(getattr(error, "reason", error))


def check(link):
    """Classify one link as ok, blocked or broken.

    HEAD first because it avoids downloading the page, then GET on anything that
    is not a clean 2xx: a fair number of hosts do not implement HEAD properly and
    answer 403/405 to it while serving GET normally.
    """
    name, url = link
    status, error = request(url, "HEAD")
    if error is not None or status is None or status >= 400:
        status, error = request(url, "GET")

    if error is not None:
        return "broken", name, url, error
    if status in BLOCKED_STATUSES:
        return "blocked", name, url, f"HTTP {status}"
    if status >= 400:
        return "broken", name, url, f"HTTP {status}"
    return "ok", name, url, f"HTTP {status}"


def main():
    """Check every profile URL and report anything that is not plainly fine."""
    parser = argparse.ArgumentParser(
        description="Check the profile URLs in ../data/yaml/profiles.yaml"
    )
    parser.add_argument(
        "--jobs", type=int, default=8,
        help="Concurrent requests (default: 8)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="List the working links too, not just the problems",
    )
    args = parser.parse_args()

    # Bare message format: this is an interactive tool whose output is read by a
    # person, not a log file.
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    links = load_links()
    logger.info("Checking %d profile URLs...", len(links))

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(check, links))

    broken = [r for r in results if r[0] == "broken"]
    blocked = [r for r in results if r[0] == "blocked"]
    ok = [r for r in results if r[0] == "ok"]

    if args.verbose:
        for _, name, url, detail in ok:
            logger.info("  ok      %-22s %s (%s)", name, url, detail)

    for _, name, url, detail in blocked:
        logger.info("  blocked %-22s %s (%s)", name, url, detail)
    for _, name, url, detail in broken:
        logger.info("  BROKEN  %-22s %s (%s)", name, url, detail)

    logger.info("")
    logger.info("%d ok, %d blocked, %d broken", len(ok), len(blocked), len(broken))
    if blocked:
        logger.info(
            "Blocked means the host answered but refuses automated clients; "
            "open one in a browser before treating it as dead."
        )
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
