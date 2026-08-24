import json
from typing import Any

import pytest

from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.redis_stream import STREAM_SOCIAL_RAW, RedisStreamPublisher, consume_raw_payload


class FakeRedis:
    def __init__(self) -> None:
        self.added: list[tuple[str, dict[str, str]]] = []

    async def xadd(self, stream: str, fields: dict[str, str]) -> str:
        self.added.append((stream, fields))
        return "1-0"


@pytest.mark.asyncio
async def test_publish_raw_post() -> None:
    post = normalize_raw_post(
        {
            "platform": "telegram",
            "external_id": "7",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "n"},
            "content": {"raw_text": "hi"},
        }
    )
    assert post is not None
    redis = FakeRedis()
    publisher = RedisStreamPublisher(redis)  # type: ignore[arg-type]
    message_id = await publisher.publish_raw_post(post)
    assert message_id == "1-0"
    stream, fields = redis.added[0]
    assert stream == STREAM_SOCIAL_RAW
    payload = json.loads(fields["payload"])
    assert payload["external_id"] == "7"
    assert fields["platform"] == "telegram"


@pytest.mark.asyncio
async def test_consume_skips_malformed() -> None:
    assert await consume_raw_payload({}) is None
    assert await consume_raw_payload({"payload": "not-json"}) is None
    parsed = await consume_raw_payload({"payload": '{"platform":"x"}'})
    assert parsed == {"platform": "x"}
