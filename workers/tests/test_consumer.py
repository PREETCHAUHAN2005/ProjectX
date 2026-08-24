import json

import pytest

from workers.ingestion.normalize import normalize_raw_post
from workers.inference.consumer import consume_stream_batch
from workers.inference.go_emotions import StaticEmotionInferencer, vector_with_dominant
from workers.inference.pipeline import InferencePipeline


@pytest.mark.asyncio
async def test_consumer_persists_valid_and_skips_malformed() -> None:
    stored: list[object] = []
    pipeline = InferencePipeline(
        inferencer=StaticEmotionInferencer(vector_with_dominant("joy")),
    )
    raw = normalize_raw_post(
        {
            "platform": "x",
            "external_id": "88",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "n"},
            "content": {"raw_text": "hello world"},
        }
    )
    assert raw is not None
    messages = [
        ("1-0", {"payload": "not-json"}),
        ("1-1", {"payload": json.dumps(raw.model_dump())}),
    ]
    result = await consume_stream_batch(messages, pipeline, stored.append)
    assert len(result) == 1
    assert result[0].external_id == "88"
    assert len(stored) == 1
