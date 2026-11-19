from __future__ import annotations

import pytest

from spell_correction.data_wiki import parser
from spell_correction.utils import (
    CleanText,
    find_homophone_pair,
    find_homophones,
    get_homophone_list,
    load_data,
)


def test_find_homophone_pair_both_directions():
    assert find_homophone_pair("سفر") == "صفر"
    assert find_homophone_pair("صفر") == "سفر"


def test_find_homophone_pair_unknown_word():
    assert find_homophone_pair("کتاب") is None
    assert find_homophones("کتاب") == []


def test_find_homophones_returns_all_alternatives():
    assert find_homophones("ارض") == ["ارز", "عرض"]
    assert find_homophones("ارز") == ["عرض", "ارض"]


def test_get_homophone_list_is_flat():
    words = get_homophone_list()
    assert "سفر" in words and "صفر" in words
    assert all(isinstance(w, str) for w in words)


def test_load_data_reads_utf8(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("سلام دنیا", encoding="utf-8")
    assert load_data(path) == "سلام دنیا"


def test_corpus_path_points_to_bundled_file():
    path = parser.get_path()
    assert path.endswith(parser.CORPUS_FILE_NAME)


def test_corpus_path_missing(monkeypatch):
    monkeypatch.setattr(parser, "CORPUS_FILE_NAME", "does-not-exist.txt")
    with pytest.raises(FileNotFoundError):
        parser.get_path()


@pytest.fixture(scope="module")
def cleaner():
    return CleanText()


def test_clean_text_removes_punctuation(cleaner):
    assert cleaner.clean_text("سلام، دنیا!") == ["سلام", "دنیا"]


def test_clean_text_sentence_output(cleaner):
    assert cleaner.clean_text("سلام، دنیا!", output="sentence") == "سلام دنیا"
