from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.schemas.contracts import WsEnvelope, WsFilterCriteria

logger = logging.getLogger(__name__)

router = APIRouter()

EVENT_NAMES = frozenset(
    {"event:new_post", "event:trend_spike", "event:graph_delta"}
)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class ConnectionHub:
    def __init__(self) -> None:
        self._clients: dict[WebSocket, WsFilterCriteria] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients[websocket] = WsFilterCriteria(type="filter")

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.pop(websocket, None)

    def set_filter(self, websocket: WebSocket, criteria: WsFilterCriteria) -> None:
        self._clients[websocket] = criteria

    def _matches(self, criteria: WsFilterCriteria, envelope: WsEnvelope) -> bool:
        payload = envelope.payload
        if criteria.topic:
            payload_topic = payload.get("topic_name") or payload.get("topic")
            if payload_topic and payload_topic != criteria.topic:
                return False
        if criteria.severity:
            payload_severity = payload.get("severity")
            if payload_severity and payload_severity != criteria.severity:
                return False
        window = criteria.time_window or {}
        start = _parse_ts(window.get("from") if isinstance(window, dict) else None)
        end = _parse_ts(window.get("to") if isinstance(window, dict) else None)
        if start or end:
            stamp = _parse_ts(str(payload.get("timestamp") or ""))
            if stamp is not None:
                if start and stamp < start:
                    return False
                if end and stamp > end:
                    return False
        return True

    async def broadcast(self, envelope: WsEnvelope) -> None:
        stale: list[WebSocket] = []
        body = envelope.model_dump()
        for websocket, criteria in self._clients.items():
            if not self._matches(criteria, envelope):
                continue
            try:
                await websocket.send_json(body)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)


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
    comment_budget = max(0, 40 - len(roots))
    selected = [*roots, *comments[-comment_budget:]]
    selected.sort(key=lambda row: str(row.get("timestamp") or ""))
    for document in selected:
        try:
            payload = document_to_new_post(document).model_dump(exclude_none=True)
            await websocket.send_json({"event": "event:new_post", "payload": payload})
        except Exception:
            logger.exception("Failed replaying seeded post on WebSocket connect")


@router.websocket("/ws")
async def websocket_gateway(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    # Yield so the browser/Vite proxy attaches onmessage before catch-up frames.
    await asyncio.sleep(0.25)
    await _replay_recent(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data: Any = json.loads(raw)
                criteria = WsFilterCriteria.model_validate(data)
                hub.set_filter(websocket, criteria)
            except (json.JSONDecodeError, ValidationError):
                logger.warning("Ignoring malformed WebSocket client frame")
                continue
    except WebSocketDisconnect:
        hub.disconnect(websocket)
