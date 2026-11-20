#!/usr/bin/env python

"""Compare the pages Google has indexed with the pages the sitemap lists.

Google has no call that returns "every indexed URL of this site". The two
it does have are used together, cheapest first:

1. Search Analytics, one request for the whole site: every page that showed
   up in a search result in the last --days days. A page that was shown is
   indexed, so this settles most of the sitemap at once.
2. URL Inspection, one request per page, for the pages step 1 did not
   settle. This is the verdict the Search Console page shows, and it names
   the reason a page is not indexed. It is the slow half: about seven
   seconds a page, and a quota of 2000 a day. So step 1 runs first, and a
   page inspected and found indexed is remembered in CACHE for --max-age
   days: a first run inspects several hundred pages, later ones only the
   new pages and the ones still waiting. --no-inspect skips the step.

Authentication is the gcloud login, not a key in a file: the token comes
from `gcloud auth application-default print-access-token`, and that login
must carry the Search Console scope. Once:

    gcloud auth application-default login \\
        --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters.readonly
    gcloud services enable searchconsole.googleapis.com

Not part of the build: it talks to the network and reports Google's state,
not the tree's. It always exits 0 when it could ask; a page waiting to be
crawled is not a failure of this repo. See doc/SEO.md.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
import tomllib
import urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

CONFIG = tomllib.loads(
    (Path(__file__).resolve().parent.parent / "rssite.toml").read_text(encoding="utf-8")
)
SITE = CONFIG["base_url"].rstrip("/")
# The Search Console property: a domain property, which covers every host
# and every repository that publishes under the domain.
PROPERTY = "sc-domain:" + (urllib.parse.urlparse(SITE).hostname or "")
API = "https://searchconsole.googleapis.com"
ADC_FILE = Path.home() / ".config/gcloud/application_default_credentials.json"
TIMEOUT = 60
# Search Analytics returns at most this many rows a request.
PAGE_ROWS = 25000
# Attempts at one request before giving up on it.
RETRIES = 3
# Parallel URL inspections; well inside the 600-a-minute quota.
WORKERS = 8
# Pages an inspection found indexed, with the day it said so. Google's state,
# not the tree's, so it lives outside the repository.
CACHE = Path.home() / ".cache" / "veltzer.github.io" / "indexed.json"


def session(project):
    """A requests session carrying the gcloud token and the quota project."""
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"no gcloud application-default login:\n{result.stderr.strip()}")
    if project is None and ADC_FILE.exists():
        project = json.loads(ADC_FILE.read_text(encoding="utf-8")).get("quota_project_id")
    if not project:
        sys.exit("no quota project: pass --project or set one on the gcloud login")
    http = requests.Session()
    http.headers["Authorization"] = f"Bearer {result.stdout.strip()}"
    http.headers["x-goog-user-project"] = project
    return http


def post(http, url, body):
    """POST json and return the decoded answer, or exit with Google's reason.

    A request that times out or loses its connection is tried RETRIES times
    in all: one inspection in a few hundred stalls (seen 2026-11-20, a read
    timeout after 60 seconds), and the next attempt answers.
    """
    for attempt in range(1, RETRIES + 1):
        try:
            response = http.post(url, json=body, timeout=TIMEOUT)
            break
        except (requests.Timeout, requests.ConnectionError):
            if attempt == RETRIES:
                raise
    if response.status_code != 200:
        try:
            message = response.json()["error"]["message"]
        except (ValueError, KeyError):
            message = response.text[:300]
        sys.exit(f"{response.status_code} from {url}\n{message}\n\nSee the docstring for the one-time login.")
    return response.json()


def sitemap_urls():
    """Every <loc> of the live sitemap."""
    response = requests.get(SITE + "/sitemap.xml", timeout=TIMEOUT)
    response.raise_for_status()
    return re.findall(r"<loc>([^<]+)</loc>", response.text)


def shown_pages(http, days):
    """Every page of the property that appeared in a search result."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    url = f"{API}/webmasters/v3/sites/{urllib.parse.quote(PROPERTY, safe='')}/searchAnalytics/query"
    pages = set()
    start_row = 0
    while True:
        rows = post(http, url, {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": PAGE_ROWS,
            "startRow": start_row,
        }).get("rows", [])
        pages.update(row["keys"][0] for row in rows)
        if len(rows) < PAGE_ROWS:
            return pages
        start_row += PAGE_ROWS


