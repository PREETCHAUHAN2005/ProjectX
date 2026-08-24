"""In-memory and optional Mongo persistence for confirmed `posts` documents.

Duplicate strategy (implementation): upsert on (platform, external_id).
Indexes are an open decision and are not created here as a product contract.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


class PostStore(Protocol):
    def upsert(self, document: dict[str, Any]) -> None: ...

    def list_posts(
        self,
        *,
        topic: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
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
    ) -> list[dict[str, Any]]:
        rows = list(self._docs.values())
        if topic:
            rows = [
                row
                for row in rows
                if topic
                in {
                    (row.get("analytics") or {}).get("topic_id"),
                    (row.get("analytics") or {}).get("topic_name"),
                }
            ]
        if from_ts:
            rows = [row for row in rows if str(row.get("timestamp") or "") >= from_ts]
        if to_ts:
            rows = [row for row in rows if str(row.get("timestamp") or "") <= to_ts]
        return rows

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
        return list(self._col().find(query, {"_id": 0}))


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
