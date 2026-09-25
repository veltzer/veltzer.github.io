#!/usr/bin/env python

"""
Search for podcasts using the iTunes Search API and add one to the YAML file.
Interactive: search, pick from results, confirm, and append.
"""

import argparse
import sys

import requests
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

SEARCH_URL = "https://itunes.apple.com/search"


def search_podcasts(query, limit=10):
    """Search the iTunes podcast directory."""
    params = {
        "term": query,
        "media": "podcast",
        "entity": "podcast",
        "limit": limit,
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("results", [])


def display_results(results):
    """Print search results in a numbered list."""
    if not results:
        print("No results found.")
        return
    for i, r in enumerate(results, 1):
        name = r.get("trackName") or r.get("collectionName", "?")
        author = r.get("artistName", "?")
        episodes = r.get("trackCount", "?")
        genre = r.get("primaryGenreName", "?")
        print(f"  {i:>2}. {name}")
        print(f"      by {author}  |  {episodes} episodes  |  {genre}")


def pick_result(results):
    """Let the user pick a result by number, search again, or quit."""
    while True:
        choice = input("\nEnter number to add, 's' to search again, or 'q' to quit: ").strip()
        if choice.lower() == "q":
            return None
        if choice.lower() == "s":
            return "search_again"
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            return results[int(choice) - 1]
        print(f"Invalid choice. Enter 1-{len(results)}, 's', or 'q'.")


def get_next_internal_id(data):
    """Find the next available internal_id."""
    max_id = 0
    for item in data.get("items", []):
        iid = item.get("internal_id", 0)
        if isinstance(iid, (int, float)) and iid > max_id:
            max_id = int(iid)
    return max_id + 1


def add_podcast_to_yaml(file_path, podcast_info):
    """Append a new podcast entry to the YAML file."""
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'.")
        return False

    name = podcast_info.get("trackName") or podcast_info.get("collectionName", "Unknown")
    url = podcast_info.get("collectionViewUrl") or podcast_info.get("trackViewUrl", "")
    rss_feed = podcast_info.get("feedUrl", "")
    next_id = get_next_internal_id(data)

    new_entry = {
        "name": DQ(name),
        "url": DQ(url),
        "rss_feed": DQ(rss_feed),
        "chapters": [],
        "rating": 0,
        "review": DQ(""),
        "internal_id": next_id,
    }

    data["items"].append(new_entry)

    with open(file_path, "w", encoding="UTF8") as f:
        yaml.dump(data, f)

    print(f"\nAdded \"{name}\" to {file_path} (internal_id: {next_id}).")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Search for podcasts and add one to a YAML file."
    )
    parser.add_argument("yaml_file", nargs="?", default="data/yaml/podcasts.yaml", help="The YAML file to add the podcast to.")
    parser.add_argument("query", nargs="?", help="Initial search query (optional, will prompt if omitted).")
    parser.add_argument("--limit", type=int, default=10, help="Max search results (default: 10).")
    args = parser.parse_args()

    query = args.query
    while True:
        if not query:
            query = input("Search for a podcast: ").strip()
            if not query:
                continue

        print(f"\nSearching for \"{query}\"...\n")
        try:
            results = search_podcasts(query, args.limit)
        except requests.exceptions.RequestException as e:
            print(f"Error searching: {e}")
            query = None
            continue

        display_results(results)

        if not results:
            query = None
            continue

        choice = pick_result(results)
        if choice is None:
            print("Cancelled.")
            sys.exit(0)
        if choice == "search_again":
            query = None
            continue

        # Confirm
        name = choice.get("trackName") or choice.get("collectionName", "?")
        confirm = input(f"\nAdd \"{name}\" to {args.yaml_file}? [y/N] ").strip().lower()
        if confirm in ("y", "yes"):
            add_podcast_to_yaml(args.yaml_file, choice)
        else:
            print("Skipped.")
        break


if __name__ == "__main__":
    main()
