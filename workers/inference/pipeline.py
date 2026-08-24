"""Raw post → preprocess → GoEmotions → polarity → topic → NER.

Empty or whitespace text is skipped. Inference failures do not invent scores.
"""

from __future__ import annotations

import logging
import re

from workers.ingestion.raw_post import RawPost
from workers.inference.document import (
    Analytics,
    Author,
    Content,
    Demographics,
    Emotion,
    Engagement,
    PostDocument,
    Sentiment,
)
from workers.inference.go_emotions import EmotionInferencer, InferenceError
from workers.inference.ner import DemographicProfiler, UnavailableNerProfiler
from workers.inference.polarity import GO_EMOTIONS_LABELS, polarity_from_emotions
from workers.inference.preprocess import preprocess, tokenizer_from_optional, truncate_for_model
from workers.inference.topics import TopicClusterer, UnavailableTopicClusterer

logger = logging.getLogger(__name__)

HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)")


class InferencePipeline:
    def __init__(
        self,
        inferencer: EmotionInferencer,
        topic_clusterer: TopicClusterer | None = None,
        ner_profiler: DemographicProfiler | None = None,
        tokenizer: object | None = None,
    ) -> None:
        self._inferencer = inferencer
        self._topics = topic_clusterer or UnavailableTopicClusterer()
        self._ner = ner_profiler or UnavailableNerProfiler()
        self._tokenizer = tokenizer_from_optional(tokenizer)

    def analyze(self, post: RawPost) -> PostDocument | None:
        clean = preprocess(post.content.raw_text)
        if not clean:
            logger.warning(
                "Skipping post with empty text after preprocess platform=%s id=%s",
                post.platform,
                post.external_id,
            )
            return None

        truncated = truncate_for_model(clean, self._tokenizer)
        try:
            emotions = self._inferencer.infer(truncated)
        except InferenceError:
            logger.exception("Emotion inference failed; not persisting fake scores")
            return None
        except Exception:
            logger.exception("Unexpected inference failure")
            return None

        if len(emotions) != len(GO_EMOTIONS_LABELS):
            logger.warning("Rejecting emotion vector that is not 28-dimensional")
            return None

        try:
            polarity, score = polarity_from_emotions(emotions)
        except ValueError:
            logger.warning("Polarity mapping failed")
            return None

        topic = self._topics.assign(truncated)
        demo = self._ner.profile(truncated)
        hashtags = post.content.hashtags
        if not hashtags:
            found = HASHTAG_RE.findall(post.content.raw_text)
            hashtags = found or None

        return PostDocument(
            platform=post.platform,
            external_id=post.external_id,
            timestamp=post.timestamp,
            author=Author(
                user_id=post.author.user_id,
                handle=post.author.handle,
                bio=post.author.bio,
                follower_count=post.author.follower_count,
            ),
            content=Content(
                raw_text=post.content.raw_text,
                clean_text=truncated,
                hashtags=hashtags,
                language=post.content.language,
            ),
            analytics=Analytics(
                sentiment=Sentiment(label=polarity, score=score),
                emotions=[Emotion(label=item.label, score=item.score) for item in emotions],
                topic_id=topic.topic_id if topic else None,
                topic_name=topic.topic_name if topic else None,
                demographics=(
                    Demographics(
                        inferred_country=demo.inferred_country,
                        inferred_region=demo.inferred_region,
                        inferred_profession=demo.inferred_profession,
                        confidence=demo.confidence,
                    )
                    if demo
                    else None
                ),
            ),
            engagement=Engagement(
                likes=post.engagement.likes,
                shares=post.engagement.shares,
                views=post.engagement.views,
            ),
        )
