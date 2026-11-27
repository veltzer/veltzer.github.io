"""Tests for make_word_vectors.py's tokenizer.

The release's vectors are keyed by the embeddings repo's tokenizer, so this
copy must split and fold text exactly as that one does; a word it spells
differently simply has no vector. These pin the cases the two copies (and
blog-search.js, the third) must agree on.
"""

import numpy as np

from make_word_vectors import quantize, tokenize


def test_niqqud_is_dropped() -> None:
    assert tokenize("שָׁלוֹם עוֹלָם") == ["שלום", "עולם"]


def test_geresh_and_gershayim_fold_to_ascii() -> None:
    assert tokenize("ג\u05f3ק של צה\u05f4ל") == ["ג'ק", "של", 'צה"ל']


def test_apostrophes_and_accents() -> None:
    assert tokenize("Don\u2019t visit the Café") == ["don't", "visit", "the", "cafe"]


def test_digits_and_punctuation_split_words() -> None:
    assert tokenize("in 2026, re-run it") == ["in", "re", "run", "it"]


def test_quantize_all_zero_row_is_zeros_with_finite_scale() -> None:
    vectors = np.array([[0.0, 0.0, 0.0], [0.5, -0.25, 0.1]], dtype=np.float32)
    rows, scale = quantize(vectors)
    assert np.isfinite(scale).all()
    assert (scale > 0).all()
    assert not rows[0].any()
    assert np.array_equal(rows[1], np.round(vectors[1] / scale[1]).astype(np.int8))
    assert np.allclose(rows * scale[:, None], vectors, atol=float(scale.max()) / 2)


def test_quantize_round_trips_closely() -> None:
    vectors = np.array([[0.5, -0.25, 0.1], [-0.02, 0.01, 0.0]], dtype=np.float32)
    rows, scale = quantize(vectors)
    assert rows.dtype == np.int8
    assert np.abs(rows).max() == 127
    assert np.allclose(rows * scale[:, None], vectors, atol=float(scale.max()) / 2)
