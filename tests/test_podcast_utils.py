"""Tests for scripts/podcast_utils.py and the chapter rebuild of podcasts_backfill_rss_data.py."""

import io
from pathlib import Path

import pytest
from podcast_utils import (
    dump_to_string,
    duration_to_seconds,
    make_yaml,
    match_episode,
    set_rss_fields,
)
from podcasts_backfill_rss_data import _rebuild_chapter_from_name
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent
PODCASTS = ROOT / "data" / "yaml" / "podcasts.yaml"
VIDEO_YOUTUBE = ROOT / "data" / "yaml" / "video_youtube.yaml"


@pytest.mark.parametrize(("raw", "expected"), [
    ("90", 90),
    ("3600.0", 3600),
    ("1:02:03", 3723),
    ("1:02:03.5", 3723),
    ("12:34", 754),
    (" 45 ", 45),
    (286, 286),
])
def test_duration_to_seconds(raw, expected):
    assert duration_to_seconds(raw) == expected


@pytest.mark.parametrize("raw", ["", "abc", "1:2:3:4", "nan", "inf", "-5"])
def test_duration_to_seconds_rejects(raw):
    with pytest.raises(ValueError):
        duration_to_seconds(raw)


@pytest.mark.parametrize("path", [PODCASTS, VIDEO_YOUTUBE])
def test_roundtrip_is_stable_and_lossless(path):
    """A no-edit load+dump keeps the data, and dumping the dump changes nothing."""
    text = path.read_text(encoding="utf-8")
    yaml = make_yaml()
    once = dump_to_string(yaml, yaml.load(text))
    twice = dump_to_string(yaml, make_yaml().load(once))
    assert once == twice
    plain = YAML(typ="safe")
    assert plain.load(io.StringIO(once)) == plain.load(io.StringIO(text))


EPISODES = [
    {"title": "Trailer", "guid": "g0"},
    {"title": "1. Greatness!", "guid": "g1"},
    {"title": "2. Other", "guid": "g2"},
]


def test_match_episode_by_title_then_position():
    assert match_episode({"title": "1. greatness"}, 5, EPISODES) is EPISODES[1]
    assert match_episode({"title": "Unknown"}, 1, EPISODES) is None
    assert match_episode({"title": "2"}, 0, EPISODES) is EPISODES[0]
    assert match_episode({"title": "7"}, 9, EPISODES) is None
    assert match_episode({"title": "x", "guid": "g2"}, 0, EPISODES) is EPISODES[2]


def test_rebuild_chapter_keeps_every_key():
    yaml = make_yaml()
    data = yaml.load('- name: "Old"\n  custom: "kept"\n  rating: 5\n  device: "x"\n')
    chapter = data[0]
    ep = {"description": "d", "pubDate": "p", "episodeType": "full", "explicit": "no",
          "enclosure_url": "u", "image": "", "author": "a", "guid": "g", "episode": 3, "duration": 60}
    _rebuild_chapter_from_name(chapter, ep)
    keys = list(chapter)
    assert keys[0] == "title"
    assert "name" not in keys
    assert {"custom", "rating", "device", "guid", "duration"} <= set(keys)
    assert chapter["custom"] == "kept"
    assert keys.index("guid") < keys.index("custom")


def test_set_rss_fields_only_missing():
    target = {"guid": "keep"}
    ep = {"description": "d", "pubDate": "", "episodeType": "", "explicit": "", "enclosure_url": "",
          "image": "", "author": "", "guid": "new", "episode": None, "duration": 5}
    assert set_rss_fields(target, ep, only_missing=True)
    assert target["guid"] == "keep"
    assert target["duration"] == 5
