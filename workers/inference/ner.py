"""spaCy NER demographic profiler.

Produces only the confirmed posts.analytics.demographics fields.
If spaCy or a model is missing, return None — do not invent demographics.
"""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)

PROFESSION_HINTS = {
    "ORG": "organization",
}


class DemographicHint:
    __slots__ = (
        "inferred_country",
        "inferred_region",
        "inferred_profession",
        "confidence",
    )

    def __init__(
        self,
        inferred_country: str | None,
        inferred_region: str | None,
        inferred_profession: str | None,
        confidence: float,
    ) -> None:
        self.inferred_country = inferred_country
        self.inferred_region = inferred_region
        self.inferred_profession = inferred_profession
        self.confidence = confidence

    def as_dict(self) -> dict[str, str | float | None]:
        return {
            "inferred_country": self.inferred_country,
            "inferred_region": self.inferred_region,
            "inferred_profession": self.inferred_profession,
            "confidence": self.confidence,
        }


class DemographicProfiler(Protocol):
    def profile(self, text: str) -> DemographicHint | None: ...


class UnavailableNerProfiler:
    def profile(self, text: str) -> DemographicHint | None:
        _ = text
        return None


class SpacyNerProfiler:
    def __init__(self, nlp: object | None = None, model_name: str = "en_core_web_sm") -> None:
        self._nlp = nlp
        self._model_name = model_name

    def _load(self) -> object | None:
        if self._nlp is not None:
            return self._nlp
        try:
            import spacy
        except ImportError:
            logger.warning("spaCy is not installed; demographics will be omitted")
            return None
        try:
            self._nlp = spacy.load(self._model_name)
        except Exception:
            logger.warning("spaCy model %s is unavailable", self._model_name)
            return None
        return self._nlp

    def profile(self, text: str) -> DemographicHint | None:
        nlp = self._load()
        if nlp is None or not text:
            return None
        try:
            doc = nlp(text)
        except Exception:
            logger.warning("spaCy NER failed; omitting demographics")
            return None
        country = None
        region = None
        profession = None
        hits = 0
        for ent in getattr(doc, "ents", []):
            label = getattr(ent, "label_", "")
            value = str(getattr(ent, "text", "")).strip()
            if not value:
                continue
            if label == "GPE" and country is None:
                country = value
                hits += 1
            elif label in {"LOC", "FAC"} and region is None:
                region = value
                hits += 1
            elif label in PROFESSION_HINTS and profession is None:
                profession = value
                hits += 1
        if hits == 0:
            return None
        confidence = min(1.0, hits / 3.0)
        return DemographicHint(country, region, profession, confidence)
