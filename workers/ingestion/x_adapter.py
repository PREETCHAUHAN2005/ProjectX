from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Literal

from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.raw_post import RawPost, utc_now_iso

logger = logging.getLogger(__name__)

XBackend = Literal["ntscraper", "official_api"]
X_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


class XIngestionAdapter(ABC):
    """X source is unresolved (ntscraper vs official API). Keep behind this adapter."""

    backend: XBackend

    @abstractmethod
    def fetch_posts(
        self, *, query: str | None = None, limit: int = 10
    ) -> AsyncIterator[RawPost]:
        raise NotImplementedError


class NtscraperXAdapter(XIngestionAdapter):
    backend: XBackend = "ntscraper"

    def __init__(self, query: str | None = None) -> None:
        self._query = query

    async def fetch_posts(
        self, *, query: str | None = None, limit: int = 10
    ) -> AsyncIterator[RawPost]:
        term = (query or self._query or "India").strip() or "India"
        try:
            posts = await asyncio.wait_for(
                asyncio.to_thread(_ntscraper_collect, term, max(1, min(limit, 40))),
                timeout=5,
            )
        except Exception:
            logger.warning("ntscraper fetch failed; caller may use demo replay")
            posts = []
        for post in posts:
            yield post


class OfficialXApiAdapter(XIngestionAdapter):
    backend: XBackend = "official_api"

    def __init__(self, bearer_token: str | None = None, query: str | None = None) -> None:
        self._bearer_token = bearer_token
        self._query = query

    async def fetch_posts(
        self, *, query: str | None = None, limit: int = 10
    ) -> AsyncIterator[RawPost]:
        posts: list[RawPost] = []
        if not self._bearer_token:
            logger.error("X official API selected but X_BEARER_TOKEN is empty")
        else:
            term = (query or self._query or "India").strip() or "India"
            try:
                posts = await _official_search(
                    self._bearer_token, term, max(10, min(limit, 50))
                )
            except Exception:
                logger.warning("X official API fetch failed")
                posts = []
        for post in posts:
            yield post


def build_x_adapter(
    backend: str, bearer_token: str | None = None, query: str | None = None
) -> XIngestionAdapter:
    if backend == "official_api":
        return OfficialXApiAdapter(bearer_token=bearer_token, query=query)
    if backend not in {"ntscraper", "auto"}:
        logger.warning("Unknown X_INGESTION_BACKEND=%s; using ntscraper adapter", backend)
    return NtscraperXAdapter(query=query)


def from_ntscraper_item(item: dict[str, Any]) -> RawPost | None:
    """Map a scraper-like dict into the internal raw-post (implementation)."""
    link = str(item.get("link") or "")
    derived_id = link.rstrip("/").split("/")[-1] if link else ""
    user = item.get("user") or item.get("username") or item.get("handle") or ""
    if isinstance(user, dict):
        user = user.get("username") or user.get("name") or ""
    return normalize_raw_post(
        {
            "platform": "x",
            "external_id": item.get("id") or item.get("external_id") or derived_id,
            "timestamp": item.get("timestamp") or item.get("date") or utc_now_iso(),
            "author": {
                "user_id": item.get("user_id") or user or "",
                "handle": user or item.get("username") or item.get("handle") or "",
            },
            "content": {"raw_text": item.get("text") or item.get("raw_text") or ""},
        }
    )


def from_official_api_item(
    tweet: dict[str, Any], users_by_id: dict[str, dict[str, Any]]
) -> RawPost | None:
    author_id = str(tweet.get("author_id") or "")
    user = users_by_id.get(author_id) or {}
    metrics = tweet.get("public_metrics") or {}
    user_metrics = user.get("public_metrics") or {}
    return normalize_raw_post(
        {
            "platform": "x",
            "external_id": str(tweet.get("id") or ""),
            "timestamp": str(tweet.get("created_at") or utc_now_iso()),
            "author": {
                "user_id": author_id,
                "handle": str(user.get("username") or author_id),
                "bio": user.get("description"),
                "follower_count": user_metrics.get("followers_count"),
            },
            "content": {
                "raw_text": str(tweet.get("text") or ""),
                "language": tweet.get("lang"),
            },
            "engagement": {
                "likes": metrics.get("like_count"),
                "shares": metrics.get("retweet_count"),
                "views": metrics.get("impression_count"),
            },
        }
    )


def _ntscraper_collect(term: str, limit: int) -> list[RawPost]:
    try:
        from ntscraper import Nitter
    except ImportError:
        logger.warning("ntscraper is not installed")
        return []
    scraper = Nitter(log_level=1, skip_instance_check=True)
    payload = scraper.get_tweets(term, mode="term", number=limit)
    tweets = payload.get("tweets") if isinstance(payload, dict) else None
    if not tweets:
        return []
    posts: list[RawPost] = []
    for item in tweets:
        if not isinstance(item, dict):
            continue
        post = from_ntscraper_item(item)
        if post is not None:
            posts.append(post)
    return posts


async def _official_search(bearer_token: str, query: str, limit: int) -> list[RawPost]:
    try:
        import httpx
    except ImportError:
        logger.warning("httpx is not installed")
        return []
    params = {
        "query": query[: 400],
        "max_results": str(limit),
        "tweet.fields": "created_at,lang,public_metrics,author_id",
        "expansions": "author_id",
        "user.fields": "username,description,public_metrics",
    }
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.get(X_SEARCH_URL, params=params, headers=headers)
    if response.status_code != 200:
        logger.warning("X official API HTTP %s", response.status_code)
        return []
    body = response.json()
    if not isinstance(body, dict):
        return []
    users_by_id = {
        str(user.get("id")): user
        for user in (body.get("includes") or {}).get("users") or []
        if isinstance(user, dict) and user.get("id")
    }
    posts: list[RawPost] = []
    for tweet in body.get("data") or []:
        if not isinstance(tweet, dict):
            continue
        post = from_official_api_item(tweet, users_by_id)
        if post is not None:
            posts.append(post)
    return posts


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
