from __future__ import annotations

from spell_correction.corrector import SpellCorrector

CORPUS = ["من"] * 100 + ["سفر"] * 60 + ["صفر"] * 60 + ["کردم"] * 80 + ["کتاب"] * 50
CORPUS += ["خواندم"] * 50 + ["کباب"] * 40


def make(fake_predictor_factory, ranking):
    predictor = fake_predictor_factory(ranking)
    return SpellCorrector(words=CORPUS, predictor=predictor), predictor


def test_correct_sentence_is_unchanged(fake_predictor_factory):
    corrector, predictor = make(fake_predictor_factory, ["کتاب"])
    assert corrector.correct("من کتاب خواندم") == "من کتاب خواندم"
    assert predictor.calls == []  # no homophones and no misspellings


def test_misspelling_uses_bert_ranking(fake_predictor_factory):
    # Norvig alone would pick the more frequent "کتاب"; BERT context prefers "کباب".
    corrector, predictor = make(fake_predictor_factory, ["غذا", "کباب", "کتاب"])
    assert corrector.correct("من کتاپ خواندم") == "من کباب خواندم"
    assert predictor.calls == ["من [MASK] خواندم"]


def test_misspelling_falls_back_to_norvig(fake_predictor_factory):
    corrector, _ = make(fake_predictor_factory, ["غذا"])
    assert corrector.correct("من کتاپ خواندم") == "من کتاب خواندم"


def test_homophone_replaced_when_alternative_ranks_higher(fake_predictor_factory):
    corrector, _ = make(fake_predictor_factory, ["سفر", "کار", "صفر"])
    assert corrector.correct("من صفر کردم") == "من سفر کردم"


def test_homophone_kept_when_it_ranks_higher(fake_predictor_factory):
    corrector, _ = make(fake_predictor_factory, ["سفر", "کار", "صفر"])
    assert corrector.correct("من سفر کردم") == "من سفر کردم"


def test_homophone_kept_when_no_option_predicted(fake_predictor_factory):
    corrector, _ = make(fake_predictor_factory, ["کار"])
    assert corrector.correct("من صفر کردم") == "من صفر کردم"


def test_top_words_is_forwarded(fake_predictor_factory):
    predictor = fake_predictor_factory(["کار", "سفر"])
    corrector = SpellCorrector(words=CORPUS, predictor=predictor, top_words=1)
    assert corrector.correct("من صفر کردم") == "من صفر کردم"


def test_legacy_api(fake_predictor_factory):
    from Spell_correction import correct_spelling

    model = correct_spelling(words=CORPUS, predictor=fake_predictor_factory(["سفر"]))
    assert model.get_correct_text("من صفر کردم") == "من سفر کردم"
