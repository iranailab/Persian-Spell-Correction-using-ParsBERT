"""A Norvig-style, frequency-based spell checker for Persian."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from functools import lru_cache

import hazm

PERSIAN_LETTERS = "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"


@lru_cache(maxsize=1)
def _stopwords() -> frozenset[str]:
    return frozenset(hazm.stopwords_list())


class NorvigSpellChecker:
    """Spell checker based on Peter Norvig's edit-distance approach.

    Args:
        words: Corpus tokens used to build the word-frequency dictionary.
        min_frequency: Words seen fewer times than this are treated as possibly
            misspelled.
        letters: Alphabet used to generate edit candidates.
    """

    def __init__(
        self,
        words: Iterable[str],
        min_frequency: int = 30,
        letters: str = PERSIAN_LETTERS,
    ) -> None:
        self.WORDS: Counter[str] = Counter(words)
        self.N = sum(self.WORDS.values())
        self.min_frequency = min_frequency
        self.letters = letters

    def P(self, word: str) -> float:
        """Probability of ``word`` occurring in the corpus."""
        if self.N == 0:
            return 0.0
        return self.WORDS[word] / self.N

    def is_correct(self, word: str) -> bool:
        """Return ``True`` if ``word`` is frequent enough to be trusted as-is.

        Single-character tokens are only trusted when they are stopwords.
        """
        if self.WORDS[word] < self.min_frequency:
            return False
        return not (len(word) == 1 and word not in _stopwords())

    def candidates(self, word: str) -> list[str]:
        """Known words one edit away from ``word``, most probable first.

        Returns an empty list when ``word`` is considered correct.
        """
        if self.is_correct(word):
            return []
        return sorted(self.known(self.edits1(word)), key=self.P, reverse=True)

    def correction(self, word: str) -> str:
        """Most probable spelling correction for ``word``."""
        return max(self.word_pool(word), key=self.P)

    def word_pool(self, word: str) -> set[str] | list[str]:
        """Known words at the smallest edit distance (0, 1, then 2) from ``word``."""
        return (
            self.known([word])
            or self.known(self.edits1(word))
            or self.known(self.edits2(word))
            or [word]
        )

    def known(self, words: Iterable[str]) -> set[str]:
        """Subset of ``words`` that appear in the corpus."""
        return {w for w in words if w in self.WORDS}

    def edits1(self, word: str) -> set[str]:
        """All strings one delete, transpose, replace or insert away from ``word``."""
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in self.letters]
        inserts = [L + c + R for L, R in splits for c in self.letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word: str) -> Iterator[str]:
        """All strings two edits away from ``word``."""
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))
