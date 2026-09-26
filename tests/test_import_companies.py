"""Tests for import_companies.py, which picks the taught-at organizations.

organizations.yaml carries every organization with research notes, three
geocoded fields and logo provenance; the companies tab wants the teaching
ones with only their card fields. These pin the selection rule, what is
dropped, the one map point that survives, and the blurb the card prints.
"""

import gzip
import json

import import_companies


def organization(**overrides):
    base = {
        "id": 2,
        "name": "Amdocs",
        "slug": "amdocs",
        "functions": ["teaching", "consulting"],
        "logo": "logos/amdocs.svg",
        "logo_original": "raw/logos/amdocs.gif",
        "logo_kind": "official vector",
        "logo_source": "https://upload.wikimedia.org/wikipedia/commons/1/18/Amdocs_Logo.svg",
        "logo_license": "PD-textlogo (public domain, trademark applies)",
        "logo_note": "current lowercase wordmark",
        "old_url": "http://www.amdocs.com",
        "status": "active",
        "website": "https://www.amdocs.com",
        "location": "Chesterfield, Missouri, USA (registered in Guernsey)",
        "location_geo": {"place": "Chesterfield, Missouri, USA", "lat": 38.65818, "lon": -90.56806},
        "israel_office": "Ra'anana, Israel (main R&D centre and largest site)",
        "israel_office_geo": {"place": "Ra'anana, Israel", "lat": 32.18602, "lon": 34.86784},
        "geo": {"from": "israel_office", "place": "Ra'anana, Israel", "lat": 32.18602, "lon": 34.86784},
        "sources": ["https://en.wikipedia.org/wiki/Amdocs"],
    }
    base.update(overrides)
    return base


class TestSelection:
    def test_teaching_organizations_are_kept(self):
        out = import_companies.convert({"items": [organization()]})
        assert [item["name"] for item in out["items"]] == ["Amdocs"]

    def test_consulting_only_organizations_are_dropped(self):
        out = import_companies.convert({"items": [organization(functions=["consulting"])]})
        assert out["items"] == []

    def test_missing_functions_means_not_taught(self):
        assert not import_companies.taught_at(organization(functions=None))
        assert not import_companies.taught_at({"name": "x"})


class TestFields:
    def test_card_fields_survive(self):
        out = import_companies.convert_item(organization())
        assert out["name"] == "Amdocs"
        assert out["logo"] == "logos/amdocs.svg"
        assert out["functions"] == ["teaching", "consulting"]
        assert out["status"] == "active"
        assert out["website"] == "https://www.amdocs.com"
        assert out["israel_office"].startswith("Ra'anana")
        assert out["logo_license"].startswith("PD-textlogo")

    def test_research_and_provenance_fields_are_dropped(self):
        out = import_companies.convert_item(organization())
        for key in ("id", "sources", "old_url", "logo_original", "logo_note", "location_geo", "israel_office_geo"):
            assert key not in out

    def test_only_the_chosen_geo_point_survives_without_its_from(self):
        out = import_companies.convert_item(organization())
        assert out["geo"] == {"place": "Ra'anana, Israel", "lat": 32.18602, "lon": 34.86784}

    def test_incomplete_geo_is_omitted(self):
        out = import_companies.convert_item(organization(geo={"place": "Somewhere"}))
        assert "geo" not in out

    def test_empty_values_are_omitted(self):
        out = import_companies.convert_item(organization(website="", remark=None))
        assert "website" not in out
        assert "remark" not in out


class TestBlurb:
    def test_what_happened_is_the_blurb(self):
        item = organization(status="acquired", what_happened="Acquired by Nokia in 2016.")
        assert import_companies.convert_item(item)["review"] == "Acquired by Nokia in 2016."
        assert "what_happened" not in import_companies.convert_item(item)

    def test_active_company_says_so(self):
        assert import_companies.blurb(organization(status="active")) == "Still active."

    def test_other_status_without_a_story_is_capitalized(self):
        assert import_companies.blurb(organization(status="defunct")) == "Defunct."


class TestOutput:
    def test_gzipped_json_is_reproducible(self, tmp_path):
        data = import_companies.convert({"items": [organization()]})
        first = tmp_path / "a.json.gz"
        second = tmp_path / "b.json.gz"
        import_companies.write_json_gz(first, data)
        import_companies.write_json_gz(second, data)
        assert first.read_bytes() == second.read_bytes()
        with gzip.open(first, "rt", encoding="utf-8") as handle:
            assert json.load(handle) == data
