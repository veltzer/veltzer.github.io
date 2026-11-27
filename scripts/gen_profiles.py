#!/usr/bin/env python

"""
Render the shared profile block from data/profiles.yaml into every
place on this site that shows it, so the copies cannot drift apart.

Targets:
  content/about/_index.en.md         this site's About page
  content/about/_index.he.md         its Hebrew translation
  content/about/_index.ru.md         its Russian translation
  data/identity.toml               sameAs URLs for the Person JSON-LD

The same profiles.yaml also drives README.md in the ../veltzer repository, the
GitHub profile page. That repo builds its own copy with its own rsconstruct
setup -- this script does not write there. Each repository owns its artifact,
and the shared YAML is the only thing that crosses between them.

The whole block between the marker comments is generated: the contact line,
the intro, the link groups and the trailing extras. Everything outside the
markers is left exactly as it was, so the hand-written prose above them
survives regeneration.

Run it after editing profiles.yaml and commit what it writes. With --check
it writes nothing and exits non-zero when a target no longer matches what
the YAML renders to; the build runs it that way (the `profiles` processor in
rsconstruct.toml), so a YAML edit without a regeneration, or a hand edit
inside a generated block, fails the build. The fix is to run it without
--check.
"""

import argparse
import html
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

SOURCE = REPO_ROOT / "data" / "profiles.yaml"
ABOUT_EN = REPO_ROOT / "content" / "about" / "_index.en.md"
ABOUT_HE = REPO_ROOT / "content" / "about" / "_index.he.md"
ABOUT_RU = REPO_ROOT / "content" / "about" / "_index.ru.md"
IDENTITY = REPO_ROOT / "data" / "identity.toml"

# Groups whose links are identity profiles -- pages that ARE Mark Veltzer
# somewhere else. Only these belong in schema.org sameAs, which means "another
# official page for this same person". The learning_no_profile group is
# deliberately absent: brilliant.org and audible.com are sites he uses, not
# profiles of him, and claiming them as sameAs would be a false identity claim
# and dilute the signal. The typing group is absent for a milder reason -- the
# keybr children are per-email throwaway profiles, not a public identity.
SAMEAS_GROUPS = ("development", "learning", "trove")
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")

# Everything between these two lines is replaced; everything outside is kept.
# They are HTML comments so they stay invisible in rendered markdown on both
# GitHub and the site.
BEGIN = "<!-- BEGIN generated profiles -- edit data/profiles.yaml -->"
END = "<!-- END generated profiles -->"
# An existing block is found by this prefix, not by the full BEGIN line, so
# rewording the hint in BEGIN rewrites the old block instead of appending a
# second one next to it.
BEGIN_PREFIX = "<!-- BEGIN generated profiles"


