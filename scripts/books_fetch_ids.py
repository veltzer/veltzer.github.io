#!/usr/bin/env python

"""
Look up goodreads ids for books in books_read.yaml that have no id yet.

For each item whose names carry neither a goodreads_id nor a simania_id,
searches goodreads (its autocomplete json endpoint; the html search and
book pages sit behind an AWS WAF challenge for non-browser clients) by
the english title, scores the hits by title similarity, author similarity
and popularity, and offers the best one. A confirmed hit is verified
against the goodreads book page, the english name is replaced by the
exact page title (`pydatacheck check_books` asserts they are equal), the
title is stored in the checker's cache, and the goodreads_id is written.
When the page title differs from the old name beyond punctuation and
case, the old name is kept in the item's remark so nothing is lost.

Incremental: writes after every accepted item, so progress is not lost, and
only rewrites the yaml block of the item it changed. Every other item stays
byte for byte as it was.

Usage:
  scripts/books_fetch_ids.py            # interactive: confirm each match
  scripts/books_fetch_ids.py --auto     # accept only confident matches, skip the rest
  scripts/books_fetch_ids.py --dry-run  # show what would be written
  scripts/books_fetch_ids.py --assign "Ulysees=338798"   # set (or replace) the goodreads id of one item by its current english name
  scripts/books_fetch_ids.py --assign-simania "Chess=11971"   # same for a simania id (hebrew books; simania search is javascript only)
"""

import argparse
import difflib
import json
import math
import os
import re
import shelve
import sys
import time
import urllib.parse

import bs4  # type: ignore
import requests
import yaml

YAML_PATH = "data/yaml/books_read.yaml"
CACHE_PATH = "/tmp/goodreads_search_cache.json"
SEARCH_URL = "https://www.goodreads.com/book/auto_complete?format=json&q={query}"
# /book/show/ answers non-browser clients with an empty 202 (WAF challenge);
# the /en/ prefixed url serves the same page. Same page pydatacheck reads.
BOOK_URL = "https://www.goodreads.com/en/book/show/{book_id}"
CHECKER_CACHE_PATH = "shelve/goodreads_id_to_goodreads_data.shelve"
SIMANIA_URL = "https://simania.co.il/bookdetails.php?item_id={book_id}"
SIMANIA_CACHE_PATH = "shelve/simania_id_to_simania_data.shelve"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) books_fetch_ids"
SERIES_RE = re.compile(r"\s*\([^)]*#\s*\d[^)]*\)\s*$")
HEBREW_RE = re.compile("[\u0590-\u05ff]")
KEY_RE = re.compile(r'^(\s*(?:- )*)"([A-Za-z_][A-Za-z0-9_]*)":', re.MULTILINE)

# thresholds for --auto
AUTO_TITLE_SIM = 0.85
AUTO_AUTHOR_SIM = 0.8
AUTO_MIN_RATINGS = 100


def load_cache():
    """Load the search cache."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Save the search cache."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)


def normalize(text):
    """Lower case, drop a trailing series marker, keep only letters, digits and spaces."""
    text = SERIES_RE.sub("", text)
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^0-9a-z֐-׿]+", " ", text)
    return " ".join(text.split())


def similarity(a, b):
    """Similarity of two strings after normalization, 0..1."""
    a, b = normalize(a), normalize(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def search_goodreads(title, session, cache, delay):
    """Search goodreads for a title and return the result rows."""
    if title in cache:
        return cache[title]
    url = SEARCH_URL.format(query=urllib.parse.quote_plus(title))
    response = session.get(url, timeout=60)
    response.raise_for_status()
    time.sleep(delay)
    rows = []
    for hit in response.json():
        rows.append({
            "id": str(hit["bookId"]),
            "title": hit.get("bookTitleBare") or hit["title"],
            "author": (hit.get("author") or {}).get("name", ""),
            "ratings": int(hit.get("ratingsCount") or 0),
        })
    cache[title] = rows
    save_cache(cache)
    return rows


def fetch_book_title(book_id, session):
    """The title on the goodreads book page, parsed the way pydatacheck check_books parses it."""
    response = session.get(BOOK_URL.format(book_id=book_id), timeout=60)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    title = soup.find(id="bookTitle")
    if title is None:
        title = soup.find("h1", {"data-testid": "bookTitle"})
    if title is None:
        raise RuntimeError(f"no title on the goodreads page of {book_id}")
    return title.text.strip()


def fetch_simania_title(book_id, session):
    """The title on the simania book page (its h1), the way pydatacheck check_books reads it."""
    response = session.get(SIMANIA_URL.format(book_id=book_id), timeout=60)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    title = soup.find("h1")
    if title is None:
        raise RuntimeError(f"no title on the simania page of {book_id}")
    return title.text.strip()


def hebrew_name(item):
    """The hebrew name entry of an item, created if missing."""
    for name in item["names"]:
        if name["language"] == "hebrew":
            return name
    name = {"language": "hebrew", "name": ""}
    item["names"].append(name)
    return name


def author_similarity(item_authors, candidate_author):
    """Best similarity between the candidate author and any of the item's authors."""
    if not item_authors:
        return 1.0
    best = 0.0
    for names in item_authors:
        for name in names:
            if name["language"] != "english":
                continue
            best = max(best, similarity(name["name"], candidate_author))
            # surname match is a strong signal on its own ("Vonnegut" vs "Kurt Vonnegut Jr.")
            surname = normalize(name["name"]).split()[-1:]
            if surname and surname[0] in normalize(candidate_author).split():
                best = max(best, 0.9)
    return best


