from fastapi.testclient import TestClient

from app.main import app
from app.schemas.contracts import WsEnvelope
from app.ws.gateway import hub


def test_websocket_accepts_connection_and_ignores_malformed() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("not-json")
        websocket.send_json({"type": "filter", "topic": "elections", "severity": "high"})
        websocket.send_json({"nope": True})


def test_websocket_broadcast_new_post() -> None:
    client = TestClient(app)
    envelope = WsEnvelope(
        event="event:new_post",
        payload={
            "platform": "telegram",
            "external_id": "1",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "n"},
            "content": {"raw_text": "hello"},
        },
    )
    with client.websocket_connect("/ws") as websocket:
        import anyio

        anyio.from_thread.run(hub.broadcast, envelope)
        message = websocket.receive_json()
        assert message["event"] == "event:new_post"
        assert message["payload"]["external_id"] == "1"


def test_trend_spike_event_payload() -> None:
    envelope = WsEnvelope(
        event="event:trend_spike",
        payload={
            "topic_id": "t1",
            "topic_name": "elections",
            "velocity": 2.51,
            "sample_size": 51,
        },
    )
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        import anyio

        anyio.from_thread.run(hub.broadcast, envelope)
        message = websocket.receive_json()
        assert message["event"] == "event:trend_spike"
