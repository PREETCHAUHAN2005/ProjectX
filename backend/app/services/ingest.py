"""Persist analyzed posts and emit dashboard WebSocket events.

IMPLEMENTATION: broadcasting from persist is not a confirmed product API;
it is required so the live feed works in the local demo without workers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.schemas.contracts import (
    GraphDeltaPayload,
    GraphLink,
    GraphNode,
    NewPostPayload,
    TrendSpikePayload,
    WsEnvelope,
)
from app.stores.graph import get_graph_store
from app.stores.posts import get_post_store

logger = logging.getLogger(__name__)

_emitted_spike_topics: set[str] = set()


def reset_ingest_emit_state() -> None:
    _emitted_spike_topics.clear()


def _is_trend_spike(*, velocity: float, sample_size: int) -> bool:
    """Keep in lockstep with workers.inference.trend_spike.is_trend_spike."""
    return velocity > 2.5 and sample_size > 50


def _parent_author_id(in_reply_to: str | None) -> str | None:
    if not in_reply_to:
        return None
    for row in get_post_store().list_posts():
        if str(row.get("external_id") or "") == in_reply_to:
            return str((row.get("author") or {}).get("user_id") or "") or None
    return None


def document_to_new_post(document: dict[str, Any]) -> NewPostPayload:
    analytics = document.get("analytics") or {}
    sentiment = analytics.get("sentiment") or {}
    author = document.get("author") or {}
    content = document.get("content") or {}
    polarity = sentiment.get("label")
    if polarity not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
        polarity = None
    platform_raw = str(document.get("platform") or "x")
    platform = platform_raw if platform_raw in {"telegram", "x"} else "x"
    return NewPostPayload(
        platform=platform,
        external_id=str(document.get("external_id") or ""),
        timestamp=str(document.get("timestamp") or ""),
        author={
            "user_id": str(author.get("user_id") or ""),
            "handle": str(author.get("handle") or ""),
            "bio": author.get("bio"),
            "follower_count": author.get("follower_count"),
        },
        content={
            "raw_text": str(content.get("raw_text") or ""),
            "hashtags": content.get("hashtags"),
            "language": content.get("language"),
        },
        topic_id=analytics.get("topic_id"),
        topic_name=analytics.get("topic_name"),
        severity=analytics.get("severity"),
        thread_role=analytics.get("thread_role"),
        in_reply_to=analytics.get("in_reply_to"),
        polarity=polarity,
        emotions=analytics.get("emotions") or [],
    )


def persist_to_stores(document: dict[str, Any]) -> tuple[list[GraphNode], list[GraphLink]]:
    store = get_graph_store()
    before_nodes, before_links = store.snapshot()
    analytics = document.get("analytics") or {}
    parent_id = analytics.get("in_reply_to")
    reply_to = _parent_author_id(str(parent_id) if parent_id else None)
    get_post_store().upsert(document)
    store.ingest_post(document, reply_to_user_id=reply_to)
    after_nodes, after_links = store.snapshot()
    known_nodes = {node.id for node in before_nodes}
    known_links = {(link.source, link.target, link.type) for link in before_links}
    new_nodes = [node for node in after_nodes if node.id not in known_nodes]
    new_links = [
        link
        for link in after_links
        if (link.source, link.target, link.type) not in known_links
    ]
    return new_nodes, new_links


def persist_analyzed_post(document: dict[str, Any]) -> None:
    new_nodes, new_links = persist_to_stores(document)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(emit_persist_events(document, new_nodes, new_links))


async def persist_and_emit(document: dict[str, Any]) -> None:
    new_nodes, new_links = persist_to_stores(document)
    await emit_persist_events(document, new_nodes, new_links)


async def emit_persist_events(
    document: dict[str, Any],
    new_nodes: list[GraphNode],
    new_links: list[GraphLink],
) -> None:
    from app.services.analytics import AnalyticsService
    from app.ws.gateway import hub

    payload = document_to_new_post(document)
    await hub.broadcast(
        WsEnvelope(event="event:new_post", payload=payload.model_dump(exclude_none=True))
    )
    if new_nodes or new_links:
        delta = GraphDeltaPayload(nodes=new_nodes, links=new_links)
        await hub.broadcast(
            WsEnvelope(event="event:graph_delta", payload=delta.model_dump())
        )
    trending = AnalyticsService().trending(limit=8)
    for topic in trending.topics:
        if not _is_trend_spike(velocity=topic.velocity, sample_size=topic.sample_size):
            continue
        if topic.topic_id in _emitted_spike_topics:
            continue
        _emitted_spike_topics.add(topic.topic_id)
        spike = TrendSpikePayload(
            topic_id=topic.topic_id,
            topic_name=topic.topic_name,
            velocity=topic.velocity,
            sample_size=topic.sample_size,
        )
        await hub.broadcast(WsEnvelope(event="event:trend_spike", payload=spike.model_dump()))
        break
