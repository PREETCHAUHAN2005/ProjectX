from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from workers.ingestion.raw_post import RawAuthor, RawContent, RawEngagement, RawPost, utc_now_iso

logger = logging.getLogger(__name__)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_raw_post(data: dict[str, Any]) -> RawPost | None:
    """Return a RawPost or None if the event must be quarantined (never silent)."""
    try:
        author = data.get("author") or {}
        content = data.get("content") or {}
        engagement = data.get("engagement") or {}
        post = RawPost(
            platform=data.get("platform"),
            external_id=str(data.get("external_id") or ""),
            timestamp=str(data.get("timestamp") or ""),
            author=RawAuthor(
                user_id=str(author.get("user_id") or ""),
                handle=str(author.get("handle") or ""),
                bio=author.get("bio"),
                follower_count=_optional_int(author.get("follower_count")),
            ),
            content=RawContent(
                raw_text=str(content.get("raw_text") or ""),
                hashtags=content.get("hashtags"),
                language=content.get("language"),
            ),
            engagement=RawEngagement(
                likes=_optional_int(engagement.get("likes")),
                shares=_optional_int(engagement.get("shares")),
                views=_optional_int(engagement.get("views")),
            ),
            ingested_at=str(data.get("ingested_at") or utc_now_iso()),
        )
        return post
    except (ValidationError, TypeError, ValueError) as exc:
        logger.warning("Quarantined malformed source event: %s", exc)
        return None
