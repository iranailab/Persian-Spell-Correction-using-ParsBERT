from __future__ import annotations

import pytest

from spell_correction.NorvigSpellChecker import NorvigSpellChecker


@pytest.fixture
def checker():
    words = ["کتاب"] * 50 + ["کباب"] * 40 + ["کتب"] * 5 + ["و"] * 100 + ["ژ"] * 100
    return NorvigSpellChecker(words)


def test_probability(checker):
    assert checker.P("کتاب") == pytest.approx(50 / 295)
    assert checker.P("ناشناخته") == 0


def test_empty_corpus_probability_is_zero():
    assert NorvigSpellChecker([]).P("کتاب") == 0.0


def test_is_correct_uses_frequency_threshold(checker):
    assert checker.is_correct("کتاب")
    assert not checker.is_correct("کتب")  # too rare
    assert not checker.is_correct("کتاپ")  # unknown


def test_single_char_must_be_stopword(checker):
    assert checker.is_correct("و")
    assert not checker.is_correct("ژ")


def test_candidates_sorted_by_probability(checker):
    assert checker.candidates("کااب") == ["کتاب", "کباب"]
    assert checker.candidates("کتاپ") == ["کتاب"]
    assert checker.candidates("کتاب") == []  # already correct


def test_correction_picks_most_frequent(checker):
    assert checker.correction("کتاپ") == "کتاب"
    assert checker.correction("کتاب") == "کتاب"


def test_correction_uses_two_edits(checker):
    assert checker.correction("کتاپپ") == "کتاب"


def test_correction_returns_word_when_nothing_known(checker):
    assert checker.correction("ییییییی") == "ییییییی"


def test_edits1_contains_all_edit_types():
    checker = NorvigSpellChecker([], letters="اب")
    edits = checker.edits1("اب")
    assert "ا" in edits  # delete
    assert "با" in edits  # transpose
    assert "بب" in edits  # replace
    assert "ااب" in edits  # insert
