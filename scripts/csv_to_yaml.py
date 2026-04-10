#!/usr/bin/env python

"""Convert YouTube CSV export to trimmed YAML for the media viewer."""

import argparse
import csv
import sys

import yaml


FIELDS = [
    "title",
    "channel",
    "upload_date",
    "duration",
    "view_count",
    "categories",
    "webpage_url",
]


def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def convert_row(row):
    item = {}
    for field in FIELDS:
        value = row.get(field, "")
        if not value:
            continue
        if field in ("duration", "view_count"):
            value = parse_int(value)
            if value is None:
                continue
        if field == "upload_date" and len(value) == 8 and value.isdigit():
            value = f"{value[:4]}-{value[4:6]}-{value[6:8]}"
        item[field] = value
    return item


def main():
    parser = argparse.ArgumentParser(description="Convert YouTube CSV to YAML")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("output", help="Output YAML file")
    args = parser.parse_args()

    items = []
    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = convert_row(row)
            if not item.get("title"):
                continue
            if item["title"] == "METADATA_NOT_FOUND":
                item["status"] = "missing"
            items.append(item)

    data = {"items": items}
    with open(args.output, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Converted {len(items)} items to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
