"""SamLowe/roberta-base-go_emotions inferencer.

The Hugging Face pipeline is loaded lazily. Tests inject a fake that still
returns the full 28-d vector. Do not substitute another emotion model.
"""

from __future__ import annotations

import logging
from typing import Protocol

from workers.inference.polarity import GO_EMOTIONS_LABELS, EmotionScore

logger = logging.getLogger(__name__)

GO_EMOTIONS_MODEL_ID = "SamLowe/roberta-base-go_emotions"


class EmotionInferencer(Protocol):
    def infer(self, text: str) -> list[EmotionScore]: ...


class InferenceError(RuntimeError):
    """Model I/O failed — callers must not invent emotion scores."""


class HuggingFaceGoEmotions:
    def __init__(self, model_id: str = GO_EMOTIONS_MODEL_ID) -> None:
        if model_id != GO_EMOTIONS_MODEL_ID:
            raise ValueError("Emotion model substitution is not allowed")
        self._model_id = model_id
        self._pipeline = None
        self._tokenizer = None

    @property
    def tokenizer(self):
        self._ensure_loaded()
        return self._tokenizer

    def _ensure_loaded(self) -> None:
        if self._pipeline is not None:
            return
        try:
            from transformers import pipeline as hf_pipeline
        except ImportError as exc:
            raise InferenceError("transformers is not installed") from exc
        logger.info("Loading emotion model %s", self._model_id)
        self._pipeline = hf_pipeline(
            task="text-classification",
            model=self._model_id,
            top_k=None,
            function_to_apply="sigmoid",
            truncation=True,
            max_length=512,
        )
        self._tokenizer = getattr(self._pipeline, "tokenizer", None)

    def infer(self, text: str) -> list[EmotionScore]:
        self._ensure_loaded()
        assert self._pipeline is not None
        try:
            raw = self._pipeline(text)
        except Exception as exc:
            raise InferenceError("GoEmotions forward pass failed") from exc
        rows = raw[0] if raw and isinstance(raw[0], list) else raw
        by_label = {str(item["label"]).lower(): float(item["score"]) for item in rows}
        missing = [label for label in GO_EMOTIONS_LABELS if label not in by_label]
        if missing:
            raise InferenceError("GoEmotions output missing labels")
        return [EmotionScore(label, by_label[label]) for label in GO_EMOTIONS_LABELS]


class StaticEmotionInferencer:
    """Test double: returns a provided 28-d vector. Not used in production."""

    def __init__(self, emotions: list[EmotionScore]) -> None:
        if len(emotions) != len(GO_EMOTIONS_LABELS):
            raise ValueError("static inferencer must return all 28 labels")
        self._emotions = emotions

    def infer(self, text: str) -> list[EmotionScore]:
        _ = text
        return list(self._emotions)


def vector_with_dominant(label: str, score: float = 0.9) -> list[EmotionScore]:
    if label not in GO_EMOTIONS_LABELS:
        raise ValueError(f"unknown GoEmotions label: {label}")
    remainder = (1.0 - score) / (len(GO_EMOTIONS_LABELS) - 1)
    return [
        EmotionScore(name, score if name == label else remainder)
        for name in GO_EMOTIONS_LABELS
    ]
