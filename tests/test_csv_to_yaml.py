"""Tests for csv_to_yaml.py, which converts the YouTube CSV export to YAML.

This script processes ~29,000 records with no other coverage, so the cases here
target the transformations whose silent failure would corrupt the media
database rather than raise: the YYYYMMDD date rewrite, integer coercion, and
the METADATA_NOT_FOUND handling that keeps unfetchable videos linkable.
"""

import csv_to_yaml


class TestParseInt:
    def test_parses_digits(self):
        assert csv_to_yaml.parse_int("42") == 42

    def test_returns_none_for_empty(self):
        assert csv_to_yaml.parse_int("") is None

    def test_returns_none_for_non_numeric(self):
        assert csv_to_yaml.parse_int("N/A") is None

    def test_returns_none_for_none(self):
        assert csv_to_yaml.parse_int(None) is None

    def test_does_not_truncate_float_strings_silently(self):
        # "1.5" is not a valid int literal, so it must be dropped rather than
        # silently becoming 1.
        assert csv_to_yaml.parse_int("1.5") is None


class TestUploadDateConversion:
    def test_converts_yyyymmdd_to_iso(self):
        row = {"title": "t", "upload_date": "20240115"}
        assert csv_to_yaml.convert_row(row)["upload_date"] == "2024-01-15"

    def test_leaves_already_iso_dates_alone(self):
        row = {"title": "t", "upload_date": "2024-01-15"}
        assert csv_to_yaml.convert_row(row)["upload_date"] == "2024-01-15"

    def test_leaves_non_digit_eight_char_values_alone(self):
        # Same length as YYYYMMDD but not digits, so the reformat must not fire.
        row = {"title": "t", "upload_date": "abcdefgh"}
        assert csv_to_yaml.convert_row(row)["upload_date"] == "abcdefgh"

    def test_omits_empty_upload_date(self):
        row = {"title": "t", "upload_date": ""}
        assert "upload_date" not in csv_to_yaml.convert_row(row)


class TestConvertRow:
    def test_keeps_only_known_fields(self):
        row = {"title": "t", "channel": "c", "unwanted": "x"}
        item = csv_to_yaml.convert_row(row)
        assert "unwanted" not in item
        assert item["title"] == "t"
        assert item["channel"] == "c"

    def test_coerces_numeric_fields_to_int(self):
        item = csv_to_yaml.convert_row(
            {"title": "t", "duration": "300", "view_count": "1000"}
        )
        assert item["duration"] == 300
        assert item["view_count"] == 1000
        assert isinstance(item["duration"], int)
        assert isinstance(item["view_count"], int)

    def test_drops_unparseable_numeric_fields(self):
        item = csv_to_yaml.convert_row(
            {"title": "t", "duration": "not-a-number", "view_count": ""}
        )
        assert "duration" not in item
        assert "view_count" not in item

    def test_zero_view_count_is_kept(self):
        # Documents current behaviour: the `if not value` guard runs on the raw
        # string, so "0" survives it and becomes int 0.
        item = csv_to_yaml.convert_row({"title": "t", "view_count": "0"})
        assert item["view_count"] == 0

    def test_empty_row_yields_empty_item(self):
        # Deliberately `== {}` rather than `not ...`: this asserts the result is an
        # empty dict, not merely something falsy.
        # pylint: disable=use-implicit-booleaness-not-comparison
        assert csv_to_yaml.convert_row({}) == {}
