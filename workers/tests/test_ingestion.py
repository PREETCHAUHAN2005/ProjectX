from workers.ingestion.normalize import normalize_raw_post
from workers.ingestion.telegram_worker import from_telethon_message
from workers.ingestion.x_adapter import build_x_adapter, from_ntscraper_item


def test_normalize_valid_telegram() -> None:
    post = normalize_raw_post(
        {
            "platform": "telegram",
            "external_id": "42",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "news"},
            "content": {"raw_text": "hello"},
        }
    )
    assert post is not None
    assert post.platform == "telegram"
    assert post.external_id == "42"


def test_normalize_quarantines_missing_id() -> None:
    post = normalize_raw_post(
        {
            "platform": "x",
            "external_id": "",
            "timestamp": "2026-08-24T00:00:00+00:00",
            "author": {"user_id": "1", "handle": "u"},
            "content": {"raw_text": "hello"},
        }
    )
    assert post is None


def test_telegram_message_mapper() -> None:
    post = from_telethon_message(
        {
            "id": 9,
            "date": "2026-08-24T01:00:00+00:00",
            "message": "channel text",
            "chat": {"username": "publicchan"},
        }
    )
    assert post is not None
    assert post.platform == "telegram"
    assert post.content.raw_text == "channel text"


def test_x_adapter_choice_not_frozen_as_product() -> None:
    ntscraper = build_x_adapter("ntscraper")
    official = build_x_adapter("official_api")
    assert ntscraper.backend == "ntscraper"
    assert official.backend == "official_api"


def test_x_item_mapper() -> None:
    post = from_ntscraper_item(
        {"id": "t1", "username": "alice", "text": "hello x", "date": "2026-08-24T00:00:00Z"}
    )
    assert post is not None
    assert post.platform == "x"
    assert post.external_id == "t1"
