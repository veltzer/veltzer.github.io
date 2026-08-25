#!/usr/bin/env python

"""
Render the profile links from ../data/yaml/profiles.yaml into both places that
show them, so the two cannot drift apart.

Targets:
  content/about/_index.en.md         this site's About page
  content/about/_index.he.md         its Hebrew translation
  static/identity.toml               sameAs URLs for the Person JSON-LD

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
IDENTITY = REPO_ROOT / "static" / "identity.toml"

# Groups whose links are identity profiles -- pages that ARE Mark Veltzer
# somewhere else. Only these belong in schema.org sameAs, which means "another
# official page for this same person". The learning_no_profile group is
# deliberately absent: brilliant.org and audible.com are sites he uses, not
# profiles of him, and claiming them as sameAs would be a false identity claim
# and dilute the signal. The typing group is absent for a milder reason -- the
# keybr children are per-email throwaway profiles, not a public identity.
SAMEAS_GROUPS = ("development", "learning", "trove")

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


def render_identity(data):
    """Emit the sameAs URL list as TOML for base.html's Person JSON-LD.

    Written into static/ rather than being read from the YAML at build time
    for the same reason the About page is generated and committed: CI has no
    ../data checkout, so the template must read something that lives in this
    repo. load_data() picks it up from static/identity.toml.

    Only SAMEAS_GROUPS contribute, and only top-level items -- see the comment
    on that constant. Nested children (the per-email keybr profiles) are skipped.
    """
    urls = []
    for group in data["groups"]:
        if group["id"] not in SAMEAS_GROUPS:
            continue
        for item in group["items"]:
            if item["url"] not in urls:
                urls.append(item["url"])
    if not urls:
        die("no sameAs URLs found -- check SAMEAS_GROUPS against profiles.yaml")

    lines = [
        "# Generated by scripts/gen_profiles.py from ../data/yaml/profiles.yaml.",
        "# Do not hand-edit -- edit the YAML and re-run the script.",
        "#",
        "# Read by templates/base.html into the Person JSON-LD as schema.org",
        "# sameAs: the canonical list of other pages that are the same person.",
        "# This is what tells a search engine that veltzer.org, the GitHub",
        "# account and the rest are one identity, which is the whole point of",
        "# the markup for a name query.",
        "",
        "sameas = [",
    ]
    lines.extend(f'    "{url}",' for url in urls)
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def write_identity(path, body):
    """Write path only when the content actually changes, like splice() does."""
    if path.is_file() and path.read_text(encoding="utf-8") == body:
        print(f"unchanged {path}")
        return
    path.write_text(body, encoding="utf-8")
    print(f"wrote {path}")


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
    write_identity(IDENTITY, render_identity(data))


if __name__ == "__main__":
    main()
