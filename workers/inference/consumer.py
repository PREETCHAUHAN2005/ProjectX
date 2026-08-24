"""Consume stream:social:raw, infer, and hand documents to persistence callbacks."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.redis_stream import consume_raw_payload
from workers.inference.document import PostDocument
from workers.inference.pipeline import InferencePipeline

logger = logging.getLogger(__name__)

PersistFn = Callable[[PostDocument], Awaitable[None] | None]


async def handle_stream_fields(
    fields: dict[str, str],
    pipeline: InferencePipeline,
    persist: PersistFn,
) -> PostDocument | None:
    payload = await consume_raw_payload(fields)
    if payload is None:
        return None
    raw = normalize_raw_post(payload)
    if raw is None:
        return None
    document = pipeline.analyze(raw)
    if document is None:
        return None
    result = persist(document)
    if isinstance(result, Awaitable):
        await result
    return document


async def consume_stream_batch(
    messages: list[tuple[str, dict[str, Any]]],
    pipeline: InferencePipeline,
    persist: PersistFn,
) -> list[PostDocument]:
    """messages: [(id, fields), ...] from Redis XREAD (implementation)."""
    stored: list[PostDocument] = []
    for message_id, fields in messages:
        try:
            coerced = {str(k): str(v) for k, v in fields.items()}
            document = await handle_stream_fields(coerced, pipeline, persist)
            if document is not None:
                stored.append(document)
        except Exception:
            logger.exception("Failed consuming Redis message id=%s", message_id)
    return stored
