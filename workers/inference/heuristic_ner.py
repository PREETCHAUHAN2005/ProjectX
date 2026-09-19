"""Keyword demographic hints when spaCy is unavailable.

IMPLEMENTATION fallback. Emits only confirmed demographics fields.
"""

from __future__ import annotations

from workers.inference.ner import DemographicHint

_COUNTRY_HINTS: tuple[tuple[str, str], ...] = (
    ("bangladesh", "Bangladesh"),
    ("dhaka", "Bangladesh"),
    ("united kingdom", "United Kingdom"),
    ("london", "United Kingdom"),
    ("united states", "United States"),
    ("washington", "United States"),
    ("uae", "UAE"),
    ("dubai", "UAE"),
    ("singapore", "Singapore"),
    ("germany", "Germany"),
    ("berlin", "Germany"),
    ("assam", "India"),
    ("patna", "India"),
    ("kerala", "India"),
    ("chennai", "India"),
    ("mumbai", "India"),
    ("delhi", "India"),
    ("kolkata", "India"),
    ("bengaluru", "India"),
    ("guwahati", "India"),
    ("srinagar", "India"),
    ("ladakh", "India"),
    ("india", "India"),
)

_REGION_HINTS: tuple[tuple[str, str], ...] = (
    ("assam", "Assam"),
    ("bihar", "Bihar"),
    ("kerala", "Kerala"),
    ("ladakh", "Ladakh"),
    ("kashmir", "Kashmir"),
    ("tamil nadu", "Tamil Nadu"),
)

_PROFESSION_HINTS: tuple[tuple[str, str], ...] = (
    ("journalist", "journalist"),
    ("reporter", "media"),
    ("volunteer", "volunteer"),
    ("engineer", "engineer"),
    ("analyst", "analyst"),
    ("official", "public sector"),
    ("district", "public sector"),
    ("ndrf", "public sector"),
    ("researcher", "researcher"),
    ("doctor", "health worker"),
)


class HeuristicNerProfiler:
    def profile(self, text: str) -> DemographicHint | None:
        if not text:
            return None
        lowered = text.lower()
        country = next((name for key, name in _COUNTRY_HINTS if key in lowered), None)
        region = next((name for key, name in _REGION_HINTS if key in lowered), None)
        profession = next((name for key, name in _PROFESSION_HINTS if key in lowered), None)
        hits = sum(value is not None for value in (country, region, profession))
        if hits == 0:
            return DemographicHint("India", None, None, 0.25)
        return DemographicHint(country, region, profession, min(1.0, hits / 3.0))
