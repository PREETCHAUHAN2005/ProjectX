"""Native WebSocket gateway — no Socket.io.

Confirmed event names: event:new_post | event:trend_spike | event:graph_delta
Filter criteria JSON is not fully specified; this accepts a conservative subset.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.contracts import GraphDeltaPayload, NewPostPayload, TrendSpikePayload, WsEnvelope

logger = logging.getLogger(__name__)

router = APIRouter()

REPLAY_LIMIT = 40


def _parse_ts(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _matches_filters(envelope: dict[str, Any], filters: dict[str, Any]) -> bool:
    event = envelope.get("event")
    payload = envelope.get("payload") or {}
    topic = filters.get("topic")
    if topic:
        if event == "event:new_post" and topic not in {
            payload.get("topic_id"),
            payload.get("topic_name"),
        }:
            return False
        if event == "event:trend_spike" and topic not in {
            payload.get("topic_id"),
            payload.get("topic_name"),
        }:
            return False
        if event == "event:graph_delta":
            return False
    severity = filters.get("severity")
    if severity and event == "event:new_post" and payload.get("severity") != severity:
        return False
    window = filters.get("time_window") or {}
    if event == "event:new_post" and (window.get("from") or window.get("to")):
        stamp = _parse_ts(str(payload.get("timestamp") or ""))
        start = _parse_ts(str(window.get("from") or ""))
        end = _parse_ts(str(window.get("to") or ""))
        if start is not None and (stamp is None or stamp < start):
            return False
        if end is not None and (stamp is None or stamp > end):
            return False
    return True


class ConnectionHub:
    def __init__(self) -> None:
        self._clients: dict[WebSocket, dict[str, Any]] = {}
        self._replay: deque[dict[str, Any]] = deque(maxlen=REPLAY_LIMIT)

    @property
    def client_count(self) -> int:
        return len(self._clients)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients[websocket] = {}
        for envelope in list(self._replay):
            if _matches_filters(envelope, self._clients[websocket]):
                await websocket.send_text(json.dumps(envelope))

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.pop(websocket, None)

    def set_filters(self, websocket: WebSocket, filters: dict[str, Any]) -> None:
        if websocket in self._clients:
            self._clients[websocket] = filters

    async def broadcast(self, envelope: dict[str, Any]) -> None:
        self._replay.append(envelope)
        stale: list[WebSocket] = []
        for websocket, filters in self._clients.items():
            if not _matches_filters(envelope, filters):
                continue
            try:
                await websocket.send_text(json.dumps(envelope))
            except Exception:
                logger.exception("websocket send failed")
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)

    def record(self, envelope: dict[str, Any] | WsEnvelope) -> None:
        payload = envelope.model_dump() if isinstance(envelope, WsEnvelope) else envelope
        self._replay.append(payload)

    def reset_for_tests(self) -> None:
        self._clients.clear()
        self._replay.clear()


hub = ConnectionHub()


def _validate_event(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    if event == "event:new_post":
        return NewPostPayload.model_validate(payload).model_dump()
    if event == "event:trend_spike":
        return TrendSpikePayload.model_validate(payload).model_dump()
    if event == "event:graph_delta":
        return GraphDeltaPayload.model_validate(payload).model_dump()
    raise ValueError("unknown event")


async def emit(event: str, payload: dict[str, Any]) -> None:
    validated = _validate_event(event, payload)
    envelope = WsEnvelope(event=event, payload=validated).model_dump()
    await hub.broadcast(envelope)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "invalid json"}))
                continue
            if not isinstance(message, dict) or message.get("type") != "filter":
                await websocket.send_text(json.dumps({"error": "invalid frame"}))
                continue
            hub.set_filters(
                websocket,
                {
                    "topic": message.get("topic"),
                    "time_window": message.get("time_window") or {},
                    "severity": message.get("severity"),
                },
            )
    except WebSocketDisconnect:
        hub.disconnect(websocket)
    except Exception:
        logger.exception("websocket connection failed")
        hub.disconnect(websocket)
