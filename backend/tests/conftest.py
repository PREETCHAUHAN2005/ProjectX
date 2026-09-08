import os

os.environ["DEMO_SEED"] = "false"

import pytest

from app.services.demo_seed import reset_demo_seed_state
from app.services.ingest import persist_analyzed_post, reset_ingest_emit_state
from app.stores.graph import reset_graph_store_for_tests
from app.stores.posts import reset_post_store_for_tests
from tests.factories import make_post


@pytest.fixture(autouse=True)
def _clean_stores() -> None:
    reset_post_store_for_tests()
    reset_graph_store_for_tests()
    reset_demo_seed_state()
    reset_ingest_emit_state()


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
