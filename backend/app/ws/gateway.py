from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.schemas.contracts import WsEnvelope, WsFilterCriteria

logger = logging.getLogger(__name__)

router = APIRouter()

EVENT_NAMES = frozenset(
    {"event:new_post", "event:trend_spike", "event:graph_delta"}
)


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
        if criteria.topic:
            payload_topic = envelope.payload.get("topic_name") or envelope.payload.get(
                "topic"
            )
            if payload_topic and payload_topic != criteria.topic:
                return False
        if criteria.severity:
            payload_severity = envelope.payload.get("severity")
            if payload_severity and payload_severity != criteria.severity:
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


@router.websocket("/ws")
async def websocket_gateway(websocket: WebSocket) -> None:
    await hub.connect(websocket)
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
