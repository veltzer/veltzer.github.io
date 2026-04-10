#!/bin/bash -eu

# Build the site using MkDocs.
# MkDocs reads from blog/ (docs_dir) and writes to docs/ (site_dir).
# Static files in blog/ (HTML, JS, CSS, data) are copied through as-is.
#
# Before running this, ensure:
# - keys.js is generated (via pydmt or manually)
# - Data files are copied (via scripts/copy_data.sh)
#
# SOURCE_DATE_EPOCH is set to the latest git commit timestamp so that
# the RSS feed pubDate/lastBuildDate fields are stable across rebuilds
# (idempotent builds). The timestamps only change when content changes.
# We exclude the site_dir (docs/) from the timestamp calculation to
# avoid circular dependencies when build output is committed.

# Check all media items have images before building
# scripts/check_images.py

export SOURCE_DATE_EPOCH
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct -- . ':!docs')
export PYTHONHASHSEED=0

mkdocs build
