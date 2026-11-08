#!/usr/bin/env python

"""Import the certifications tab from data/yaml/certifications.yaml.

certifications.yaml lists the certifications I hold; each names the
organization that issued it by its id in organizations.yaml. The tab is the
Certifications tab of the education page (/training/education/): one card per
certification, not per company, so a company that certified me twice has two
cards. A card wants the certification's own fields (name, kind, date, remark)
and, from the issuer, its name, logo, website and status, so the join is done
here and the app needs only the one file.

The importer fails when a certification points at an id that is not in
organizations.yaml, or at an organization whose functions do not include
certification: organizations.yaml says who certified me, certifications.yaml
says for what, and the two must agree.

Like import_companies.py this is a build step: ``build_site.py companies``
runs it and writes the gzipped JSON into the output directory.
"""

import argparse
import sys

import yaml
from import_companies import CERTIFICATION, has_function, write_json_gz

# The certification's own fields, copied when present.
KEPT = ("name", "kind", "date", "remark")
# The issuer's fields, copied when present, under issuer_<field> except logo.
ISSUER_KEPT = ("name", "slug", "website", "status")


def organizations_by_id(organizations):
    """The organizations of organizations.yaml keyed by their id."""
    return {item["id"]: item for item in organizations.get("items") or []}


def problems(certifications, organizations):
    """The certifications whose issuer is unknown or not a certifier, as messages."""
    by_id = organizations_by_id(organizations)
    out = []
    for item in certifications.get("items") or []:
        issuer = by_id.get(item.get("organization"))
        if issuer is None:
            out.append(f"{item.get('name', '?')}: organization {item.get('organization')} is not in organizations.yaml")
        elif not has_function(issuer, CERTIFICATION):
            out.append(f"{item.get('name', '?')}: {issuer.get('name', '?')} does not have the {CERTIFICATION} function")
    return out


def convert_item(item, issuer):
    """One card: the certification's fields and its issuer's."""
    out = {key: item[key] for key in KEPT if item.get(key) not in (None, "")}
    for key in ISSUER_KEPT:
        if issuer.get(key) not in (None, ""):
            out["issuer_" + key] = issuer[key]
    if issuer.get("logo"):
        out["logo"] = issuer["logo"]
    return out


def convert(certifications, organizations):
    """Every certification joined with its issuer, in file order."""
    by_id = organizations_by_id(organizations)
    return {"items": [convert_item(item, by_id[item["organization"]])
                      for item in certifications.get("items") or []]}


def load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("certifications", help="path to data/yaml/certifications.yaml")
    parser.add_argument("organizations", help="path to data/yaml/organizations.yaml")
    parser.add_argument("output", help="path of the .json.gz to write")
    args = parser.parse_args()
    certifications = load(args.certifications)
    organizations = load(args.organizations)
    if not certifications.get("items"):
        print(f"ERROR: {args.certifications} has no items", file=sys.stderr)
        return 1
    found = problems(certifications, organizations)
    if found:
        print(f"ERROR: {args.certifications}:", file=sys.stderr)
        for message in found:
            print(f"  {message}", file=sys.stderr)
        return 1
    converted = convert(certifications, organizations)
    write_json_gz(args.output, converted)
    print(f"Imported {len(converted['items'])} certifications to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
