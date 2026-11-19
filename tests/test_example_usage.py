"""End-to-end tests with the real corpus and ParsBERT (slow, downloads the model)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def corrector():
    from spell_correction import SpellCorrector

    return SpellCorrector()


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        ("من صفر کردم", "من سفر کردم"),
        ("من سفر کردم", "من سفر کردم"),
    ],
)
def test_end_to_end(corrector, sentence, expected):
    assert corrector.correct(sentence) == expected
