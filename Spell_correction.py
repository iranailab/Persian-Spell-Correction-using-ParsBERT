"""Backwards-compatible entry point.

Prefer ``from spell_correction import SpellCorrector`` in new code.
"""

from spell_correction.corrector import SpellCorrector


class correct_spelling(SpellCorrector):  # noqa: N801 - kept for backwards compatibility
    """Deprecated alias of :class:`spell_correction.SpellCorrector`."""


__all__ = ["SpellCorrector", "correct_spelling"]

if __name__ == "__main__":
    model = SpellCorrector()
    print(model.correct("من صفر کردم"))
