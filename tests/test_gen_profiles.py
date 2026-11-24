"""Tests for gen_profiles.py, which renders data/profiles.yaml into the About
pages and data/identity.toml, and in --check mode fails the build when they
no longer match."""

import shutil

import pytest

import gen_profiles


@pytest.fixture(name="repo")
def fixture_repo(tmp_path, monkeypatch):
    """Copies of the real source and targets, with the script pointed at them."""
    for name in ("ABOUT_EN", "ABOUT_HE", "ABOUT_RU", "IDENTITY"):
        real = getattr(gen_profiles, name)
        copy = tmp_path / real.name.replace("_index", f"_index_{name}")
        shutil.copy(real, copy)
        monkeypatch.setattr(gen_profiles, name, copy)
    return tmp_path


def pairs():
    return gen_profiles.targets(gen_profiles.load_profiles(gen_profiles.SOURCE))


def test_committed_files_match_the_yaml():
    # The same assertion the build makes, against the real files.
    assert not gen_profiles.check(pairs())


@pytest.mark.usefixtures("repo")
def test_hand_edit_inside_the_block_is_caught():
    about = gen_profiles.ABOUT_HE
    text = about.read_text(encoding="utf-8")
    end = text.index(gen_profiles.END)
    about.write_text(text[:end] + "* [hand edit](https://example.com)\n" + text[end:], encoding="utf-8")
    assert gen_profiles.check(pairs()) == [about]
    gen_profiles.write(pairs())
    assert not gen_profiles.check(pairs())
    assert "hand edit" not in about.read_text(encoding="utf-8")


@pytest.mark.usefixtures("repo")
def test_text_outside_the_block_is_kept():
    about = gen_profiles.ABOUT_EN
    about.write_text("Hand-written prose.\n\n" + about.read_text(encoding="utf-8"), encoding="utf-8")
    assert not gen_profiles.check(pairs())


@pytest.mark.usefixtures("repo")
def test_stale_identity_is_caught():
    gen_profiles.IDENTITY.write_text('sameas = ["https://example.com"]\n', encoding="utf-8")
    assert gen_profiles.check(pairs()) == [gen_profiles.IDENTITY]


@pytest.mark.usefixtures("repo")
def test_missing_identity_is_caught():
    gen_profiles.IDENTITY.unlink()
    assert gen_profiles.check(pairs()) == [gen_profiles.IDENTITY]
