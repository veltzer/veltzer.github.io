#!/usr/bin/env python

"""
Render the profile links from ../data/yaml/profiles.yaml into both places that
show them, so the two cannot drift apart.

Targets:
  ../veltzer/README.md               the GitHub profile page
  content/about/_index.en.md         this site's About page
  content/about/_index.he.md         its Hebrew translation

Direction matters. ../veltzer is the GitHub profile repository, which GitHub
renders straight from that repo's default branch -- it cannot be a build
artifact of this site, so it is a target here rather than the source, and the
source is a third file both sides read.

Only the link list is generated. Everything outside the marker comments in each
target is left exactly as it was, so the hand-written prose on the About page
and the badges and view counter on the GitHub profile survive regeneration.

Run it by hand after editing profiles.yaml, then commit both repos. Like
copy_data.py this is deliberately not part of the build: the sibling data repo
is not checked out in CI, and the generated content is committed.
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_REPO = REPO_ROOT.parent / "data"
PROFILE_REPO = REPO_ROOT.parent / "veltzer"

SOURCE = DATA_REPO / "yaml" / "profiles.yaml"
README = PROFILE_REPO / "README.md"
ABOUT_EN = REPO_ROOT / "content" / "about" / "_index.en.md"
ABOUT_HE = REPO_ROOT / "content" / "about" / "_index.he.md"

# Everything between these two lines is replaced; everything outside is kept.
# They are HTML comments so they stay invisible in rendered markdown on both
# GitHub and the site.
BEGIN = "<!-- BEGIN generated profiles -- edit ../data/yaml/profiles.yaml -->"
END = "<!-- END generated profiles -->"


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_profiles():
    if not SOURCE.is_file():
        die(f"Missing source file {SOURCE}. Clone the data repo first.")
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    groups = data.get("groups")
    if not groups:
        die(f"{SOURCE} has no 'groups' key")
    return groups


def render(groups, lang, include_github_only):
    """Render the link list as markdown.

    include_github_only keeps the entries flagged github_only, which belong on
    the GitHub profile but not on the site -- the keybr accounts are five mail
    addresses that earn a reader nothing.
    """
    title_key = f"title_{lang}"
    lines = []
    for group in groups:
        items = [
            item for item in group["items"]
            if include_github_only or not item.get("github_only")
        ]
        if not items:
            continue
        lines.append("")
        lines.append(f"### {group[title_key]}")
        lines.append("")
        for item in items:
            lines.append(f"* [{item['name']}]({item['url']})")
            if include_github_only:
                for child in item.get("children", []):
                    lines.append(f"    * [{child['name']}]({child['url']})")
    lines.append("")
    return "\n".join(lines)


def splice(path, body):
    """Replace the marked block in path, or append one if it is not there yet."""
    if not path.is_file():
        die(f"Missing target file {path}")
    text = path.read_text(encoding="utf-8")
    block = f"{BEGIN}\n{body}\n{END}\n"

    if BEGIN in text:
        if END not in text:
            die(f"{path} has a {BEGIN} marker but no closing {END}")
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        # Re-separate the block from whatever follows. tail starts with the
        # newline that ended the END line, and block already supplies it, so
        # stripping and re-adding keeps exactly one blank line rather than
        # gluing the next paragraph onto the marker.
        tail = tail.lstrip("\n")
        updated = head + block + (f"\n{tail}" if tail else "")
    else:
        updated = text.rstrip("\n") + "\n\n" + block

    if updated == text:
        print(f"unchanged {path}")
        return
    path.write_text(updated, encoding="utf-8")
    print(f"wrote {path}")


def main():
    groups = load_profiles()
    splice(README, render(groups, "en", include_github_only=True))
    splice(ABOUT_EN, render(groups, "en", include_github_only=False))
    splice(ABOUT_HE, render(groups, "he", include_github_only=False))


if __name__ == "__main__":
    main()
