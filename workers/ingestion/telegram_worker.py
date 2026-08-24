from __future__ import annotations

import logging
import os
from datetime import datetime

from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.raw_post import RawPost, utc_now_iso
from workers.ingestion.redis_stream import RedisStreamPublisher

logger = logging.getLogger(__name__)


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def telegram_channels_from_env() -> list[str]:
    """IMPLEMENTATION env TELEGRAM_CHANNELS — comma-separated public usernames."""
    raw = _env("TELEGRAM_CHANNELS")
    return [item.lstrip("@").strip() for item in raw.split(",") if item.strip()]


class TelegramIngestion:
    """Telethon public-channel ingestion. Credentials must come from env."""

    def __init__(
        self,
        api_id: str | None = None,
        api_hash: str | None = None,
        session: str | None = None,
    ) -> None:
        self.api_id = api_id if api_id is not None else _env("TELEGRAM_API_ID")
        self.api_hash = api_hash if api_hash is not None else _env("TELEGRAM_API_HASH")
        self.session = session if session is not None else _env("TELEGRAM_SESSION")

    def credentials_ok(self) -> bool:
        return bool(self.api_id and self.api_hash)

    async def publish_forever(self, publisher: RedisStreamPublisher) -> None:
        if not self.credentials_ok():
            logger.error(
                "Telegram ingestion cannot start: TELEGRAM_API_ID / TELEGRAM_API_HASH missing"
            )
            return
        try:
            from telethon import TelegramClient, events
            from telethon.sessions import StringSession
        except ImportError:
            logger.error("telethon is not installed")
            return
        try:
            api_id = int(self.api_id)
        except ValueError:
            logger.error("TELEGRAM_API_ID must be an integer")
            return

        session = StringSession(self.session) if self.session else "projectx_telegram"
        channels = telegram_channels_from_env()
        client = TelegramClient(session, api_id, self.api_hash)

        @client.on(events.NewMessage(chats=channels or None))
        async def _on_message(event: object) -> None:
            message = getattr(event, "message", event)
            post = from_telethon_message(message)
            if post is None:
                logger.warning("Quarantined Telegram message")
                return
            try:
                await publisher.publish_raw_post(post)
            except Exception:
                logger.exception("Failed publishing Telegram message to Redis")

        await client.start()
        logger.info("Telegram Telethon client connected")
        await client.run_until_disconnected()


def from_telethon_message(message: object) -> RawPost | None:
    """Normalize a Telethon message object or a test dict."""
    if isinstance(message, dict):
        data = message
        chat = data.get("chat") or {}
        sender = data.get("sender") or {}
        msg_id = data.get("id") or data.get("external_id")
        date = data.get("date") or data.get("timestamp")
        text = data.get("message") or data.get("raw_text") or ""
        user_id = sender.get("id") or chat.get("id")
        handle = (
            sender.get("username")
            or chat.get("username")
            or chat.get("title")
            or ""
        )
    else:
        chat = getattr(message, "chat", None)
        sender = getattr(message, "sender", None)
        msg_id = getattr(message, "id", None)
        date = getattr(message, "date", None)
        text = getattr(message, "message", None) or ""
        user_id = getattr(sender, "id", None) or getattr(chat, "id", None)
        handle = (
            getattr(sender, "username", None)
            or getattr(chat, "username", None)
            or getattr(chat, "title", None)
            or ""
        )

    if hasattr(date, "isoformat"):
        date = date.isoformat()

    return normalize_raw_post(
        {
            "platform": "telegram",
            "external_id": str(msg_id or ""),
            "timestamp": str(date or utc_now_iso()),
            "author": {
                "user_id": str(user_id or ""),
                "handle": str(handle or ""),
            },
            "content": {"raw_text": str(text)},
        }
    )
