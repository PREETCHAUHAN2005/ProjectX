"""GoEmotions label → POSITIVE | NEGATIVE | NEUTRAL.

Source-confirmed examples: joy/love → positive; fear/anger → negative.
The remaining 28-label table is an implementation contract so mapping is
deterministic (see .cursor/skills/sentiment-analysis/polarity-map.md).
"""

from __future__ import annotations

from typing import Literal

Polarity = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]

# Official SamLowe/roberta-base-go_emotions id2label order.
GO_EMOTIONS_LABELS: tuple[str, ...] = (
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
)

POLARITY_BY_LABEL: dict[str, Polarity] = {
    "admiration": "POSITIVE",
    "amusement": "POSITIVE",
    "anger": "NEGATIVE",
    "annoyance": "NEGATIVE",
    "approval": "POSITIVE",
    "caring": "POSITIVE",
    "confusion": "NEUTRAL",
    "curiosity": "NEUTRAL",
    "desire": "POSITIVE",
    "disappointment": "NEGATIVE",
    "disapproval": "NEGATIVE",
    "disgust": "NEGATIVE",
    "embarrassment": "NEGATIVE",
    "excitement": "POSITIVE",
    "fear": "NEGATIVE",
    "gratitude": "POSITIVE",
    "grief": "NEGATIVE",
    "joy": "POSITIVE",
    "love": "POSITIVE",
    "nervousness": "NEGATIVE",
    "optimism": "POSITIVE",
    "pride": "POSITIVE",
    "realization": "NEUTRAL",
    "relief": "POSITIVE",
    "remorse": "NEGATIVE",
    "sadness": "NEGATIVE",
    "surprise": "NEUTRAL",
    "neutral": "NEUTRAL",
}


class EmotionScore:
    __slots__ = ("label", "score")

    def __init__(self, label: str, score: float) -> None:
        self.label = label
        self.score = score

    def as_dict(self) -> dict[str, str | float]:
        return {"label": self.label, "score": self.score}


def polarity_from_emotions(
    emotions: list[EmotionScore],
) -> tuple[Polarity, float]:
    """Dominant label by score. Ties → NEUTRAL (implementation; not source-confirmed)."""
    if not emotions:
        raise ValueError("emotion vector is empty")

    top_score = max(item.score for item in emotions)
    winners = [item for item in emotions if item.score == top_score]
    if len(winners) != 1:
        return "NEUTRAL", top_score

    dominant = winners[0]
    bucket = POLARITY_BY_LABEL.get(dominant.label)
    if bucket is None:
        return "NEUTRAL", dominant.score
    return bucket, dominant.score
