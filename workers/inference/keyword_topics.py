"""Hashtag / keyword topic assignment when BERTopic is not fitted.

IMPLEMENTATION fallback for local demo. Not claimed as BERTopic output.
"""

from __future__ import annotations

import re

from workers.inference.topics import TopicAssignment

HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)")

_TOPIC_RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("flood_relief", "flood relief", ("flood", "inundat", "embankment", "ndrf", "boat", "relief camp", "floodrelief")),
    ("cyber_threat", "cyber threat", ("malware", "phishing", "ransomware", "c2", "cyber", "credential")),
    ("elections", "elections", ("election", "ballot", "poll", "vote", "evm", "campaign")),
    ("border_security", "border security", ("border", "infiltration", "patrol", "loc ", "forward post")),
    ("power_outage", "power outage", ("outage", "grid", "feeder", "load shedding", "blackout", "power")),
    ("public_health", "public health", ("vaccine", "outbreak", "hospital", "aqi", "air quality", "health")),
    ("transport", "transport", ("railway", "metro", "port", "berth", "highway", "underpass", "transit")),
    ("civic", "civic services", ("municipal", "ration", "advisory", "district office", "pump")),
)


def _from_hashtag(tag: str) -> TopicAssignment | None:
    compact = tag.lower()
    for topic_id, name, keys in _TOPIC_RULES:
        if any(key.replace(" ", "") in compact or key in compact for key in keys):
            return TopicAssignment(topic_id, name)
    return None


class KeywordTopicClusterer:
    def assign(self, text: str) -> TopicAssignment | None:
        if not text:
            return None
        for tag in HASHTAG_RE.findall(text):
            hit = _from_hashtag(tag)
            if hit is not None:
                return hit
        lowered = text.lower()
        best: TopicAssignment | None = None
        best_hits = 0
        for topic_id, name, keys in _TOPIC_RULES:
            hits = sum(1 for key in keys if key in lowered)
            if hits > best_hits:
                best_hits = hits
                best = TopicAssignment(topic_id, name)
        if best is not None:
            return best
        return TopicAssignment("general", "general discourse")
