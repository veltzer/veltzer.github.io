"""
Shared helpers of the podcast and YAML maintenance scripts: RSS parsing, the
RSS field setters, episode matching and the ruamel configuration.

Import-only; the scripts that use it live beside it in scripts/.
"""

import io
import math
import re
import xml.etree.ElementTree as ET

import requests
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"

# (field, truncate): the metadata copied from an RSS episode onto a chapter.
RSS_TEXT_FIELDS = [
    ("description", True), ("pubDate", False), ("episodeType", False),
    ("explicit", False), ("enclosure_url", False), ("image", False),
    ("author", False), ("guid", False),
]

# Errors a per-podcast fetch/parse can raise; callers catch these, report and go on.
FEED_ERRORS = (requests.exceptions.RequestException, ET.ParseError, ValueError)


def make_yaml():
    """
    Return a ruamel round-trip YAML configured for the files under data/yaml/
    (two-space maps, sequences indented four with the dash at two, quotes kept,
    no line folding). Loading and dumping with no edit changes only the long
    quoted scalars the files' formatter had wrapped by hand.
    """
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    return yaml


def dump_to_string(yaml, data):
    """Dump `data` with `yaml` to a string."""
    out = io.StringIO()
    yaml.dump(data, out)
    return out.getvalue()


def save_yaml(yaml, data, file_path):
    """Write `data` to `file_path`."""
    with open(file_path, "w", encoding="UTF8") as f:
        yaml.dump(data, f)


def duration_to_seconds(val):
    """
    Convert an iTunes duration (SS, MM:SS or HH:MM:SS, any part may carry a
    fraction: "3600.0", "1:02:03.5") to integer seconds. Raises ValueError on
    anything else.
    """
    s = str(val).strip()
    if not s:
        raise ValueError("empty duration")
    parts = s.split(":")
    if len(parts) > 3:
        raise ValueError(f"bad duration {val!r}")
    total = 0.0
    for p in parts:
        total = total * 60 + float(p)
    if not math.isfinite(total) or total < 0:
        raise ValueError(f"bad duration {val!r}")
    return int(total)


def _text(item, tag):
    el = item.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def parse_rss_episodes(rss_url):
    """
    Fetch and parse all episodes from an RSS feed.
    Returns a list of dicts in chronological order (oldest first).
    An item with an unparseable duration keeps the rest of its data.
    """
    resp = requests.get(rss_url, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    episodes = []
    for item in root.findall(".//item"):
        ep = {
            "title": _text(item, "title"),
            "description": _text(item, "description"),
            "pubDate": _text(item, "pubDate"),
            "episodeType": _text(item, f"{{{ITUNES_NS}}}episodeType"),
            "explicit": _text(item, f"{{{ITUNES_NS}}}explicit"),
            "author": _text(item, f"{{{ITUNES_NS}}}author"),
            "guid": _text(item, "guid"),
        }
        episode = _text(item, f"{{{ITUNES_NS}}}episode")
        ep["episode"] = int(episode) if episode.isdigit() else None
        try:
            dur = _text(item, f"{{{ITUNES_NS}}}duration")
            ep["duration"] = duration_to_seconds(dur) if dur else None
        except ValueError:
            ep["duration"] = None
        enc_el = item.find("enclosure")
        ep["enclosure_url"] = enc_el.get("url", "") if enc_el is not None else ""
        img_el = item.find(f"{{{ITUNES_NS}}}image")
        ep["image"] = img_el.get("href", "") if img_el is not None else ""
        episodes.append(ep)
    episodes.reverse()
    return episodes


def set_rss_fields(target, ep, only_missing=False):
    """
    Set the RSS metadata fields of episode `ep` on the dict `target`.
    With only_missing, keys `target` already has are left alone.
    Returns True when `target` changed.
    """
    changed = False
    for field, truncate in RSS_TEXT_FIELDS:
        if ep[field] and (not only_missing or field not in target):
            target[field] = DQ(ep[field][:200] if truncate else ep[field])
            changed = True
    for field in ("episode", "duration"):
        if ep[field] is not None and (not only_missing or field not in target):
            target[field] = ep[field]
            changed = True
    return changed


def normalise_title(title):
    """Casefold a title and collapse punctuation/whitespace for comparing."""
    return re.sub(r"[\W_]+", " ", str(title).casefold()).strip()


def is_numeric_title(title):
    """True for an absent title or a bare number such as "12"."""
    s = str(title).strip()
    return not s or s.isdigit()


def match_episode(chapter, position, episodes):
    """
    Find the feed episode (episodes is oldest first) a chapter belongs to.
    Order: the chapter's guid, then its normalised title, then - only when the
    title is absent or a bare number - its 0-based position in the chapter
    list, which is how podcasts_add_chapters.py appends them (chapter i is
    episodes[i]). Returns None when nothing matches.
    """
    guid = str(chapter.get("guid", ""))
    if guid:
        for ep in episodes:
            if ep["guid"] == guid:
                return ep
    title = str(chapter.get("title", chapter.get("name", "")))
    if not is_numeric_title(title):
        norm = normalise_title(title)
        for ep in episodes:
            if normalise_title(ep["title"]) == norm:
                return ep
        return None
    if 0 <= position < len(episodes):
        return episodes[position]
    return None
