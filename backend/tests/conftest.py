import pytest

from app.services.ingest import persist_analyzed_post
from app.stores.graph import reset_graph_store_for_tests
from app.stores.posts import reset_post_store_for_tests


@pytest.fixture(autouse=True)
def _clean_stores() -> None:
    reset_post_store_for_tests()
    reset_graph_store_for_tests()


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
) -> dict:
    return {
        "platform": "telegram",
        "external_id": external_id,
        "timestamp": timestamp,
        "author": {"user_id": user_id, "handle": handle},
        "content": {"raw_text": text, "clean_text": text, "language": language},
        "analytics": {
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
        },
        "engagement": {},
    }


def test_timeline_aggregates_polarity_and_top_emotions() -> None:
    persist_analyzed_post(
        make_post(external_id="1", timestamp="2026-08-24T10:15:00+00:00", polarity="POSITIVE")
    )
    persist_analyzed_post(
        make_post(
            external_id="2",
            timestamp="2026-08-24T10:40:00+00:00",
            polarity="NEGATIVE",
            joy=0.1,
        )
    )
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/analytics/timeline", params={"bucket": "hour"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["buckets"]) == 1
    bucket = body["buckets"][0]
    assert bucket["count"] == 2
    assert bucket["average_sentiment"] == 0.0
    assert bucket["top_emotions"][0]["label"] in {"joy", "anger", "neutral"}


def test_demographics_and_network_from_mentions() -> None:
    persist_analyzed_post(
        make_post(external_id="1", timestamp="2026-08-24T10:00:00+00:00", polarity="POSITIVE")
    )
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    demo = client.get("/api/v1/analytics/demographics").json()
    assert demo["country"][0] == {"key": "IN", "count": 1}
    assert demo["language"][0] == {"key": "en", "count": 1}
    graph = client.get("/api/v1/analytics/network-graph").json()
    assert len(graph["nodes"]) >= 2
    assert len(graph["links"]) >= 1
    assert all("pagerank" in node for node in graph["nodes"])


def test_trending_orders_by_velocity() -> None:
    persist_analyzed_post(
        make_post(
            external_id="1",
            timestamp="2026-08-24T09:00:00+00:00",
            polarity="NEUTRAL",
            topic="elections",
        )
    )
    for i in range(3):
        persist_analyzed_post(
            make_post(
                external_id=f"n{i}",
                timestamp="2026-08-24T10:00:00+00:00",
                polarity="POSITIVE",
                topic="elections",
            )
        )
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    body = client.get("/api/v1/topics/trending").json()
    assert body["topics"][0]["topic_name"] == "elections"
    assert body["topics"][0]["velocity"] == 3.0
    assert body["topics"][0]["sample_size"] == 3
