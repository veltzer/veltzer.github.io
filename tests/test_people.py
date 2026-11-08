"""Checks on data/yaml/people.yaml, the one list of the people I know.

The with: fields of the other data files name people by the same strings.
These pin that people.yaml has each person once, stays sorted, and has an
entry for every name any with: field uses, so a person added to a museum
visit or a concert is also added here (with a description when there is one).
"""

from pathlib import Path

import yaml

YAML_DIR = Path(__file__).resolve().parent.parent / "data" / "yaml"


def load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


PEOPLE = load(YAML_DIR / "people.yaml")["items"]
NAMES = [person["name"] for person in PEOPLE]


def test_no_duplicate_names():
    duplicates = sorted({name for name in NAMES if NAMES.count(name) > 1})
    assert duplicates == []


def test_sorted_by_name():
    assert sorted(NAMES, key=str.lower) == NAMES


def test_every_with_name_is_a_person():
    known = set(NAMES)
    missing = set()
    for path in sorted(YAML_DIR.glob("*.yaml")):
        for item in load(path).get("items") or []:
            if isinstance(item, dict):
                missing.update(f"{path.name}: {name}" for name in item.get("with") or [] if name not in known)
    assert sorted(missing) == []
