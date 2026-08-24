from __future__ import annotations

import json
import logging

from redis.asyncio import Redis

from workers.ingestion.raw_post import RawPost

logger = logging.getLogger(__name__)

STREAM_SOCIAL_RAW = "stream:social:raw"


class RedisStreamPublisher:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def publish_raw_post(self, post: RawPost) -> str:
        payload = post.model_dump()
        message_id = await self._redis.xadd(
            STREAM_SOCIAL_RAW,
            {
                "payload": json.dumps(payload, separators=(",", ":")),
                "platform": post.platform,
                "timestamp": post.timestamp,
            },
        )
        return str(message_id)


async def consume_raw_payload(fields: dict[str, str]) -> dict | None:
    raw = fields.get("payload")
    if not raw:
        logger.warning("Skipping Redis message without payload")
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Skipping malformed Redis payload")
        return None
    if not isinstance(parsed, dict):
        logger.warning("Skipping non-object Redis payload")
        return None
    return parsed
