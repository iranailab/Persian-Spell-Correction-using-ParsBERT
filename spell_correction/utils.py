"""Text utilities and the Persian homophone table."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, overload

import hazm

HOMOPHONES: tuple[tuple[str, str], ...] = (
    ("خار", "خوار"),
    ("سد", "صد"),
    ("خیش", "خویش"),
    ("خاست", "خواست"),
    ("ثواب", "صواب"),
    ("قاضی", "غازی"),
    ("علم", "الم"),
    ("غریب", "قریب"),
    ("غالب", "قالب"),
    ("پرتغال", "پرتقال"),
    ("غدیر", "قدیر"),
    ("حول", "هول"),
    ("اساس", "اثاث"),
    ("اسم", "اثم"),
    ("عمل", "امل"),
    ("امارت", "عمارت"),
    ("حیات", "حیاط"),
    ("سیف", "صیف"),
    ("خان", "خوان"),
    ("سفر", "صفر"),
    ("عرض", "ارز"),
    ("ارض", "ارز"),
    ("ارض", "عرض"),
    ("راضی", "رازی"),
    ("آقا", "آغا"),
    ("غذا", "قضا"),
    ("خرد", "خورد"),
    ("هضم", "حزم"),
    ("تهدید", "تحدید"),
    ("حوزه", "حوضه"),
    ("قدر", "غدر"),
    ("صر", "سر"),
)

# Backwards-compatible alias (the table used to be a mutable list named ``homophones``).
homophones = [list(pair) for pair in HOMOPHONES]

_PUNCTUATION_RE = re.compile(r"[^\w\s]")


def load_data(file_path: str | Path) -> str:
    """Read a UTF-8 text file and return its content."""
    return Path(file_path).read_text(encoding="utf-8")


def find_homophones(word: str) -> list[str]:
    """Return every homophone of ``word`` (in table order, without duplicates)."""
    result: list[str] = []
    for first, second in HOMOPHONES:
        other = second if word == first else first if word == second else None
        if other is not None and other not in result:
            result.append(other)
    return result


def find_homophone_pair(word: str) -> str | None:
    """Return the first homophone of ``word`` or ``None`` if it has none."""
    matches = find_homophones(word)
    return matches[0] if matches else None


def get_homophone_list() -> list[str]:
    """Return a flat list of every word that appears in the homophone table."""
    return [word for pair in HOMOPHONES for word in pair]


class CleanText:
    """Normalize, strip punctuation from, and tokenize Persian text with Hazm."""

    def __init__(self) -> None:
        self.normalizer = hazm.Normalizer()
        self.tokenizer = hazm.WordTokenizer()

    @overload
    def clean_text(self, text: str, output: Literal["word"] = ...) -> list[str]: ...

    @overload
    def clean_text(self, text: str, output: Literal["sentence"]) -> str: ...

    def clean_text(self, text: str, output: str = "word") -> list[str] | str:
        """Clean and tokenize ``text``.

        Args:
            text: The input text.
            output: ``"word"`` (default) returns a list of tokens,
                ``"sentence"`` returns the tokens joined by single spaces.
        """
        normalized_text = self.normalizer.normalize(text)
        punc_removed = _PUNCTUATION_RE.sub("", normalized_text)
        tokens = self.tokenizer.tokenize(punc_removed)
        if output == "word":
            return tokens
        return " ".join(tokens)
