"""Analyzed post document matching the confirmed MongoDB `posts` shape."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Polarity = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
Platform = Literal["telegram", "x"]


class Author(BaseModel):
    user_id: str
    handle: str
    bio: str | None = None
    follower_count: int | None = None


class Content(BaseModel):
    raw_text: str
    clean_text: str
    hashtags: list[str] | None = None
    language: str | None = None


class Sentiment(BaseModel):
    label: Polarity
    score: float


class Emotion(BaseModel):
    label: str
    score: float


class Demographics(BaseModel):
    inferred_country: str | None = None
    inferred_region: str | None = None
    inferred_profession: str | None = None
    confidence: float | None = None


class Analytics(BaseModel):
    sentiment: Sentiment
    emotions: list[Emotion]
    topic_id: str | None = None
    topic_name: str | None = None
    demographics: Demographics | None = None
    # IMPLEMENTATION extras for demo threads (not confirmed Mongo fields).
    thread_role: Literal["post", "comment"] | None = None
    in_reply_to: str | None = None
    severity: str | None = None


class Engagement(BaseModel):
    likes: int | None = None
    shares: int | None = None
    views: int | None = None


class PostDocument(BaseModel):
    """Confirmed Mongo `posts` fields. `_id` assigned by the store on persist."""

    platform: Platform
    external_id: str
    timestamp: str
    author: Author
    content: Content
    analytics: Analytics
    engagement: Engagement = Field(default_factory=Engagement)

    def document_key(self) -> tuple[str, str]:
        return self.platform, self.external_id

    def to_mongo_dict(self) -> dict[str, Any]:
        return self.model_dump()
