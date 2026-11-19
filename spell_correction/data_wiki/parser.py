"""Locate the bundled Persian Wikipedia corpus."""

from __future__ import annotations

from pathlib import Path

CORPUS_FILE_NAME = "Persian-WikiText.txt"


def get_path() -> str:
    """Return the absolute path of the bundled Persian Wikipedia corpus.

    Raises:
        FileNotFoundError: If the corpus file is missing from the package.
    """
    path = Path(__file__).resolve().parent / CORPUS_FILE_NAME
    if not path.is_file():
        raise FileNotFoundError(
            f"Corpus file not found at {path}. "
            "Make sure the repository was cloned completely (including data files)."
        )
    return str(path)
