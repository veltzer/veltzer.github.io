#!/usr/bin/env python

"""
Reads a YAML file containing YouTube video data, finds items missing a 'name',
fetches the title from YouTube, and updates the file in place.
"""

import argparse
import sys

import requests
from bs4 import BeautifulSoup
from ruamel.yaml import YAML


def get_youtube_title(video_id):
    """
    Fetches the title of a YouTube video given its ID.
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # The video title is typically in the <title> tag of the page
        title_tag = soup.find('title')
        if title_tag:
            # Clean up the title string (e.g., remove "- YouTube")
            return title_tag.string.replace("- YouTube", "").strip()
        return None
    except requests.exceptions.RequestException as e:
        print(f"  - Warning: Could not fetch title for ID {video_id}: {e}")
        return None


def process_yaml_file(file_path, dry_run=False):
    """
    Loads, processes, and saves the YAML file.
    """
    print(f"--- Processing '{file_path}' ---")

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True

    with open(file_path, encoding="UTF8") as f:
        data = yaml.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print(f"Error: No 'items' list found in '{file_path}'. Skipping.")
        return

    items_to_update = []

    for i, item in enumerate(data["items"]):
        if "id" in item and "name" not in item:
            items_to_update.append((i, item))

    if not items_to_update:
        print("All items already have names. No changes needed.")
        return

    print(f"Found {len(items_to_update)} items missing a name. Fetching titles...")

    for i, item in items_to_update:
        video_id = item["id"]
        print(f" - Fetching title for ID: {video_id}")
        title = get_youtube_title(video_id)

        if title:
            # Insert the 'name' key right after the 'id' key for consistency
            item.insert(1, 'name', title)
            print(f"   + Added name: {title}")

    if dry_run:
        print("\n--- Dry Run Complete ---")
        print("The following YAML would be written:")
        yaml.dump(data, sys.stdout)
    else:
        print(f"\nSaving updated data to '{file_path}'...")
        with open(file_path, "w", encoding="UTF8") as f:
            yaml.dump(data, f)
        print("Save complete.")


def main():
    """
    Main function to handle command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fetch and add missing YouTube video titles to a YAML file."
    )
    parser.add_argument("yaml_files", nargs='+', help="One or more YAML files to process.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the output to the console instead of saving the file."
    )
    args = parser.parse_args()

    for yaml_file in args.yaml_files:
        process_yaml_file(yaml_file, args.dry_run)
        print("-" * (len(yaml_file) + 24) + "\n")


if __name__ == "__main__":
    # To run this script, you need to install the required libraries:
    # pip install ruamel.yaml requests beautifulsoup4
    main()
