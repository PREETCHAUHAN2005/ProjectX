def make_post(
    *,
    external_id: str,
    timestamp: str,
    polarity: str,
    topic: str | None = "elections",
    country: str | None = "IN",
    language: str | None = "en",
    profession: str | None = "journalist",
    handle: str = "alice",
    user_id: str = "u1",
    text: str = "hello @bob",
    joy: float = 0.8,
    thread_role: str | None = None,
    in_reply_to: str | None = None,
    severity: str | None = None,
) -> dict:
    analytics = {
        "sentiment": {"label": polarity, "score": 0.8},
        "emotions": [
            {"label": "joy", "score": joy},
            {"label": "anger", "score": 0.1},
            {"label": "neutral", "score": 0.1},
        ],
        "topic_id": topic,
        "topic_name": topic,
        "demographics": {
            "inferred_country": country,
            "inferred_region": None,
            "inferred_profession": profession,
            "confidence": 0.5,
        },
    }
    if thread_role:
        analytics["thread_role"] = thread_role
    if in_reply_to:
        analytics["in_reply_to"] = in_reply_to
    if severity:
        analytics["severity"] = severity
    return {
        "platform": "telegram",
        "external_id": external_id,
        "timestamp": timestamp,
        "author": {"user_id": user_id, "handle": handle},
        "content": {"raw_text": text, "clean_text": text, "language": language},
        "analytics": analytics,
        "engagement": {},
    }
