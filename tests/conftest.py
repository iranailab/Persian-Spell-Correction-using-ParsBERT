from __future__ import annotations

import pytest


class FakePredictor:
    """Deterministic stand-in for ParsBERT that returns a fixed ranking."""

    def __init__(self, ranking: list[str]) -> None:
        self.ranking = ranking
        self.calls: list[str] = []

    def predict_masked_sent(self, text: str, top_words: int = 5) -> list[str]:
        assert "[MASK]" in text
        self.calls.append(text)
        return self.ranking[:top_words]


@pytest.fixture
def fake_predictor_factory():
    return FakePredictor
