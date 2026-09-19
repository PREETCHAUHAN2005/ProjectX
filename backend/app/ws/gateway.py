"""Native WebSocket gateway — no Socket.io.

Confirmed event names: event:new_post | event:trend_spike | event:graph_delta
Filter criteria JSON is not fully specified; this accepts a conservative subset.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
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


def _as_envelope_dict(envelope: dict[str, Any] | WsEnvelope) -> dict[str, Any]:
    if isinstance(envelope, WsEnvelope):
        return envelope.model_dump()
    return envelope


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

    @property
    def client_count(self) -> int:
        return len(self._clients)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients[websocket] = {}

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.pop(websocket, None)

    def set_filters(self, websocket: WebSocket, filters: dict[str, Any]) -> None:
        if websocket in self._clients:
            self._clients[websocket] = filters

    async def broadcast(self, envelope: dict[str, Any] | WsEnvelope) -> None:
        envelope = _as_envelope_dict(envelope)
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

    def reset_for_tests(self) -> None:
        self._clients.clear()


hub = ConnectionHub()


async def _replay_recent(websocket: WebSocket) -> None:
    from app.services.ingest import document_to_new_post
    from app.stores.posts import get_post_store

    posts = get_post_store().list_posts()
    roots = [
        row
        for row in posts
        if str((row.get("analytics") or {}).get("thread_role") or "post") != "comment"
    ]
    comments = [
        row
        for row in posts
        if str((row.get("analytics") or {}).get("thread_role") or "post") == "comment"
    ]
    comment_budget = max(0, REPLAY_LIMIT - len(roots))
    selected = [*roots, *comments[-comment_budget:]]
    selected.sort(key=lambda row: str(row.get("timestamp") or ""))
    filters = hub._clients.get(websocket) or {}
    for document in selected:
        try:
            payload = document_to_new_post(document).model_dump(exclude_none=True)
            envelope = {"event": "event:new_post", "payload": payload}
            if _matches_filters(envelope, filters):
                await websocket.send_text(json.dumps(envelope))
        except Exception:
            logger.exception("Failed replaying seeded post on WebSocket connect")


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
    if settings.app_env != "test":
        await asyncio.sleep(0.25)
    await _replay_recent(websocket)
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
