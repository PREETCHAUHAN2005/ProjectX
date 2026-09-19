from fastapi.testclient import TestClient

from app.main import app


def test_nlp_predict_returns_28d_and_polarity() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/nlp/predict",
        json={"text": "Fear after the flood and a malware phishing attack in Delhi."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["polarity"] == "NEGATIVE"
    assert len(body["emotions"]) == 28
    assert body["emotions"][0]["label"] == "fear"


def test_ingest_replay_populates_feed_and_timeline() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/ingest/run", json={"limit": 4, "query": "India"})
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] >= 1
    assert body["source"] == "replay"
    feed = client.get("/api/v1/feed/recent").json()
    assert len(feed["posts"]) >= 1
    post = feed["posts"][0]
    assert post["platform"] in {"x", "telegram"}
    assert post["analytics"]["sentiment"]["label"] in {"POSITIVE", "NEGATIVE", "NEUTRAL"}
    timeline = client.get("/api/v1/analytics/timeline").json()
    assert len(timeline["buckets"]) >= 1


def test_ingest_broadcasts_websocket_event() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        response = client.post("/api/v1/ingest/run", json={"limit": 1})
        assert response.status_code == 200
        assert response.json()["accepted"] >= 1
        message = websocket.receive_json()
        assert message["event"] in {
            "event:new_post",
            "event:graph_delta",
            "event:trend_spike",
        }
