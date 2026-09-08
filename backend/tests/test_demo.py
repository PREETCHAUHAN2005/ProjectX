from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_seed import load_demo_seed
from app.services.ingest import persist_and_emit, persist_to_stores
from app.stores.graph import get_graph_store
from tests.factories import make_post


def test_demo_seed_fills_readable_analytics() -> None:
    load_demo_seed(persist=lambda document: persist_to_stores(document))
    client = TestClient(app)
    timeline = client.get("/api/v1/analytics/timeline", params={"bucket": "hour"}).json()
    assert timeline["buckets"]
    posts = sum(bucket["post_count"] for bucket in timeline["buckets"])
    comments = sum(bucket["comment_count"] for bucket in timeline["buckets"])
    assert posts >= 2
    assert comments > posts
    graph = client.get("/api/v1/analytics/network-graph").json()
    handles = {node["handle"] for node in graph["nodes"]}
    assert "IndiaMetDept" in handles
    assert "PriyaKamble" in handles
    assert all(not node["handle"].startswith("u") or len(node["handle"]) > 2 for node in graph["nodes"])
    assert any(node["community"] in {"fear", "approval", "anger", "relief"} for node in graph["nodes"])
    demo = client.get("/api/v1/analytics/demographics").json()
    assert demo["country"]
    assert demo["profession"]
    trending = client.get("/api/v1/topics/trending").json()
    names = {topic["topic_name"] for topic in trending["topics"]}
    assert "flood relief" in names


def test_timeline_splits_posts_and_comments() -> None:
    persist_to_stores(
        make_post(
            external_id="root",
            timestamp="2026-08-24T10:00:00+00:00",
            polarity="NEGATIVE",
            thread_role="post",
        )
    )
    persist_to_stores(
        make_post(
            external_id="c1",
            timestamp="2026-08-24T10:20:00+00:00",
            polarity="POSITIVE",
            thread_role="comment",
            in_reply_to="root",
            handle="bob",
            user_id="u2",
            text="thanks @alice",
        )
    )
    client = TestClient(app)
    bucket = client.get("/api/v1/analytics/timeline", params={"bucket": "hour"}).json()["buckets"][0]
    assert bucket["count"] == 2
    assert bucket["post_count"] == 1
    assert bucket["comment_count"] == 1


def test_severity_filters_timeline() -> None:
    persist_to_stores(
        make_post(
            external_id="a",
            timestamp="2026-08-24T10:00:00+00:00",
            polarity="NEGATIVE",
            severity="high",
        )
    )
    persist_to_stores(
        make_post(
            external_id="b",
            timestamp="2026-08-24T10:10:00+00:00",
            polarity="POSITIVE",
            severity="low",
        )
    )
    client = TestClient(app)
    body = client.get(
        "/api/v1/analytics/timeline", params={"bucket": "hour", "severity": "high"}
    ).json()
    assert body["buckets"][0]["count"] == 1


def test_graph_reply_edge_and_emotion_community() -> None:
    persist_to_stores(
        make_post(
            external_id="root",
            timestamp="2026-08-24T10:00:00+00:00",
            polarity="NEGATIVE",
            thread_role="post",
            text="alert from the desk",
        )
    )
    persist_to_stores(
        make_post(
            external_id="c1",
            timestamp="2026-08-24T10:05:00+00:00",
            polarity="POSITIVE",
            thread_role="comment",
            in_reply_to="root",
            handle="bob",
            user_id="u2",
            text="on our way",
            joy=0.9,
        )
    )
    nodes, links = get_graph_store().snapshot()
    handles = {node.handle: node for node in nodes}
    assert "alice" in handles
    assert "bob" in handles
    assert handles["alice"].community == "joy"
    assert any(link.type == "reply" for link in links)


def test_websocket_replays_seeded_posts() -> None:
    persist_to_stores(
        make_post(external_id="1", timestamp="2026-08-24T00:00:00+00:00", polarity="POSITIVE")
    )
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            message = websocket.receive_json()
            assert message["event"] == "event:new_post"
            assert message["payload"]["external_id"] == "1"
            assert message["payload"]["author"]["handle"] == "alice"


def test_persist_emits_new_post_on_websocket() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            assert client.portal is not None
            client.portal.call(
                persist_and_emit,
                make_post(
                    external_id="live-1",
                    timestamp="2026-08-24T00:00:00+00:00",
                    polarity="NEGATIVE",
                ),
            )
            message = websocket.receive_json()
            assert message["event"] == "event:new_post"
            assert message["payload"]["external_id"] == "live-1"
