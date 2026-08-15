"""Tests for import_audible.py, which cleans audible.yaml from ../data.

Focused on the conversions recorded as fixes in doc/IMPROVEMENTS.md -- numeric
fields that used to be strings, and empty optional fields that used to be
emitted -- plus the asin quoting that keeps leading zeros from being eaten.
"""

import import_audible
import yaml


class TestNumericConversion:
    def test_int_fields_become_ints(self):
        out = import_audible.convert_item(
            {"runtime_length_min": "360", "num_ratings": "42"}
        )
        assert out["runtime_length_min"] == 360
        assert out["num_ratings"] == 42
        assert isinstance(out["runtime_length_min"], int)

    def test_float_fields_become_floats(self):
        out = import_audible.convert_item({"rating": "4.5", "percent_complete": "80"})
        assert out["rating"] == 4.5
        assert out["percent_complete"] == 80.0
        assert isinstance(out["percent_complete"], float)

    def test_unparseable_numerics_are_left_as_is(self):
        # The script swallows the error and keeps the original value rather than
        # dropping the field.
        out = import_audible.convert_item({"rating": "unrated"})
        assert out["rating"] == "unrated"

    def test_already_numeric_values_pass_through(self):
        out = import_audible.convert_item({"rating": 4.5, "num_ratings": 42})
        assert out["rating"] == 4.5
        assert out["num_ratings"] == 42


class TestAsinHandling:
    def test_asin_is_quoted_str_subclass(self):
        out = import_audible.convert_item({"asin": "B01234"})
        assert isinstance(out["asin"], import_audible.QuotedStr)

    def test_numeric_asin_is_stringified(self):
        out = import_audible.convert_item({"asin": 1234567})
        assert out["asin"] == "1234567"
        assert isinstance(out["asin"], str)

    def test_leading_zeros_survive_a_yaml_round_trip(self):
        # This is the whole point of QuotedStr: an unquoted 0123456789 would come
        # back as an int and lose the leading zero.
        out = import_audible.convert_item({"asin": "0123456789"})
        dumped = yaml.dump({"items": [out]}, default_flow_style=False, sort_keys=False)
        assert '"0123456789"' in dumped
        reloaded = yaml.safe_load(dumped)["items"][0]["asin"]
        assert reloaded == "0123456789"


class TestFieldFiltering:
    def test_unknown_fields_are_dropped(self):
        out = import_audible.convert_item({"title": "T", "unwanted": "x"})
        assert "unwanted" not in out
        assert out["title"] == "T"

    def test_none_values_are_omitted(self):
        out = import_audible.convert_item({"title": "T", "subtitle": None})
        assert "subtitle" not in out

    def test_empty_series_fields_are_omitted(self):
        out = import_audible.convert_item(
            {"title": "T", "series_title": "", "series_sequence": "   "}
        )
        assert "series_title" not in out
        assert "series_sequence" not in out

    def test_populated_series_fields_are_kept(self):
        out = import_audible.convert_item(
            {"title": "T", "series_title": "Foundation", "series_sequence": "2"}
        )
        assert out["series_title"] == "Foundation"
        assert out["series_sequence"] == "2"

    def test_empty_item_yields_empty_output(self):
        # See note in test_csv_to_yaml: `== {}` is the stronger assertion here.
        # pylint: disable=use-implicit-booleaness-not-comparison
        assert import_audible.convert_item({}) == {}

    def test_field_order_follows_keep_fields(self):
        # Output order is stable regardless of input order, which keeps the
        # generated YAML diffable across runs.
        out = import_audible.convert_item({"rating": 5, "asin": "B1", "title": "T"})
        assert list(out) == ["asin", "title", "rating"]