def score_rows(item, title, rows):
    """Attach title/author similarity and a combined score to each row, best first."""
    scored = []
    for row in rows:
        # goodreads often appends a subtitle after a colon; match the bare title too
        title_sim = max(similarity(title, row["title"]), similarity(title, row["title"].split(":")[0]))
        author_sim = author_similarity(item["authors"], row["author"])
        popularity = min(math.log10(row["ratings"] + 1) / 6, 1.0)
        score = 0.6 * title_sim + 0.3 * author_sim + 0.1 * popularity
        scored.append({**row, "title_sim": title_sim, "author_sim": author_sim, "score": score})
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored


def is_confident(row):
    """Whether a scored row is good enough to accept without asking."""
    return (
        row["title_sim"] >= AUTO_TITLE_SIM
        and row["author_sim"] >= AUTO_AUTHOR_SIM
        and row["ratings"] >= AUTO_MIN_RATINGS
    )


def english_name(item):
    """The english name entry of an item, or None."""
    for name in item["names"]:
        if name["language"] == "english":
            return name
    return None


def has_id(item):
    """Whether any name of the item already carries a goodreads or simania id."""
    return any("goodreads_id" in n or "simania_id" in n for n in item["names"])


def read_blocks():
    """Split the yaml into (header, [block texts]); one block per item, starting at '  - names:'."""
    with open(YAML_PATH, encoding="utf-8") as f:
        text = f.read()
    head, sep, body = text.partition("items:\n")
    assert sep, "no items: key in yaml"
    starts = [m.start() for m in re.finditer(r"^  - names:", body, re.MULTILINE)]
    blocks = [body[s:e] for s, e in zip(starts, starts[1:] + [len(body)])]
    assert "".join(blocks) == body, "item blocks do not cover the whole file"
    return head + sep, blocks


