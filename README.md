# Persian Spell Correction using ParsBERT

[![CI](https://github.com/iranailab/Persian-Spell-Correction-using-ParsBERT/actions/workflows/ci.yml/badge.svg)](https://github.com/iranailab/Persian-Spell-Correction-using-ParsBERT/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A context-aware spell corrector for Persian (Farsi) text. It combines a classic
frequency-based **Norvig spell checker** with the **ParsBERT** masked language model
(`HooshvareLab/bert-fa-base-uncased`) to fix both typos and real-word errors such as
homophone confusions (e.g. `صفر` ↔ `سفر`).

```text
input:  من صفر کردم
output: من سفر کردم
```

## How it works

1. **Normalize & tokenize** the sentence with [Hazm](https://github.com/roshan-research/hazm).
2. **Detect misspellings** – a word is suspicious if it is rare (fewer than 30
   occurrences) in a word-frequency dictionary built from a Persian Wikipedia corpus.
3. **Correct with context** – each suspicious word is replaced by `[MASK]` and ParsBERT
   ranks possible replacements. The highest-ranked prediction that is also within one
   edit of the original word wins; otherwise the most frequent Norvig correction is used.
4. **Resolve homophones** – words from a built-in homophone table (e.g. `حیات`/`حیاط`,
   `خواست`/`خاست`) are masked, and whichever spelling ParsBERT ranks highest in context
   is kept.

## Installation

Requires **Python 3.9 – 3.11** (Hazm 0.10 pins NumPy 1.24, which has no wheels for 3.12+).

```bash
git clone https://github.com/iranailab/Persian-Spell-Correction-using-ParsBERT
cd Persian-Spell-Correction-using-ParsBERT

python -m venv .venv && source .venv/bin/activate

# Optional: CPU-only PyTorch (much smaller download)
pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt
```

The ParsBERT model (~650 MB) is downloaded automatically from the Hugging Face Hub on
first use and cached under `~/.cache/huggingface`.

## Usage

### Python

```python
from spell_correction import SpellCorrector

corrector = SpellCorrector()          # loads the corpus and ParsBERT (takes a while)
print(corrector.correct("من صفر کردم"))  # -> من سفر کردم
```

Create the corrector once and reuse it — building the frequency dictionary and loading
the model is the expensive part.

Options:

| Argument    | Default                     | Description                                       |
|-------------|-----------------------------|---------------------------------------------------|
| `words`     | bundled Wikipedia corpus    | Iterable of tokens used for the frequency dictionary |
| `predictor` | `MaskedSentencePredictor()` | Any object with `predict_masked_sent(text, top_words)` |
| `top_words` | `500`                       | Number of BERT predictions considered per masked word |

To use a different BERT checkpoint or device:

```python
from spell_correction import SpellCorrector
from spell_correction.MaskedSentencePredictor import MaskedSentencePredictor

predictor = MaskedSentencePredictor("HooshvareLab/bert-fa-base-uncased", device="cpu")
corrector = SpellCorrector(predictor=predictor)
```

The original API still works:

```python
from Spell_correction import correct_spelling

model = correct_spelling()
model.get_correct_text("من صفر کردم")
```

### Command line

```bash
python -m spell_correction "من صفر کردم"

# or one sentence per line from stdin
cat sentences.txt | python -m spell_correction
```

## Project structure

```text
├── spell_correction/
│   ├── __init__.py                  # Public API (SpellCorrector, NorvigSpellChecker, CleanText)
│   ├── __main__.py                  # Command-line interface
│   ├── corrector.py                 # SpellCorrector: the full correction pipeline
│   ├── MaskedSentencePredictor.py   # ParsBERT masked-word prediction
│   ├── NorvigSpellChecker.py        # Frequency/edit-distance spell checker
│   ├── utils.py                     # Text cleaning and homophone table
│   └── data_wiki/
│       ├── parser.py                # Locates the bundled corpus
│       └── Persian-WikiText.txt     # Persian Wikipedia corpus (~96 MB)
├── tests/                           # Unit tests (fast) and integration tests (ParsBERT)
├── Spell_correction.py              # Backwards-compatible entry point
├── pyproject.toml                   # Packaging and tool configuration
├── requirements.txt                 # Runtime dependencies
└── requirements-dev.txt             # Development dependencies
```

## Development

```bash
pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
make install-dev   # dev dependencies + pre-commit hooks

make lint          # ruff + black --check
make format        # auto-fix lint issues and format
make test          # fast unit tests (ParsBERT is replaced by a fake predictor)
make test-all      # also run integration tests (downloads ParsBERT)
```

### CI/CD

GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs on every
push to `main` and every pull request:

| Job                 | What it does                                                        |
|---------------------|---------------------------------------------------------------------|
| **Lint**            | `ruff` and `black --check`                                          |
| **Unit tests**      | Python 3.9 / 3.10 / 3.11 matrix with coverage, CPU-only PyTorch     |
| **Integration tests** | End-to-end tests with the real corpus and a cached ParsBERT model |
| **Build**           | Builds sdist and wheel and validates them with `twine check`        |
| **Release**         | On a `v*` tag, publishes a GitHub Release with the built packages   |

Dependabot keeps GitHub Actions and Python dependencies up to date.

To cut a release:

```bash
git tag v0.2.0 && git push origin v0.2.0
```

## Limitations

- The misspelling detector is frequency-based, so rare but correct words may be
  flagged, and they are only replaced if a better candidate exists.
- ParsBERT predicts WordPiece tokens, so corrections are limited to words that exist
  as whole tokens in its vocabulary or in the corpus.
- Homophone handling only covers the pairs listed in `spell_correction/utils.py`.
  Contributions to extend the table are welcome.

## License

Released under the [MIT License](LICENSE).
