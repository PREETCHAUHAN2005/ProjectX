from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Platform = Literal["telegram", "x"]


class RawAuthor(BaseModel):
    user_id: str
    handle: str
    bio: str | None = None
    follower_count: int | None = None


class RawContent(BaseModel):
    raw_text: str
    hashtags: list[str] | None = None
    language: str | None = None


class RawEngagement(BaseModel):
    likes: int | None = None
    shares: int | None = None
    views: int | None = None


class RawPost(BaseModel):
    """Internal raw-post shape published to stream:social:raw (implementation)."""

    platform: Platform
    external_id: str
    timestamp: str
    author: RawAuthor
    content: RawContent
    engagement: RawEngagement = Field(default_factory=RawEngagement)
    ingested_at: str

    @field_validator("external_id")
    @classmethod
    def external_id_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("external_id is required")
        return value

    @field_validator("timestamp")
    @classmethod
    def timestamp_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("timestamp is required")
        return value


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
