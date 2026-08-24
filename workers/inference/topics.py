"""BERTopic clustering adapter.

BERTopic is used when the package is installed and a model has been fitted.
If unavailable, topic fields stay unset — do not invent topic names.
"""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class TopicAssignment:
    __slots__ = ("topic_id", "topic_name")

    def __init__(self, topic_id: str | None, topic_name: str | None) -> None:
        self.topic_id = topic_id
        self.topic_name = topic_name


class TopicClusterer(Protocol):
    def assign(self, text: str) -> TopicAssignment | None: ...


class UnavailableTopicClusterer:
    def assign(self, text: str) -> TopicAssignment | None:
        _ = text
        return None


class BertopicClusterer:
    def __init__(self, model: object | None = None) -> None:
        self._model = model

    def _load(self) -> object | None:
        if self._model is not None:
            return self._model
        try:
            from bertopic import BERTopic
        except ImportError:
            logger.warning("BERTopic is not installed; topic_id will be omitted")
            return None
        self._model = BERTopic()
        return self._model

    def assign(self, text: str) -> TopicAssignment | None:
        model = self._load()
        if model is None or not text:
            return None
        transform = getattr(model, "transform", None)
        if not callable(transform):
            return None
        try:
            topics, _ = transform([text])
        except Exception:
            logger.warning("BERTopic transform failed; omitting topic")
            return None
        if not topics:
            return None
        topic_id = topics[0]
        if topic_id is None or int(topic_id) < 0:
            return None
        name = None
        get_topic_info = getattr(model, "get_topic_info", None)
        if callable(get_topic_info):
            try:
                info = get_topic_info(int(topic_id))
                name = str(info["Name"].iloc[0]) if "Name" in info else None
            except Exception:
                name = None
        return TopicAssignment(topic_id=str(int(topic_id)), topic_name=name)
