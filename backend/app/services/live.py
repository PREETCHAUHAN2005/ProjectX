"""In-process ingest → inference → persist → WebSocket (local demo runtime).

Preserves the product flow. Redis/Mongo/Neo4j remain optional; this path
keeps a laptop demo live when those stores are not running.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from app.core.config import settings
from app.core.paths import ensure_repo_on_path
from app.schemas.contracts import WsEnvelope
from app.services.analytics import AnalyticsService
from app.services.ingest import persist_to_stores
from app.stores.graph import get_graph_store
from app.stores.posts import get_post_store
from app.ws.gateway import hub

ensure_repo_on_path()

from workers.ingestion.demo_corpus import live_raw_post, seed_raw_posts
from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.raw_post import RawPost
from workers.ingestion.x_adapter import build_x_adapter
from workers.inference.document import PostDocument
from workers.inference.pipeline import build_pipeline
from workers.inference.polarity import polarity_from_emotions
from workers.inference.preprocess import preprocess, truncate_for_model
from workers.inference.trend_spike import is_trend_spike

logger = logging.getLogger(__name__)

_HIGH_NEGATIVE = frozenset({"fear", "anger", "disgust"})


def _severity(document: PostDocument) -> str:
    label = document.analytics.sentiment.label
    if label != "NEGATIVE":
        return "low" if label == "POSITIVE" else "medium"
    top = max(document.analytics.emotions, key=lambda item: item.score)
    if top.label in _HIGH_NEGATIVE:
        return "critical"
    return "high"


def feed_payload(document: PostDocument) -> dict[str, Any]:
    dumped = document.to_mongo_dict()
    top = sorted(document.analytics.emotions, key=lambda item: item.score, reverse=True)[:3]
    topic_name = document.analytics.topic_name
    return {
        "platform": document.platform,
        "external_id": document.external_id,
        "timestamp": document.timestamp,
        "author": dumped["author"],
        "content": {
            "raw_text": document.content.raw_text,
            "hashtags": document.content.hashtags,
            "language": document.content.language,
        },
        "topic_id": document.analytics.topic_id,
        "topic_name": topic_name,
        "severity": _severity(document),
        "thread_role": dumped.get("analytics", {}).get("thread_role") or "post",
        "in_reply_to": dumped.get("analytics", {}).get("in_reply_to"),
        "polarity": document.analytics.sentiment.label,
        "emotions": [item.model_dump() for item in top],
        "analytics": {
            "sentiment": dumped["analytics"]["sentiment"],
            "emotions": [item.model_dump() for item in top],
            "topic_id": document.analytics.topic_id,
            "topic_name": topic_name,
            "severity": _severity(document),
        },
    }


def graph_delta_payload(document: PostDocument) -> dict[str, Any]:
    nodes, links = get_graph_store().snapshot()
    author_id = document.author.user_id
    related = [
        link for link in links if link.source == author_id or link.target == author_id
    ]
    ids = {author_id}
    for link in related:
        ids.add(link.source)
        ids.add(link.target)
    return {
        "nodes": [node.model_dump() for node in nodes if node.id in ids],
        "links": [link.model_dump() for link in related],
    }


def sanitize_query(raw: str | None) -> str:
    text = (raw or settings.x_query or "India").strip()[:120]
    lowered = text.lower()
    if "http://" in lowered or "https://" in lowered:
        return settings.x_query or "India"
    return text or "India"


class LiveRuntime:
    def __init__(self) -> None:
        self.pipeline = build_pipeline(emotion_backend=settings.emotion_backend)
        self.ingest_source = "idle"
        self._tick = 0
        self._fired_spikes: set[str] = set()
        self._lock = asyncio.Lock()
        self._last_fetch_at = 0.0
        self._analytics = AnalyticsService()

    async def ingest_raw_dict(self, data: dict[str, Any], *, emit: bool = True) -> bool:
        raw = normalize_raw_post(data)
        if raw is None:
            return False
        return await self.ingest_raw(raw, emit=emit)

    async def ingest_raw(self, raw: RawPost, *, emit: bool = True) -> bool:
        async with self._lock:
            document = self.pipeline.analyze(raw)
            if document is None:
                return False
            mongo = document.to_mongo_dict()
            analytics = mongo.setdefault("analytics", {})
            analytics["severity"] = _severity(document)
            persist_to_stores(mongo)
            if emit:
                payload = feed_payload(document)
                await hub.broadcast(WsEnvelope(event="event:new_post", payload=payload))
                delta = graph_delta_payload(document)
                if delta["nodes"]:
                    await hub.broadcast(WsEnvelope(event="event:graph_delta", payload=delta))
            await self._maybe_spike(document)
            return True

    async def _maybe_spike(self, document: PostDocument) -> None:
        topic_id = document.analytics.topic_id or document.analytics.topic_name
        topic_name = document.analytics.topic_name or topic_id
        if not topic_id:
            return
        trending = self._analytics.trending(100)
        for topic in trending.topics:
            if topic.topic_id != topic_id and topic.topic_name != topic_name:
                continue
            if not is_trend_spike(velocity=topic.velocity, sample_size=topic.sample_size):
                continue
            key = str(topic.topic_id)
            if key in self._fired_spikes:
                return
            self._fired_spikes.add(key)
            await hub.broadcast(
                WsEnvelope(
                    event="event:trend_spike",
                    payload={
                        "topic_id": topic.topic_id,
                        "topic_name": topic.topic_name,
                        "velocity": topic.velocity,
                        "sample_size": topic.sample_size,
                    },
                )
            )
            return

    async def seed_if_empty(self) -> int:
        if get_post_store().count() > 0:
            return 0
        accepted = 0
        for row in seed_raw_posts():
            if await self.ingest_raw_dict(row, emit=False):
                accepted += 1
        self.ingest_source = "replay"
        logger.info("Demo seed ingested %s analyzed posts", accepted)
        return accepted

    async def _replay_batch(self, limit: int) -> int:
        accepted = 0
        for _ in range(limit):
            self._tick += 1
            if await self.ingest_raw_dict(live_raw_post(self._tick)):
                accepted += 1
        self.ingest_source = "replay"
        return accepted

    async def fetch_posts(self, *, query: str | None, limit: int) -> tuple[int, str]:
        now = time.monotonic()
        if now - self._last_fetch_at < 8:
            return 0, self.ingest_source
        self._last_fetch_at = now
        cleaned = sanitize_query(query)
        if settings.demo_ingest == "replay":
            return await self._replay_batch(limit), "replay"

        adapter = build_x_adapter(
            settings.x_ingestion_backend,
            bearer_token=settings.x_bearer_token or None,
            query=cleaned,
        )
        accepted = 0
        try:
            async for post in adapter.fetch_posts(query=cleaned, limit=limit):
                if await self.ingest_raw(post):
                    accepted += 1
        except Exception:
            logger.exception("X fetch failed")
        if accepted == 0:
            accepted = await self._replay_batch(limit)
            return accepted, "replay"
        self.ingest_source = adapter.backend
        return accepted, adapter.backend

    async def emit_one(self) -> None:
        self._tick += 1
        await self.ingest_raw_dict(live_raw_post(self._tick))

    async def run_loop(self) -> None:
        interval = max(1.5, float(settings.demo_interval_seconds))
        await asyncio.sleep(1.5)
        while True:
            try:
                await self.emit_one()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Live ingest loop failed")
            await asyncio.sleep(interval)

    def predict_text(self, text: str) -> dict[str, Any]:
        clean = truncate_for_model(preprocess(text), None)
        if not clean:
            return {
                "emotions": [],
                "polarity": "NEUTRAL",
                "backend": settings.emotion_backend,
            }
        emotions = self.pipeline._inferencer.infer(clean)
        polarity, _score = polarity_from_emotions(emotions)
        ranked = sorted(emotions, key=lambda item: item.score, reverse=True)
        return {
            "emotions": [item.as_dict() for item in ranked],
            "polarity": polarity,
            "backend": settings.emotion_backend,
        }


_runtime: LiveRuntime | None = None


def get_runtime() -> LiveRuntime:
    global _runtime
    if _runtime is None:
        _runtime = LiveRuntime()
    return _runtime


def recent_feed_payloads(limit: int) -> list[dict[str, Any]]:
    rows = get_post_store().list_recent(limit)
    posts: list[dict[str, Any]] = []
    for row in rows:
        try:
            document = PostDocument.model_validate(row)
        except Exception:
            continue
        posts.append(feed_payload(document))
    return posts


def reset_runtime_for_tests() -> None:
    global _runtime
    _runtime = None
