"""In-memory and optional Mongo persistence for confirmed `posts` documents.

Duplicate strategy (implementation): upsert on (platform, external_id).
Indexes are an open decision and are not created here as a product contract.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


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


def _matches_filters(
    row: dict[str, Any],
    *,
    topic: str | None,
    from_ts: str | None,
    to_ts: str | None,
    severity: str | None,
) -> bool:
    analytics = row.get("analytics") or {}
    if topic:
        if topic not in {analytics.get("topic_id"), analytics.get("topic_name")}:
            return False
    if severity:
        if str(analytics.get("severity") or "") != severity:
            return False
    stamp = _parse_ts(str(row.get("timestamp") or ""))
    if from_ts:
        start = _parse_ts(from_ts)
        if start is not None and (stamp is None or stamp < start):
            return False
    if to_ts:
        end = _parse_ts(to_ts)
        if end is not None and (stamp is None or stamp > end):
            return False
    return True


class PostStore(Protocol):
    def upsert(self, document: dict[str, Any]) -> None: ...

    def list_posts(
        self,
        *,
        topic: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]: ...


class MemoryPostStore:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str], dict[str, Any]] = {}

    def upsert(self, document: dict[str, Any]) -> None:
        platform = str(document.get("platform") or "")
        external_id = str(document.get("external_id") or "")
        if not platform or not external_id:
            raise ValueError("platform and external_id are required")
        self._docs[(platform, external_id)] = dict(document)

    def list_posts(
        self,
        *,
        topic: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self._docs.values()
            if _matches_filters(
                row,
                topic=topic,
                from_ts=from_ts,
                to_ts=to_ts,
                severity=severity,
            )
        ]
        rows.sort(key=lambda row: str(row.get("timestamp") or ""))
        return rows

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = list(self._docs.values())
        rows.sort(key=lambda row: str(row.get("timestamp") or ""), reverse=True)
        return rows[: max(0, limit)]

    def count(self) -> int:
        return len(self._docs)

    def clear(self) -> None:
        self._docs.clear()


class MongoPostStore:
    def __init__(self, uri: str) -> None:
        self._uri = uri
        self._collection = None

    def _col(self):
        if self._collection is not None:
            return self._collection
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise RuntimeError("pymongo is not installed") from exc
        client = MongoClient(self._uri, serverSelectionTimeoutMS=2000)
        self._collection = client.get_default_database().get_collection("posts")
        return self._collection

    def upsert(self, document: dict[str, Any]) -> None:
        col = self._col()
        col.update_one(
            {
                "platform": document["platform"],
                "external_id": document["external_id"],
            },
            {"$set": document},
            upsert=True,
        )

    def list_posts(
        self,
        *,
        topic: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if topic:
            query["$or"] = [
                {"analytics.topic_id": topic},
                {"analytics.topic_name": topic},
            ]
        ts_filter: dict[str, str] = {}
        if from_ts:
            ts_filter["$gte"] = from_ts
        if to_ts:
            ts_filter["$lte"] = to_ts
        if ts_filter:
            query["timestamp"] = ts_filter
        if severity:
            query["analytics.severity"] = severity
        rows = list(self._col().find(query, {"_id": 0}))
        return [
            row
            for row in rows
            if _matches_filters(
                row,
                topic=topic,
                from_ts=from_ts,
                to_ts=to_ts,
                severity=severity,
            )
        ]

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(
            self._col().find({}, {"_id": 0}).sort("timestamp", -1).limit(max(0, limit))
        )

    def count(self) -> int:
        return int(self._col().count_documents({}))


_store: MemoryPostStore | MongoPostStore | None = None


def get_post_store() -> MemoryPostStore | MongoPostStore:
    global _store
    if _store is not None:
        return _store
    if settings.mongodb_uri:
        try:
            _store = MongoPostStore(settings.mongodb_uri)
            return _store
        except Exception:
            logger.exception("MongoDB unavailable; using in-memory post store")
    _store = MemoryPostStore()
    return _store


def reset_post_store_for_tests() -> MemoryPostStore:
    global _store
    _store = MemoryPostStore()
    return _store
