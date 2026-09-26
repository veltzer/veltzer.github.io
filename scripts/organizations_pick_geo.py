#!/usr/bin/env python
"""
Pick the one map point per organization in data/yaml/organizations.yaml.

``organizations_geocode.py`` gives an organization up to three points
(``location_geo``, ``israel_office_geo``, ``former_location_geo``). A map
that wants a single marker per organization needs one of them chosen, and
that is a judgement call (where did I actually deal with them?), so this
script asks. The answer is written as a ``geo`` block just before the
item's ``sources``::

    geo:
      from: israel_office
      place: Ra'anana, Israel
      lat: 32.18602
      lon: 34.86784

``from`` names the field the point was taken from, so a later re-geocode
can be re-applied and the choice stays legible.

Organizations whose ``_geo`` blocks all sit on the same spot (an Israeli
company whose HQ is its Israel office) are decided without asking; only
those with more than one distinct spot prompt. The prompt shows every
distinct spot with the field(s) that carry it and the original prose, with
the suggested answer first: the Israel office if there is one, else the
current location, else the former one. Enter takes the suggestion, a number
picks, ``s`` skips the organization for now, ``q`` stops. The file is
rewritten after every answer, so quitting or Ctrl-C loses nothing and the
next run continues from the first undecided organization. An existing
``geo`` block is kept unless ``--force`` asks to choose again; ``--auto``
takes the suggestion everywhere without prompting.

Run from the repo root:

    scripts/organizations_pick_geo.py            # decide what is undecided
    scripts/organizations_pick_geo.py --force    # choose everything again
    scripts/organizations_pick_geo.py --auto     # suggestions only, no prompt
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

YAML_PATH = Path("data/yaml/organizations.yaml")
# Preference order for the suggestion: where I dealt with them, then where they are, then where they were.
PLACE_FIELDS = ("israel_office", "location", "former_location")
ANCHOR = "sources"  # every item ends with its sources; geo goes right before that key

ITEM_RE = re.compile(r"^- id: (\d+)\s*$")
KEY_RE = re.compile(r"^  ([a-z_]+):")


class Candidate:
    """One distinct spot of an organization and the fields that share it."""

    def __init__(self, field: str, geo: dict[str, Any]) -> None:
        self.fields = [field]
        self.place: str = geo["place"]
        self.lat: float = geo["lat"]
        self.lon: float = geo["lon"]

    @property
    def key(self) -> tuple[float, float]:
        return (self.lat, self.lon)


def candidates(item: dict[str, Any]) -> list[Candidate]:
    """The organization's distinct spots, in suggestion order (first is the suggestion)."""
    out: list[Candidate] = []
    for field in PLACE_FIELDS:
        geo = item.get(f"{field}_geo")
        if geo is None:
            continue
        for c in out:
            if c.key == (geo["lat"], geo["lon"]):
                c.fields.append(field)
                break
        else:
            out.append(Candidate(field, geo))
    return out


def geo_lines(choice: Candidate) -> list[str]:
    place = yaml.safe_dump(choice.place, allow_unicode=True, width=10000).strip().removesuffix("...").strip()
    return [
        "  geo:\n",
        f"    from: {choice.fields[0]}\n",
        f"    place: {place}\n",
        f"    lat: {choice.lat}\n",
        f"    lon: {choice.lon}\n",
    ]


def splice(lines: list[str], item_id: int, block: list[str]) -> list[str]:
    """Return ``lines`` with ``block`` as the ``geo`` of item ``item_id`` (replacing an existing one)."""
    out: list[str] = []
    current = 0
    skipping = False
    for line in lines:
        m_item = ITEM_RE.match(line)
        m_key = KEY_RE.match(line)
        if m_item or m_key or not line.startswith(" "):
            skipping = False
        if m_item:
            current = int(m_item.group(1))
        elif m_key and current == item_id:
            if m_key.group(1) == "geo":
                skipping = True
            elif m_key.group(1) == ANCHOR:
                out.extend(block)
        if not skipping:
            out.append(line)
    return out


def describe(item: dict[str, Any], cands: list[Candidate]) -> None:
    print()
    print(f"[{item['id']}] {item['name']}  ({item['status']}; {', '.join(item['functions'])})")
    if item.get("remark"):
        print(f"      remark: {item['remark']}")
    for n, c in enumerate(cands, 1):
        tag = "suggested" if n == 1 else ""
        print(f"  {n}) {c.place:32} {c.lat:9.5f} {c.lon:10.5f}  <- {'/'.join(c.fields)}  {tag}")
        for field in c.fields:
            print(f"        {field}: {item[field]}")


def ask(cands: list[Candidate]) -> Candidate | None | str:
    """A candidate, None to skip, or "quit"."""
    while True:
        try:
            answer = input(f"  pick [1-{len(cands)}] (Enter=1, s=skip, q=quit): ").strip().lower()
        except EOFError:
            print()
            return "quit"
        if answer == "":
            return cands[0]
        if answer == "s":
            return None
        if answer == "q":
            return "quit"
        if answer.isdigit() and 1 <= int(answer) <= len(cands):
            return cands[int(answer) - 1]
        print("  ? not an option")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="choose again where a geo block already exists")
    parser.add_argument("--auto", action="store_true", help="take the suggestion everywhere, never prompt")
    parser.add_argument("--yaml", type=Path, default=YAML_PATH, help=f"the file to edit (default {YAML_PATH})")
    args = parser.parse_args()

    text = args.yaml.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    data = yaml.safe_load(text)

    decided = asked = skipped = 0
    for item in data["items"]:
        if "geo" in item and not args.force:
            continue
        cands = candidates(item)
        if not cands:
            print(f"[{item['id']}] {item['name']}: no _geo at all, nothing to pick")
            continue
        if len(cands) == 1 or args.auto:
            choice: Candidate | None | str = cands[0]
        else:
            describe(item, cands)
            choice = ask(cands)
            asked += 1
        if choice == "quit":
            break
        if choice is None:
            skipped += 1
            continue
        assert isinstance(choice, Candidate)
        lines = splice(lines, item["id"], geo_lines(choice))
        args.yaml.write_text("".join(lines), encoding="utf-8")
        decided += 1

    undecided = sum(1 for item in yaml.safe_load(args.yaml.read_text(encoding="utf-8"))["items"] if "geo" not in item)
    print(f"\n{decided} decided ({asked} by prompt), {skipped} skipped this run; {undecided} organizations still without geo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
