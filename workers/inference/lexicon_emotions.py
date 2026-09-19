"""DEMO FALLBACK 28-d GoEmotions vector when Hugging Face is not loaded.

This is not a substitute emotion model. Production still uses
`SamLowe/roberta-base-go_emotions`. The lexicon only fills the confirmed
28-label space so a laptop demo can run the same polarity mapping without
downloading PyTorch weights.
"""

from __future__ import annotations

import re

from workers.inference.polarity import GO_EMOTIONS_LABELS, EmotionScore

# (keywords, dominant GoEmotions label)
_KEYWORD_LABELS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("joy", "happy", "delighted", "wonderful", "great news"), "joy"),
    (("love", "beloved"), "love"),
    (("thank", "thanks", "grateful", "gratitude"), "gratitude"),
    (("relief", "rescued", "restored", "cleared"), "relief"),
    (("proud", "pride"), "pride"),
    (("optimism", "hopeful", "hope "), "optimism"),
    (("excited", "excitement"), "excitement"),
    (("care", "caring", "volunteer", "ration"), "caring"),
    (("approve", "approval", "endorsed"), "approval"),
    (("admiration", "commend", "salute"), "admiration"),
    (("fear", "afraid", "terror", "threat", "malware", "phishing", "flood", "evacuat"), "fear"),
    (("anger", "angry", "furious", "outrage"), "anger"),
    (("annoy", "outage", "delay", "congestion", "load shedding"), "annoyance"),
    (("sad", "grief", "death", "casualty", "drowned"), "sadness"),
    (("disappoint", "fell short"), "disappointment"),
    (("disgust", "revolting"), "disgust"),
    (("disapprove", "condemn"), "disapproval"),
    (("nervous", "tension", "uneasy"), "nervousness"),
    (("remorse", "sorry", "apology"), "remorse"),
    (("embarrass",), "embarrassment"),
    (("confus", "unclear"), "confusion"),
    (("curious", "asking", "anyone know"), "curiosity"),
    (("surprise", "unexpected", "sudden"), "surprise"),
    (("realize", "confirmed report"), "realization"),
    (("desire", "need dry", "need boats"), "desire"),
    (("amusement", "laugh"), "amusement"),
)


def _dominant_label(text: str) -> str:
    lowered = text.lower()
    best_label = "neutral"
    best_score = 0
    for keywords, label in _KEYWORD_LABELS:
        matched = [word for word in keywords if word in lowered]
        if not matched:
            continue
        score = len(matched) * 10 + max(len(word) for word in matched)
        if score > best_score:
            best_score = score
            best_label = label
    return best_label


class LexiconEmotionInferencer:
    """Deterministic 28-d vector in the GoEmotions label order."""

    def infer(self, text: str) -> list[EmotionScore]:
        dominant = _dominant_label(text)
        token_n = max(1, len(re.findall(r"\w+", text)))
        peak = min(0.93, 0.62 + min(token_n, 24) * 0.008)
        remainder = (1.0 - peak) / (len(GO_EMOTIONS_LABELS) - 1)
        return [
            EmotionScore(label, peak if label == dominant else remainder)
            for label in GO_EMOTIONS_LABELS
        ]
