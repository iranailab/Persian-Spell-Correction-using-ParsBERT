"""Masked-word prediction with ParsBERT."""

from __future__ import annotations

import torch
from transformers import BertForMaskedLM, BertTokenizer

DEFAULT_MODEL_NAME = "HooshvareLab/bert-fa-base-uncased"


class MaskedSentencePredictor:
    """Predict the most likely tokens for a ``[MASK]`` in a Persian sentence.

    Args:
        model_name: Hugging Face model id or local path of a BERT masked-LM.
        device: Torch device to run on. Defaults to CUDA when available.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str | torch.device | None = None,
    ) -> None:
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForMaskedLM.from_pretrained(model_name)
        self.model.eval()
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(self.device)

    def predict_masked_sent(self, text: str, top_words: int = 5) -> list[str]:
        """Return the ``top_words`` most likely tokens for the first ``[MASK]``.

        Args:
            text: Sentence containing a ``[MASK]`` token.
            top_words: Number of predictions to return.

        Raises:
            ValueError: If ``text`` contains no ``[MASK]`` token.
        """
        tokens = self.tokenizer.tokenize(f"[CLS] {text} [SEP]")
        try:
            masked_index = tokens.index(self.tokenizer.mask_token)
        except ValueError:
            raise ValueError("Input text must contain a [MASK] token.") from None

        input_ids = torch.tensor(
            [self.tokenizer.convert_tokens_to_ids(tokens)], device=self.device
        )

        with torch.no_grad():
            logits = self.model(input_ids).logits

        probs = torch.softmax(logits[0, masked_index], dim=-1)
        k = min(top_words, probs.shape[-1])
        top_indices = torch.topk(probs, k, sorted=True).indices
        return self.tokenizer.convert_ids_to_tokens(top_indices.tolist())
