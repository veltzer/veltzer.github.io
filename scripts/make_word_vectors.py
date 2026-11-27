#!/usr/bin/env python
"""
Write the word vectors the blog's semantic search loads, into
static/data/vectors/.

The vectors come from the newest release of github.com/veltzer/embeddings:
fastText trained on Wikipedia, 300 dimensions, English, Hebrew and Russian
rotated into one shared space. A release holds 200,000 words per language, 160 MB
gzipped; the browser gets a slice of that: the most frequent --common words
(what a query is likely to use) plus every word some post of that language
uses (what the posts are made of). Rows keep the release's order, most
frequent first, so regenerating after new posts mostly appends and git's
deltas stay small.

Per language: <lang>.words.json (the words, in row order), <lang>.int8 (each
row scaled to fill -127..127, row after row) and <lang>.scale.f32 (each
row's scale, little-endian float32). int8 is a quarter of float32's size and
moves the rankings not at all; cutting dimensions (PCA) was measured and
does move them, so all 300 stay. manifest.json records the release and the
tokenizer version.

The browser computes the post vectors itself from <lang>/search.json, so a
new post needs no rerun; a word only it uses is ignored until the next run.
A manual step, run from the repo root; the release is
downloaded once into download/embeddings/<tag>/.
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS = REPO_ROOT / "content" / "blog"
DEST = REPO_ROOT / "static" / "data" / "vectors"
CACHE = REPO_ROOT / "download" / "embeddings"
RELEASES = "https://api.github.com/repos/veltzer/embeddings/releases/latest"
LANGUAGES = ["en", "he", "ru"]

# The release's vectors are keyed by its tokenizer, so this one must be the
# same: tokenize() in the embeddings repo's scripts/common.py, copied, and
# checked against the release manifest's tokenizer_version. normalize() in
# static/blog-search.js is the third copy.
TOKENIZER_VERSION = 1
_WORD = re.compile(r"[^\W\d_]+(?:['\"][^\W\d_]+)*")
_FOLD = str.maketrans({
    "\u05f3": "'",  # Hebrew geresh
    "\u05f4": '"',  # Hebrew gershayim
    "\u2019": "'",  # right single quotation mark, the typographic apostrophe
})


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.translate(_FOLD))
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped.casefold()


def tokenize(text: str) -> list[str]:
    return _WORD.findall(normalize(text))


def post_words(lang: str) -> set[str]:
    """Every word of every post of lang, front matter (title, tags) included."""
    words: set[str] = set()
    for path in sorted(POSTS.glob(f"*.{lang}.md")):
        words.update(tokenize(path.read_text(encoding="utf-8")))
    return words


def get(url: str) -> bytes:
    """Fetch url. GitHub API calls carry GH_TOKEN when it is set (CI sets
    it), so they do not share the runner IP's anonymous rate limit."""
    request = urllib.request.Request(url)
    token = os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        body: bytes = response.read()
        return body


def fetch(release: dict[str, Any], name: str) -> Path:
    """Download one asset of release (once) and check it against SHA256SUMS."""
    tag_name: str = release["tag_name"]
    target = CACHE / tag_name
    target.mkdir(parents=True, exist_ok=True)
    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
    path = target / name
    if not path.exists():
        print(f"downloading {name} from release {release['tag_name']}", flush=True)
        sums = {}
        for line in get(assets["SHA256SUMS"]).decode().splitlines():
            digest, file = line.split()
            sums[file] = digest
        tmp = path.with_name(name + ".part")
        with urllib.request.urlopen(assets[name]) as response, tmp.open("wb") as f:
            while chunk := response.read(1 << 20):
                f.write(chunk)
        if hashlib.sha256(tmp.read_bytes()).hexdigest() != sums[name]:
            tmp.unlink()
            sys.exit(f"{name}: sha256 mismatch")
        tmp.replace(path)
    return path


def select(path: Path, common: int, wanted: set[str]) -> tuple[list[str], np.ndarray]:
    """The first common rows of a .vec.gz and those of the wanted words, in file order."""
    words: list[str] = []
    rows: list[str] = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        f.readline()
        for i, line in enumerate(f):
            word, _, numbers = line.partition(" ")
            if i < common or word in wanted:
                words.append(word)
                rows.append(numbers)
    vectors = np.array([np.array(r.split(), dtype=np.float32) for r in rows])
    return words, vectors


def quantize(vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # An all-zero row would give scale 0 and 0/0 = NaN; give it scale 1/127 so
    # it quantizes to zeros and dequantizes to zeros with a finite scale.
    peak = np.abs(vectors).max(axis=1)
    scale = np.where(peak == 0, 1.0, peak).astype(np.float64) / 127
    return np.round(vectors / scale[:, None]).astype(np.int8), scale.astype("<f4")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--common", type=int, default=10000, help="most frequent words kept per language")
    parser.add_argument("--languages", nargs="+", choices=LANGUAGES, default=LANGUAGES,
                        help="redo only these languages; the others keep their files and manifest entry")
    args = parser.parse_args()

    release = json.loads(get(RELEASES))
    manifest = json.loads(fetch(release, "manifest.json").read_text())
    if manifest["tokenizer_version"] != TOKENIZER_VERSION:
        sys.exit(f"release {release['tag_name']} uses tokenizer version {manifest['tokenizer_version']}, "
                 f"this script and blog-search.js implement {TOKENIZER_VERSION}")
    DEST.mkdir(parents=True, exist_ok=True)
    out = {"release": release["tag_name"], "tokenizer_version": TOKENIZER_VERSION, "languages": {}}
    previous = DEST / "manifest.json"
    if set(args.languages) != set(LANGUAGES) and previous.is_file():
        kept = json.loads(previous.read_text())
        if kept["release"] != out["release"] or kept["tokenizer_version"] != TOKENIZER_VERSION:
            sys.exit(f"{previous} is from another release; redo every language")
        out["languages"] = {lang: kept["languages"][lang] for lang in LANGUAGES
                            if lang not in args.languages and lang in kept["languages"]}
    for lang in args.languages:
        wanted = post_words(lang)
        words, vectors = select(fetch(release, f"{lang}.vec.gz"), args.common, wanted)
        rows, scale = quantize(vectors)
        (DEST / f"{lang}.words.json").write_text(json.dumps(words, ensure_ascii=False) + "\n", encoding="utf-8")
        (DEST / f"{lang}.int8").write_bytes(rows.tobytes())
        (DEST / f"{lang}.scale.f32").write_bytes(scale.tobytes())
        missing = len(wanted) - len(set(words) & wanted)
        out["languages"][lang] = {"words": len(words), "dim": vectors.shape[1], "post_words_missing": missing}
        size = sum((DEST / f"{lang}.{ext}").stat().st_size for ext in ("words.json", "int8", "scale.f32"))
        print(f"{lang}: {len(words)} words x {vectors.shape[1]}, {size / 1e6:.1f} MB; "
              f"{missing} post words are not in the release")
    out["languages"] = {lang: out["languages"][lang] for lang in LANGUAGES if lang in out["languages"]}
    (DEST / "manifest.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
