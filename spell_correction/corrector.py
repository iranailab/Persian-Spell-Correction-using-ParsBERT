"""Context-aware Persian spell corrector combining Norvig candidates with ParsBERT."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from spell_correction.data_wiki import parser
from spell_correction.NorvigSpellChecker import NorvigSpellChecker
from spell_correction.utils import CleanText, find_homophones, load_data

MASK_TOKEN = "[MASK]"


class MaskPredictor(Protocol):
    """Anything that can rank candidate tokens for a ``[MASK]`` position."""

    def predict_masked_sent(self, text: str, top_words: int = 5) -> list[str]: ...


class SpellCorrector:
    """Correct spelling mistakes and homophone confusions in Persian sentences.

    The pipeline is:

    1. Normalize and tokenize the sentence with Hazm.
    2. For every word the frequency dictionary does not trust, mask it and let
       ParsBERT rank replacements; the best-ranked word that is also a Norvig
       edit-distance candidate wins. Falls back to the Norvig correction.
    3. For every homophone (e.g. ``سفر`` / ``صفر``), mask it and keep whichever
       spelling ParsBERT ranks highest in context.

    Args:
        words: Corpus tokens for the frequency dictionary. Defaults to the
            bundled Persian Wikipedia corpus.
        predictor: Masked-LM predictor. Defaults to ParsBERT.
        top_words: How many BERT predictions to consider per masked word.
    """

    def __init__(
        self,
        words: Iterable[str] | None = None,
        predictor: MaskPredictor | None = None,
        top_words: int = 500,
    ) -> None:
        self.clean_text_model = CleanText()
        if words is None:
            words = self.clean_text_model.clean_text(load_data(parser.get_path()))
        self.spl = NorvigSpellChecker(words)

        if predictor is None:
            from spell_correction.MaskedSentencePredictor import (
                MaskedSentencePredictor,
            )

            predictor = MaskedSentencePredictor()
        self.bert_predictor = predictor
        self.top_words = top_words

    def _predict(self, words: list[str], index: int) -> list[str]:
        masked = [*words]
        masked[index] = MASK_TOKEN
        return self.bert_predictor.predict_masked_sent(
            " ".join(masked), top_words=self.top_words
        )

    def _fix_misspelling(self, words: list[str], index: int) -> str:
        word = words[index]
        norvig_cands = set(self.spl.candidates(word))
        preds = self._predict(words, index)
        best = next((p for p in preds if p in norvig_cands), None)
        return best if best is not None else self.spl.correction(word)

    def _fix_homophone(self, words: list[str], index: int) -> str:
        word = words[index]
        options = [word, *find_homophones(word)]
        if len(options) == 1:
            return word
        preds = self._predict(words, index)
        rank = {token: i for i, token in reversed(list(enumerate(preds)))}
        ranked = [option for option in options if option in rank]
        if not ranked:
            return word
        return min(ranked, key=rank.__getitem__)

    def correct(self, sentence: str) -> str:
        """Return the corrected version of ``sentence``."""
        words = self.clean_text_model.clean_text(sentence)

        for i, word in enumerate(words):
            if not self.spl.is_correct(word):
                words[i] = self._fix_misspelling(words, i)

        for i in range(len(words)):
            words[i] = self._fix_homophone(words, i)

        return " ".join(words)

    # Backwards-compatible name used by the original API.
    def get_correct_text(self, sentence: str) -> str:
        """Alias of :meth:`correct` kept for backwards compatibility."""
        return self.correct(sentence)
