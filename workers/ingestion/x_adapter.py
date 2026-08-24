from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Literal

from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.raw_post import RawPost, utc_now_iso

logger = logging.getLogger(__name__)

XBackend = Literal["ntscraper", "official_api"]


class XIngestionAdapter(ABC):
    """X source is unresolved (ntscraper vs official API). Keep behind this adapter."""

    backend: XBackend

    @abstractmethod
    def fetch_posts(self) -> AsyncIterator[RawPost]:
        raise NotImplementedError


class NtscraperXAdapter(XIngestionAdapter):
    backend: XBackend = "ntscraper"

    def __init__(self, query: str | None = None) -> None:
        self._query = query

    async def fetch_posts(self) -> AsyncIterator[RawPost]:
        logger.warning(
            "X ntscraper adapter is a placeholder; no posts until a source is selected"
        )
        return
        yield  # pragma: no cover


class OfficialXApiAdapter(XIngestionAdapter):
    backend: XBackend = "official_api"

    def __init__(self, bearer_token: str | None = None) -> None:
        self._bearer_token = bearer_token

    async def fetch_posts(self) -> AsyncIterator[RawPost]:
        if not self._bearer_token:
            logger.error("X official API selected but X_BEARER_TOKEN is empty")
        else:
            logger.warning(
                "X official API adapter is a placeholder; token present but client not finalized"
            )
        return
        yield  # pragma: no cover


def build_x_adapter(backend: str, bearer_token: str | None = None) -> XIngestionAdapter:
    if backend == "official_api":
        return OfficialXApiAdapter(bearer_token=bearer_token)
    if backend != "ntscraper":
        logger.warning("Unknown X_INGESTION_BACKEND=%s; using ntscraper placeholder", backend)
    return NtscraperXAdapter()


def from_ntscraper_item(item: dict[str, Any]) -> RawPost | None:
    """Map a scraper-like dict into the internal raw-post (implementation)."""
    return normalize_raw_post(
        {
            "platform": "x",
            "external_id": item.get("id") or item.get("external_id"),
            "timestamp": item.get("timestamp") or item.get("date") or utc_now_iso(),
            "author": {
                "user_id": item.get("user_id") or item.get("username") or "",
                "handle": item.get("username") or item.get("handle") or "",
            },
            "content": {"raw_text": item.get("text") or item.get("raw_text") or ""},
        }
    )