class Dumper(yaml.SafeDumper):
    """Dump lists with indented dashes, matching the style of the yaml files."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


Dumper.add_representer(str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style='"'))


def dump_block(item):
    """Render one item as a yaml list-item block in the style of the file."""
    text = yaml.dump([item], Dumper=Dumper, allow_unicode=True, sort_keys=False, width=100000)
    text = KEY_RE.sub(r"\1\2:", text)
    return "".join("  " + line + "\n" for line in text.rstrip("\n").split("\n"))


def write_item(index, item):
    """Rewrite only the block of item `index`."""
    head, blocks = read_blocks()
    blocks[index] = dump_block(item)
    with open(YAML_PATH, "w", encoding="utf-8") as f:
        f.write(head + "".join(blocks))


def show_candidates(item, title, rows, limit):
    """Print the item and its best candidates."""
    authors = ", ".join(n["name"] for names in item["authors"] for n in names if n["language"] == "english")
    print(f"\n  YOUR YAML:  {title}  [{authors or 'no author'}]")
    for i, row in enumerate(rows[:limit], 1):
        flag = "*" if is_confident(row) else " "
        print(f"  {flag}{i}. {row['title']}  [{row['author']}]  "
              f"{row['ratings']:,} ratings  id={row['id']}  "
              f"(title {row['title_sim']:.2f}, author {row['author_sim']:.2f})")


def ask_choice(count):
    """Ask which candidate to take. Returns index, 'skip', 'quit' or a manual id."""
    while True:
        answer = input(f"  choose [1-{count}], id=<goodreads id>, s=skip, q=quit: ").strip().lower()
        if answer in ("s", ""):
            return "skip"
        if answer == "q":
            return "quit"
        if answer.startswith("id="):
            return answer[3:].strip()
        if answer.isdigit() and 1 <= int(answer) <= count:
            return int(answer) - 1
        print("  ?")


def apply(item, name, book_id, session, dry_run):
    """Verify the id on the book page and update the item in place. Returns the page title."""
    with shelve.open(CHECKER_CACHE_PATH) as cache:
        if book_id in cache:
            page_title = cache[book_id]["title"]
        else:
            page_title = fetch_book_title(book_id, session)
            if not dry_run:
                cache[book_id] = {"title": page_title}
    if HEBREW_RE.search(page_title):
        # goodreads lists the hebrew edition: record it as the hebrew name and
        # leave the english (transliterated) name untouched
        hebrew = hebrew_name(item)
        hebrew["name"] = page_title
        hebrew["goodreads_id"] = book_id
        return page_title
    old = name["name"]
    if normalize(old) != normalize(page_title) and "was named: " not in item.get("remark", ""):
        note = f"was named: {old}"
        item["remark"] = f"{item['remark']}; {note}" if item.get("remark") else note
    name["name"] = page_title
    name["goodreads_id"] = book_id
    return page_title


def apply_simania(item, book_id, session, dry_run):
    """Verify a simania id on its page and record it as the hebrew name. Returns the page title."""
    with shelve.open(SIMANIA_CACHE_PATH) as cache:
        if book_id in cache:
            page_title = cache[book_id]["title"]
        else:
            page_title = fetch_simania_title(book_id, session)
            if not dry_run:
                cache[book_id] = {"title": page_title}
    hebrew = hebrew_name(item)
    hebrew.pop("goodreads_id", None)
    hebrew["name"] = page_title
    hebrew["simania_id"] = book_id
    return page_title


def assign(items, assignments, simania_assignments, session, dry_run):
    """Apply explicit NAME=ID assignments."""
    for assignment, simania in [(a, False) for a in assignments] + [(a, True) for a in simania_assignments]:
        wanted, _, book_id = assignment.rpartition("=")
        found = [(i, item) for i, item in enumerate(items)
                 if english_name(item) is not None and english_name(item)["name"] == wanted]
        if len(found) != 1:
            print(f"  {wanted!r}: {len(found)} items match, skipped")
            continue
        index, item = found[0]
        if simania:
            page_title = apply_simania(item, book_id, session, dry_run)
        else:
            name = english_name(item)
            name.pop("goodreads_id", None)
            page_title = apply(item, name, book_id, session, dry_run)
        print(f"  {wanted} -> {'simania' if simania else 'goodreads'} id={book_id} title={page_title}")
        if not dry_run:
            write_item(index, item)
    return 0


def main():
    """main entry point"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--auto", action="store_true", help="accept confident matches only, never ask")
    parser.add_argument("--dry-run", action="store_true", help="do not write the yaml")
    parser.add_argument("--limit", type=int, default=0, help="stop after this many items without ids (0 = all)")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds to sleep between goodreads requests")
    parser.add_argument("--show", type=int, default=5, help="how many candidates to show")
    parser.add_argument("--assign", action="append", default=[], metavar="NAME=ID",
                        help="set the goodreads id of the item whose english name is NAME (replaces an existing id); repeatable")
    parser.add_argument("--assign-simania", action="append", default=[], metavar="NAME=ID",
                        help="set the simania id (as the hebrew name) of the item whose english name is NAME; repeatable")
    args = parser.parse_args()

    cache = load_cache()
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    _, blocks = read_blocks()
    items = [yaml.safe_load(b)[0] for b in blocks]
    if args.assign or args.assign_simania:
        return assign(items, args.assign, args.assign_simania, session, args.dry_run)
    todo = [(i, item) for i, item in enumerate(items) if not has_id(item)]
    print(f"{len(items)} items, {len(todo)} without an id")
    if args.limit:
        todo = todo[:args.limit]

    accepted, skipped, unresolved = 0, [], []
    for index, item in todo:
        name = english_name(item)
        if name is None:
            skipped.append((item["names"][0]["name"], "no english name to search by"))
            continue
        title = name["name"]
        rows = score_rows(item, title, search_goodreads(title, session, cache, args.delay))
        if not rows:
            unresolved.append((title, "no search results"))
            continue
        show_candidates(item, title, rows, args.show)
        chosen = None
        if is_confident(rows[0]):
            chosen = rows[0]["id"]
        if args.auto:
            if chosen is None:
                unresolved.append((title, f"best: {rows[0]['title']} [{rows[0]['author']}] id={rows[0]['id']}"))
                print("  no confident match, skipped")
                continue
        else:
            answer = ask_choice(min(args.show, len(rows)))
            if answer == "quit":
                break
            if answer == "skip":
                skipped.append((title, "skipped by user"))
                continue
            chosen = rows[answer]["id"] if isinstance(answer, int) else answer
        page_title = apply(item, name, chosen, session, args.dry_run)
        time.sleep(args.delay)
        print(f"  -> id={chosen} title={page_title}")
        if not args.dry_run:
            write_item(index, item)
        accepted += 1

    print(f"\naccepted {accepted}, skipped {len(skipped)}, unresolved {len(unresolved)}")
    for title, why in skipped + unresolved:
        print(f"  {title}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
