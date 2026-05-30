#!/usr/bin/env python

"""
Build the site using MkDocs.

MkDocs reads from blog/ (docs_dir) and writes to _site/ (site_dir).
Static files in blog/ (HTML, JS, CSS, data) are copied through as-is.

Before running this, ensure:
- keys.js is generated (via rsconstruct or manually)
- Data files are copied (via scripts/copy_data.py)

SOURCE_DATE_EPOCH is set to the latest git commit timestamp so that
the RSS feed pubDate/lastBuildDate fields are stable across rebuilds
(idempotent builds). The timestamps only change when content changes.
We exclude the site_dir from the timestamp calculation to avoid
circular dependencies when build output is committed.
"""

import os
import subprocess
import sys


def latest_commit_epoch():
    """Latest git commit timestamp, excluding the build output dir."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", ".", ":(exclude)_site"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main():
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = latest_commit_epoch()
    env["PYTHONHASHSEED"] = "0"

    try:
        subprocess.run(["mkdocs", "build"], check=True, env=env)
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
