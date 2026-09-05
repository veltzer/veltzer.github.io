#!/usr/bin/env python

"""Import books_read.yaml from ../data into the flat shape the media page renders.

The source is nested -- a book has a list of names (one per language, carrying
the goodreads or simania id), a list of authors each with names per language,
a list of ownings and a list of readings -- and the media app searches, sorts
and filters on flat item fields (media-app.js has no per-plugin load hook to
reshape data in the browser). So each book becomes one item with string fields
for the card and the search box, plus the small lists the plugin needs for
filters and stats.

Readings come in two shapes: dated ones carry date, timezone, rating and
review; the ones migrated from the old xml catalog only say `undated: true`.
The rating and review shown on the card are those of the most recent dated
reading; a book with only undated readings has none.

The cover image key is the same key `scripts/fetch_book_covers.py` names the
file by: `goodreads-<id>` or `simania-<id>`. Simania wins when both exist,
because the simania entry is the hebrew edition that was actually read.
"""

import argparse
import sys

import yaml


class QuotedStr(str):
    """String subclass that forces YAML quoting, so an all-digit id stays a string."""


def _quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.add_representer(QuotedStr, _quoted_str_representer)

GOODREADS_URL = "https://www.goodreads.com/book/show/{book_id}"
SIMANIA_URL = "https://simania.co.il/bookdetails.php?item_id={book_id}"

# Cover keys whose page carries no cover image (simania shows its
# "no picture yet" placeholder). No `cover` is emitted for these, so the card
# renders without an image instead of a broken one, and check_images.py does
# not report them. Remove an entry once the site has a cover.
NO_COVER = {
    "simania-67157",   # In the Dawn of My Childhood (Vera Inber)
    "simania-995897",  # The full guide to raising cats
}


def _name_in(entries, language):
    """The `name` of the entry in `language`, or None."""
    for entry in entries:
        if entry.get("language") == language and entry.get("name"):
            return entry["name"]
    return None


def _display_name(entries):
    """English name first, hebrew as the fallback -- the site's UI is english."""
    return _name_in(entries, "english") or _name_in(entries, "hebrew") or ""


def _ids(names):
    """(goodreads_id, simania_id) from whichever name entries carry them."""
    goodreads = simania = None
    for entry in names:
        goodreads = goodreads or entry.get("goodreads_id")
        simania = simania or entry.get("simania_id")
    return goodreads, simania


def _cover(goodreads, simania):
    if simania:
        key = f"simania-{simania}"
    elif goodreads:
        key = f"goodreads-{goodreads}"
    else:
        return None
    return None if key in NO_COVER else key


def _readings(item):
    """Readings sorted most recent first; undated ones after all dated ones."""
    out = []
    for reading in item.get("readings") or []:
        entry = {"language": reading.get("language", "")}
        if reading.get("date"):
            entry["date"] = reading["date"]
        if reading.get("rating") is not None:
            entry["rating"] = reading["rating"]
        if reading.get("review"):
            entry["review"] = reading["review"]
        if reading.get("undated"):
            entry["undated"] = True
        out.append(entry)
    out.sort(key=lambda r: r.get("date", ""), reverse=True)
    return out


def _subtitle(readings, owned):
    """One line for the card of a book whose latest reading has no review."""
    parts = []
    if readings:
        languages = sorted({r["language"] for r in readings if r.get("language")})
        times = "once" if len(readings) == 1 else f"{len(readings)} times"
        parts.append(f"Read {times} in {', '.join(languages)}")
        if not any("date" in r for r in readings):
            parts.append("date unknown")
    elif owned:
        parts.append("Not read yet")
    if owned:
        parts.append(f"owned in {', '.join(owned)}")
    return "; ".join(parts)


def convert_item(item):
    """One nested books_read item -> one flat media item."""
    names = item.get("names") or []
    goodreads, simania = _ids(names)
    authors = item.get("authors") or []
    author_list = [_display_name(names_of_author) for names_of_author in authors]
    author_list = [a for a in author_list if a]
    readings = _readings(item)
    owned = [o["language"] for o in item.get("ownings") or [] if o.get("language")]
    latest = next((r for r in readings if "date" in r), None)

    out = {
        "name": _display_name(names),
        "authors": ", ".join(author_list),
        "author_list": author_list,
        "language": item.get("language", ""),
        "readings": readings,
        "read_count": len(readings),
        "languages_read": sorted({r["language"] for r in readings if r.get("language")}),
        "owned_languages": owned,
    }
    hebrew = _name_in(names, "hebrew")
    if hebrew and hebrew != out["name"]:
        out["name_he"] = hebrew
    if latest:
        out["last_read"] = latest["date"]
        if "rating" in latest:
            out["rating"] = latest["rating"]
        if latest.get("review"):
            out["review"] = latest["review"]
    if "review" not in out:
        out["subtitle"] = _subtitle(readings, owned)
    for field in ("publisher", "isbn", "remark"):
        if item.get(field):
            out[field] = item[field]
    if goodreads:
        out["goodreads_id"] = QuotedStr(str(goodreads))
        out["url"] = GOODREADS_URL.format(book_id=goodreads)
    if simania:
        out["simania_id"] = QuotedStr(str(simania))
        out["url"] = SIMANIA_URL.format(book_id=simania)
    cover = _cover(goodreads, simania)
    if cover:
        out["cover"] = cover
    return out


def convert(data):
    return {"items": [convert_item(item) for item in data.get("items") or []]}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="path to books_read.yaml in the data repo")
    parser.add_argument("output", help="path of the flat yaml to write")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not data or "items" not in data:
        print(f"ERROR: {args.input} has no items", file=sys.stderr)
        return 1
    with open(args.output, "w", encoding="utf-8") as handle:
        yaml.dump(convert(data), handle, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
