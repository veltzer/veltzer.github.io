#!/usr/bin/env python

"""
Render the profile links from ../data/yaml/profiles.yaml into both places that
show them, so the two cannot drift apart.

Targets:
  content/about/_index.en.md         this site's About page
  content/about/_index.he.md         its Hebrew translation

The same profiles.yaml also drives README.md in the ../veltzer repository, the
GitHub profile page. That repo builds its own copy with its own rsconstruct
setup -- this script does not write there. Each repository owns its artifact,
and the shared YAML is the only thing that crosses between them.

Only the link list is generated. Everything outside the marker comments is left
exactly as it was, so the hand-written prose above them survives regeneration.

Run it by hand after editing profiles.yaml. Like copy_data.py this is
deliberately not part of the build: the sibling data repo is not checked out in
CI, and the generated content is committed.
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_REPO = REPO_ROOT.parent / "data"

SOURCE = DATA_REPO / "yaml" / "profiles.yaml"
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


def render(groups, lang):
    """Render the link list as markdown for one language.

    Every entry is rendered, children included, so this page and the GitHub
    profile README show the same links from the same source.
    """
    title_key = f"title_{lang}"
    lines = []
    for group in groups:
        items = group["items"]
        if not items:
            continue
        lines.append("")
        lines.append(f"### {group[title_key]}")
        lines.append("")
        for item in items:
            lines.append(f"* [{item['name']}]({item['url']})")
            for child in item.get("children", []):
                # Two spaces, matching gen_readme.py: MD007 wants indent depth
                # 1 at two spaces, and this content is linted as markdown.
                lines.append(f"  * [{child['name']}]({child['url']})")
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
    splice(ABOUT_EN, render(groups, "en"))
    splice(ABOUT_HE, render(groups, "he"))


if __name__ == "__main__":
    main()
