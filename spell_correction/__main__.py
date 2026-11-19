"""Command-line interface: ``python -m spell_correction "متن ورودی"``."""

from __future__ import annotations

import argparse
import sys

from spell_correction.corrector import SpellCorrector


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(
        prog="python -m spell_correction",
        description="Correct spelling mistakes in Persian text using ParsBERT.",
    )
    arg_parser.add_argument(
        "text",
        nargs="*",
        help="Sentence(s) to correct. Reads one sentence per line from stdin if omitted.",
    )
    args = arg_parser.parse_args(argv)

    sentences = [" ".join(args.text)] if args.text else sys.stdin.read().splitlines()
    sentences = [s for s in sentences if s.strip()]
    if not sentences:
        arg_parser.error("no input text given")

    corrector = SpellCorrector()
    for sentence in sentences:
        print(corrector.correct(sentence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