def die(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_profiles(source: Path):
    if not source.is_file():
        die(f"Missing source file {source}.")
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not data.get("groups"):
        die(f"{source} has no 'groups' key")
    return data


def render(data: dict[str, Any], lang: str) -> str:
    """Render the whole shared block as markdown for one language.

    Contact line, intro, the link list, then the trailing extras -- the same
    order the GitHub profile README uses, from the same source, so the two
    pages show the same thing. Everything here is translated: the site serves
    /he/about/ and /ru/about/ as real translated pages, not English ones under
    a translated title.
    """
    lines = []

    contact = data.get("contact")
    if contact:
        lines.append("")
        lines.append(f"{contact[f'text_{lang}']} [{contact['link_text']}]({contact['url']})")

    intro = data.get("intro")
    if intro:
        lines.append("")
        lines.append(intro[f"text_{lang}"])

    for group in data["groups"]:
        items = group["items"]
        if not items:
            continue
        lines.append("")
        # Level 2: the page's H1 is the front-matter title, so MD001 wants the
        # first body heading one level down. gen_readme.py in ../veltzer uses
        # level 3 under its own level-3 page heading.
        lines.append(f"## {group[f'title_{lang}']}")
        lines.append("")
        for item in items:
            lines.append(f"* [{item['name']}]({item['url']})")
            # Four spaces: this content is linted with .rumdl.content.toml,
            # whose MD007 indent is 4 (gen_readme.py's README is linted
            # under that repo's own config, which wants 2).
            lines.extend(f"    * [{child['name']}]({child['url']})" for child in item.get("children", []))

    for extra in data.get("extras", []):
        lines.append("")
        lines.append(render_extra(extra, lang))

    lines.append("")
    return "\n".join(lines)


def render_badge(extra: dict[str, str]) -> str:
    """A badge image served by somebody else's server.

    With `badge_width` / `badge_height` in the YAML it is an <img> that
    reserves its space and loads lazily, so a slow badge service neither
    holds the page up nor shifts it when the picture arrives. Markdown image
    syntax can say neither, which is why this is HTML. (The GitHub profile
    README, rendered from the same YAML by ../veltzer, keeps the Markdown
    form: GitHub proxies and sizes images itself.)
    """
    size = "".join(
        f' {attr}="{extra[key]}"'
        for attr, key in (("width", "badge_width"), ("height", "badge_height"))
        if key in extra
    )
    if not size:
        return f"![{extra['badge_alt']}]({extra['badge_url']})"
    alt = html.escape(extra["badge_alt"], quote=True)
    url = html.escape(extra["badge_url"], quote=True)
    return f'<img src="{url}" alt="{alt}"{size} loading="lazy" decoding="async">'


def render_extra(extra: dict[str, str], lang: str) -> str:
    """Render one trailing extra: a sentence with a link, or a linked badge."""
    if "badge_url" in extra:
        badge = render_badge(extra)
        # The view counter is a bare badge with no link to wrap it.
        body = f"[{badge}]({extra['url']})" if "url" in extra else badge
        return f"### {body}" if extra.get("heading") else body
    link = f"[{extra[f'link_text_{lang}']}]({extra['url']})"
    return f"{extra[f'text_{lang}']} {link}"


def render_identity(data: dict[str, Any]) -> str:
    """Emit the sameAs URL list as TOML for base.html's Person JSON-LD.

    Committed rather than read from the YAML at build time for the same reason
    the About page is: the rendering is done here, and the build only checks
    it (--check). templates/person_jsonld.html picks it up with load_data().

    Only SAMEAS_GROUPS contribute, and only top-level items -- see the comment
    on that constant. Nested children (the per-email keybr profiles) are skipped,
    and so is a link to an image (the Project Euler badge, the only public
    thing that site offers): sameAs names pages about the person, and a
    picture is not one.
    """
    urls = []
    for group in data["groups"]:
        if group["id"] not in SAMEAS_GROUPS:
            continue
        for item in group["items"]:
            if item["url"].lower().endswith(IMAGE_SUFFIXES):
                continue
            if item["url"] not in urls:
                urls.append(item["url"])
    if not urls:
        die("no sameAs URLs found -- check SAMEAS_GROUPS against profiles.yaml")

    lines = [
        "# Generated by scripts/gen_profiles.py from data/profiles.yaml.",
        "# Do not hand-edit -- edit the YAML and re-run the script.",
        "#",
        "# Read by templates/person_jsonld.html into the Person JSON-LD as schema.org",
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


def spliced(path: Path, body: str):
    """Return path's text with the marked block replaced by body, or appended."""
    if not path.is_file():
        die(f"Missing target file {path}")
    text = path.read_text(encoding="utf-8")
    block = f"{BEGIN}\n{body}\n{END}\n"

    count = text.count(BEGIN_PREFIX)
    if count > 1:
        die(f"{path} has {count} generated profile blocks; remove all but one")
    if count == 1:
        if END not in text:
            die(f"{path} has a {BEGIN_PREFIX} marker but no closing {END}")
        head, rest = text.split(BEGIN_PREFIX, 1)
        _, tail = rest.split(END, 1)
        # Re-separate the block from whatever follows. tail starts with the
        # newline that ended the END line, and block already supplies it, so
        # stripping and re-adding keeps exactly one blank line rather than
        # gluing the next paragraph onto the marker.
        tail = tail.lstrip("\n")
        return head + block + (f"\n{tail}" if tail else "")
    return text.rstrip("\n") + "\n\n" + block


def targets(data: dict[str, Any]):
    """Every generated file with the full text it should have."""
    return [
        (ABOUT_EN, spliced(ABOUT_EN, render(data, "en"))),
        (ABOUT_HE, spliced(ABOUT_HE, render(data, "he"))),
        (ABOUT_RU, spliced(ABOUT_RU, render(data, "ru"))),
        (IDENTITY, render_identity(data)),
    ]


def current(path: Path):
    return path.read_text(encoding="utf-8") if path.is_file() else None


def write(pairs: list[tuple[Path, str]]) -> None:
    """Write each target whose content changes; leave the others untouched."""
    for path, text in pairs:
        if current(path) == text:
            print(f"unchanged {path}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


def check(pairs: list[tuple[Path, str]]):
    """Return the targets that differ from what the YAML renders to."""
    return [path for path, text in pairs if current(path) != text]


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Render data/profiles.yaml into the About pages and data/identity.toml")
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if a generated file is out of date",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=SOURCE,
        help=f"the profiles YAML (default: {SOURCE.relative_to(REPO_ROOT)})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs = targets(load_profiles(args.source))
    if not args.check:
        write(pairs)
        return
    stale = check(pairs)
    for path in stale:
        print(f"{path.relative_to(REPO_ROOT)} does not match {args.source}", file=sys.stderr)
    if stale:
        die("generated profile files are out of date; run scripts/gen_profiles.py and commit the result")


if __name__ == "__main__":
    main()