def inspect(http, page):
    """(indexed, coverage state) for one page, as Search Console reports it.

    A page Google would not answer for is reported as not inspected, in the
    list with the unindexed ones, and the run goes on: it is not cached, so
    the next run asks again.
    """
    try:
        status = post(http, f"{API}/v1/urlInspection/index:inspect", {
            "inspectionUrl": page,
            "siteUrl": PROPERTY,
        })["inspectionResult"]["indexStatusResult"]
    except (requests.Timeout, requests.ConnectionError) as error:
        return False, f"not inspected: {type(error).__name__} after {RETRIES} attempts"
    return status.get("verdict") == "PASS", status.get("coverageState", "unknown")


def load_cache(max_age):
    """The cached indexed pages that are still fresh: {url: iso date}."""
    if not CACHE.exists():
        return {}
    oldest = (datetime.date.today() - datetime.timedelta(days=max_age)).isoformat()
    cached = json.loads(CACHE.read_text(encoding="utf-8"))
    # Strictly newer: an entry is fresh for max_age days, so 0 trusts none,
    # not even one written earlier today.
    return {page: day for page, day in cached.items() if day > oldest}


def save_cache(cache):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def inspect_all(http, pages, cache):
    """{page: coverage state} for the pages that are not indexed.

    Every indexed verdict goes into the cache, which is saved as the answers
    arrive so that an interrupted run keeps what it paid for.
    """
    today = datetime.date.today().isoformat()
    by_page = {}
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(inspect, http, page): page for page in pages}
            for done, future in enumerate(as_completed(futures), 1):
                page = futures[future]
                indexed, state = future.result()
                if indexed:
                    cache[page] = today
                else:
                    by_page[page] = state
                if done % 20 == 0 or done == len(pages):
                    save_cache(cache)
                    print(f"\rinspected {done} of {len(pages)}", end="", file=sys.stderr, flush=True)
    finally:
        # A failed request ends the run; the answers since the last save
        # were paid for all the same.
        if pages:
            save_cache(cache)
    if pages:
        print(file=sys.stderr)
    return by_page


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=90, help="how far back a search appearance counts (default 90)")
    parser.add_argument("--no-inspect", action="store_true", help="skip the per-page inspection of the pages not seen in search")
    parser.add_argument("--max-age", type=int, default=30, help="days an inspection that said 'indexed' is trusted (default 30; 0 inspects everything again)")
    parser.add_argument("--project", help="Google Cloud quota project (default: the one on the gcloud login)")
    args = parser.parse_args()

    http = session(args.project)
    listed = sitemap_urls()
    shown = shown_pages(http, args.days)
    cache = load_cache(args.max_age)
    not_shown = [page for page in listed if page not in shown]
    unsettled = [page for page in not_shown if page not in cache]
    print(f"sitemap: {len(listed)} URLs")
    print(f"shown in search in the last {args.days} days: {len(listed) - len(not_shown)}")
    print(f"inspected and indexed in the last {args.max_age} days: {len(not_shown) - len(unsettled)}")

    if args.no_inspect:
        print(f"not settled, not inspected: {len(unsettled)}")
        for page in unsettled:
            print(f"  {urllib.parse.unquote(page)}")
        return 0

    not_indexed = inspect_all(http, unsettled, cache)
    by_state = defaultdict(list)
    for page in unsettled:
        if page in not_indexed:
            by_state[not_indexed[page]].append(page)
    missing = len(not_indexed)
    print(f"inspected now: {len(unsettled)}, of which indexed: {len(unsettled) - missing}")
    print(f"\nindexed: {len(listed) - missing} of {len(listed)}, not indexed: {missing}")
    for state, pages in sorted(by_state.items(), key=lambda item: -len(item[1])):
        print(f"\n{state} ({len(pages)}):")
        for page in pages:
            print(f"  {urllib.parse.unquote(page)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
