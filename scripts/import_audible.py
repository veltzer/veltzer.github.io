#!/usr/bin/env python

"""Import audible.yaml from ../data, keeping only needed fields with correct types."""

import argparse
import sys

import yaml


class QuotedStr(str):
    """String subclass that forces YAML quoting."""


def _quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.add_representer(QuotedStr, _quoted_str_representer)

KEEP_FIELDS = [
    "asin",
    "title",
    "subtitle",
    "authors",
    "narrators",
    "series_title",
    "series_sequence",
    "genres",
    "runtime_length_min",
    "is_finished",
    "percent_complete",
    "rating",
    "num_ratings",
    "date_added",
    "release_date",
    "purchase_date",
]

INT_FIELDS = {"runtime_length_min", "num_ratings"}
FLOAT_FIELDS = {"percent_complete", "rating"}


def convert_item(item):
    out = {}
    for field in KEEP_FIELDS:
        value = item.get(field)
        if value is None:
            continue
        # Ensure asin stays a quoted string (preserve leading zeros)
        if field == "asin":
            value = QuotedStr(str(value))
        # Drop empty strings for optional fields
        if field in ("series_title", "series_sequence") and (not value or str(value).strip() == ""):
            continue
        # Convert numeric string fields to proper types
        if field in INT_FIELDS:
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
        elif field in FLOAT_FIELDS:
            try:
                value = float(value)
            except (ValueError, TypeError):
                pass
        out[field] = value
    return out


def main():
    parser = argparse.ArgumentParser(description="Import and clean audible.yaml")
    parser.add_argument("input", help="Input YAML file")
    parser.add_argument("output", help="Output YAML file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    items = [convert_item(item) for item in data.get("items", [])]

    with open(args.output, "w", encoding="utf-8") as f:
        yaml.dump({"items": items}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Imported {len(items)} audible items to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
