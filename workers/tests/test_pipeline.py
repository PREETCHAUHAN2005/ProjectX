from workers.ingestion.normalize import normalize_raw_post
from workers.inference.go_emotions import StaticEmotionInferencer, vector_with_dominant
from workers.inference.pipeline import InferencePipeline
from workers.inference.topics import TopicAssignment


class StubTopics:
    def assign(self, text: str) -> TopicAssignment | None:
        _ = text
        return TopicAssignment("t1", "elections")


def _raw(text: str):
    return normalize_raw_post(
        {
            "platform": "telegram",
            "external_id": "99",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "news"},
            "content": {"raw_text": text},
        }
    )


def test_pipeline_joy_persists_28d_and_positive() -> None:
    raw = _raw("great news today")
    assert raw is not None
    pipeline = InferencePipeline(
        inferencer=StaticEmotionInferencer(vector_with_dominant("joy")),
        topic_clusterer=StubTopics(),  # type: ignore[arg-type]
    )
    document = pipeline.analyze(raw)
    assert document is not None
    assert document.analytics.sentiment.label == "POSITIVE"
    assert len(document.analytics.emotions) == 28
    assert document.content.clean_text
    assert document.analytics.topic_name == "elections"


def test_pipeline_empty_text_does_not_fake_emotions() -> None:
    raw = _raw("   https://example.com  ")
    assert raw is not None
    pipeline = InferencePipeline(
        inferencer=StaticEmotionInferencer(vector_with_dominant("joy")),
    )
    assert pipeline.analyze(raw) is None


class BoomInferencer:
    def infer(self, text: str):
        _ = text
        raise RuntimeError("model down")


def test_pipeline_inference_failure_does_not_persist() -> None:
    raw = _raw("still some text")
    assert raw is not None
    pipeline = InferencePipeline(inferencer=BoomInferencer())  # type: ignore[arg-type]
    assert pipeline.analyze(raw) is None
