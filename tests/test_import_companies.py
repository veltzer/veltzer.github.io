"""Tests for import_companies.py, which picks the organizations of one tab.

organizations.yaml carries every organization with research notes, three
geocoded fields and logo provenance; a tab wants the ones with its function
(education) with only their card fields. These pin the selection rule, what is
dropped, the one map point that survives, and what_happened, which the card line is built from.
"""

import gzip
import json

import import_companies


def organization(**overrides):
    base = {
        "id": 2,
        "name": "Amdocs",
        "slug": "amdocs",
        "functions": ["education"],
        "logo": "logos/amdocs.svg",
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
        "address": "Amdocs Building, 8 HaPnina St., Ra'anana, Israel",
        "geo": {"from": "israel_office", "place": "Ra'anana, Israel", "lat": 32.18602, "lon": 34.86784},
        "sources": ["https://en.wikipedia.org/wiki/Amdocs"],
    }
    base.update(overrides)
    return base


class TestSelection:
    def test_organizations_with_the_function_are_kept(self):
        out = import_companies.convert({"items": [organization()]}, "education")
        assert [item["name"] for item in out["items"]] == ["Amdocs"]

    def test_organizations_without_the_function_are_dropped(self):
        out = import_companies.convert({"items": [organization(functions=["consulting"])]}, "education")
        assert out["items"] == []

    def test_missing_functions_means_no_tab(self):
        assert not import_companies.has_function(organization(functions=None), "education")
        assert not import_companies.shown({"name": "x"})

    def test_a_shown_organization_without_an_address_is_reported(self):
        data = {"items": [organization(), organization(id=3, name="Nowhere", address=None),
                          organization(id=4, name="Publisher", functions=[], address=None)]}
        assert import_companies.without_address(data) == ["Nowhere"]

    def test_education_tab(self):
        data = {"items": [organization(functions=["consulting"]), organization(id=4, name="Rimon", functions=["education"])]}
        assert [item["name"] for item in import_companies.convert(data, "education")["items"]] == ["Rimon"]

    def test_every_tab_function_is_shown(self):
        assert import_companies.shown(organization(functions=["education"]))
        assert not import_companies.shown(organization(functions=[]))
        # the consulting, the training companies, the clients I taught at and the companies that
        # certified me went to My World (myworld.stream): they have no tab
        assert not import_companies.shown(organization(functions=["consulting"]))
        assert not import_companies.shown(organization(functions=["teaching"]))
        assert not import_companies.shown(organization(functions=["certification"]))
        assert not import_companies.shown(organization(functions=["training-provider"]))


class TestFields:
    def test_card_fields_survive(self):
        out = import_companies.convert_item(organization())
        assert out["name"] == "Amdocs"
        assert out["logo"] == "logos/amdocs.svg"
        assert out["functions"] == ["education"]
        assert out["status"] == "active"
        assert out["website"] == "https://www.amdocs.com"
        assert out["israel_office"].startswith("Ra'anana")
        assert out["logo_license"].startswith("PD-textlogo")

    def test_research_and_provenance_fields_are_dropped(self):
        out = import_companies.convert_item(organization())
        for key in ("id", "sources", "old_url", "logo_note", "location_geo", "israel_office_geo"):
            assert key not in out

    def test_only_the_chosen_geo_point_survives_without_its_from(self):
        out = import_companies.convert_item(organization())
        assert out["geo"] == {"place": "Ra'anana, Israel", "lat": 32.18602, "lon": 34.86784}

    def test_map_image_is_named_after_the_point(self):
        out = import_companies.convert_item(organization())
        assert out["map"] == "images/map-32.18602_34.86784.jpg"
        assert import_companies.map_path({"lat": 42.35883, "lon": -71.05783}) == "images/map-42.35883_-71.05783.jpg"

    def test_incomplete_geo_is_omitted(self):
        out = import_companies.convert_item(organization(geo={"place": "Somewhere"}))
        assert "geo" not in out

    def test_empty_values_are_omitted(self):
        out = import_companies.convert_item(organization(website="", remark=None))
        assert "website" not in out
        assert "remark" not in out


class TestBlurb:
    def test_what_happened_is_kept_for_the_card_line(self):
        item = organization(status="acquired", what_happened="Acquired by Nokia in 2016.")
        out = import_companies.convert_item(item)
        assert out["what_happened"] == "Acquired by Nokia in 2016."
        # The line itself is built in the page's language by plugin-companies.js.
        assert "review" not in out


class TestMissingMaps:
    def test_present_image_is_not_missing(self, tmp_path):
        (tmp_path / "map-32.18602_34.86784.jpg").write_bytes(b"jpeg")
        items = import_companies.convert({"items": [organization()]}, "education")["items"]
        assert import_companies.missing_maps(items, tmp_path) == []

    def test_absent_image_is_reported_once_per_point(self, tmp_path):
        items = import_companies.convert({"items": [organization(), organization(id=3, name="Other")]}, "education")["items"]
        assert import_companies.missing_maps(items, tmp_path) == ["images/map-32.18602_34.86784.jpg"]

    def test_item_without_geo_needs_no_image(self, tmp_path):
        items = import_companies.convert({"items": [organization(geo=None)]}, "education")["items"]
        assert import_companies.missing_maps(items, tmp_path) == []


class TestOutput:
    def test_gzipped_json_is_reproducible(self, tmp_path):
        data = import_companies.convert({"items": [organization()]}, "education")
        first = tmp_path / "a.json.gz"
        second = tmp_path / "b.json.gz"
        import_companies.write_json_gz(first, data)
        import_companies.write_json_gz(second, data)
        assert first.read_bytes() == second.read_bytes()
        with gzip.open(first, "rt", encoding="utf-8") as handle:
            assert json.load(handle) == data


class TestMainFailurePaths:
    """main() must exit 1 with a message, and write nothing, on bad input."""

    def run_main(self, tmp_path, monkeypatch, capsys, data, *extra):
        import sys

        import yaml

        source = tmp_path / "organizations.yaml"
        source.write_text(yaml.safe_dump(data), encoding="utf-8")
        target = tmp_path / "out.json.gz"
        if "--function" not in extra:
            extra = ("--function", "education", *extra)
        monkeypatch.setattr(sys, "argv", ["import_companies.py", str(source), str(target), *extra])
        code = import_companies.main()
        return code, capsys.readouterr().err, target

    def test_no_items_key(self, tmp_path, monkeypatch, capsys):
        code, err, target = self.run_main(tmp_path, monkeypatch, capsys, {"other": 1})
        assert code == 1
        assert "has no items" in err
        assert not target.exists()

    def test_shown_organization_without_address(self, tmp_path, monkeypatch, capsys):
        item = organization()
        del item["address"]
        code, err, target = self.run_main(tmp_path, monkeypatch, capsys, {"items": [item]})
        assert code == 1
        assert "no address" in err
        assert not target.exists()

    def test_no_organization_with_the_function(self, tmp_path, monkeypatch, capsys):
        item = organization(functions=["consulting"])
        code, err, target = self.run_main(tmp_path, monkeypatch, capsys, {"items": [item]}, "--function", "education")
        assert code == 1
        assert "'education'" in err
        assert not target.exists()

    def test_missing_map_image_fails_when_images_dir_given(self, tmp_path, monkeypatch, capsys):
        images = tmp_path / "images"
        images.mkdir()
        code, err, target = self.run_main(
            tmp_path, monkeypatch, capsys, {"items": [organization()]}, "--images-dir", str(images))
        assert code == 1
        assert "map image(s) missing" in err
        assert not target.exists()

