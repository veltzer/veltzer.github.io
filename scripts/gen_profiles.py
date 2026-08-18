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
    if not data.get("groups"):
        die(f"{SOURCE} has no 'groups' key")
    return data


def render(data, lang):
    """Render the whole shared block as markdown for one language.

    Contact line, intro, the link list, then the trailing extras -- the same
    order the GitHub profile README uses, from the same source, so the two
    pages show the same thing. Everything here is translated: the site serves
    /he/about/ as a real Hebrew page, not an English one under a Hebrew title.
    """
    lines = []

    contact = data.get("contact")
    if contact:
        badge = f"![{contact['badge_alt']}]({contact['badge_url']})"
        lines.append("")
        lines.append(f"{contact[f'text_{lang}']} [{badge}]({contact['url']})")

    intro = data.get("intro")
    if intro:
        lines.append("")
        lines.append(intro[f"text_{lang}"])

    for group in data["groups"]:
        items = group["items"]
        if not items:
            continue
        lines.append("")
        lines.append(f"### {group[f'title_{lang}']}")
        lines.append("")
        for item in items:
            lines.append(f"* [{item['name']}]({item['url']})")
            for child in item.get("children", []):
                # Two spaces, matching gen_readme.py: MD007 wants indent depth
                # 1 at two spaces, and this content is linted as markdown.
                lines.append(f"  * [{child['name']}]({child['url']})")

    for extra in data.get("extras", []):
        lines.append("")
        lines.append(render_extra(extra, lang))

    lines.append("")
    return "\n".join(lines)


def render_extra(extra, lang):
    """Render one trailing extra: a sentence with a link, or a linked badge."""
    if "badge_url" in extra:
        badge = f"![{extra['badge_alt']}]({extra['badge_url']})"
        # The view counter is a bare badge with no link to wrap it.
        body = f"[{badge}]({extra['url']})" if "url" in extra else badge
        return f"### {body}" if extra.get("heading") else body
    link = f"[{extra[f'link_text_{lang}']}]({extra['url']})"
    return f"{extra[f'text_{lang}']} {link}"


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
    data = load_profiles()
    splice(ABOUT_EN, render(data, "en"))
    splice(ABOUT_HE, render(data, "he"))


if __name__ == "__main__":
    main()
