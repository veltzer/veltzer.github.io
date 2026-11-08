"""Tests for import_certifications.py, which joins certifications with their issuers.

certifications.yaml names the issuing organization by its id in
organizations.yaml. These pin the join (one card per certification, the
issuer's fields under issuer_*), and the two errors: an id that does not
exist, and an issuer that is not marked as certifying.
"""

import import_certifications


def organization(**overrides):
    base = {
        "id": 100,
        "name": "Amazon Web Services",
        "slug": "aws",
        "functions": ["certification"],
        "logo": "logos/aws.svg",
        "website": "https://aws.amazon.com/",
        "status": "active",
        "address": "410 Terry Ave N, Seattle",
        "sources": ["https://example.com"],
    }
    base.update(overrides)
    return base


def certification(**overrides):
    base = {"id": 1, "name": "AWS Certified Solutions Architect - Associate", "organization": 100,
            "kind": "professional", "date": "2014-05-15"}
    base.update(overrides)
    return base


class TestConvert:
    def test_one_card_per_certification(self):
        certs = {"items": [certification(), certification(id=2, name="AWS Certified Instructor", kind="instructor")]}
        orgs = {"items": [organization()]}
        names = [item["name"] for item in import_certifications.convert(certs, orgs)["items"]]
        assert names == ["AWS Certified Solutions Architect - Associate", "AWS Certified Instructor"]

    def test_issuer_fields_are_joined(self):
        item = import_certifications.convert({"items": [certification()]}, {"items": [organization()]})["items"][0]
        assert item == {
            "name": "AWS Certified Solutions Architect - Associate",
            "kind": "professional",
            "date": "2014-05-15",
            "issuer_name": "Amazon Web Services",
            "issuer_slug": "aws",
            "issuer_website": "https://aws.amazon.com/",
            "issuer_status": "active",
            "logo": "logos/aws.svg",
        }

    def test_missing_date_and_remark_are_omitted(self):
        cert = certification()
        del cert["date"]
        item = import_certifications.convert({"items": [cert]}, {"items": [organization()]})["items"][0]
        assert "date" not in item
        assert "remark" not in item


class TestProblems:
    def test_unknown_organization_is_reported(self):
        found = import_certifications.problems({"items": [certification(organization=999)]},
                                               {"items": [organization()]})
        assert found == ["AWS Certified Solutions Architect - Associate: organization 999 is not in organizations.yaml"]

    def test_issuer_without_certification_function_is_reported(self):
        found = import_certifications.problems({"items": [certification()]},
                                               {"items": [organization(functions=["teaching"])]})
        assert found == [("AWS Certified Solutions Architect - Associate: Amazon Web Services does not have the"
                          " certification function")]

    def test_consistent_data_has_no_problems(self):
        assert import_certifications.problems({"items": [certification()]}, {"items": [organization()]}) == []
