---
name: social-ingestion
description: Implement Telegram (Telethon) and X/Twitter ingestion workers that normalize raw posts and publish to Redis Streams stream:social:raw. Use when adding or changing social source workers, Telethon, ntscraper/X API adapters, raw-post shape, Redis publication, or Phase-1 platform scope (no Reddit).
---

# Social ingestion

Playbook for `workers/` ingestion. Follow `.cursor/rules/architecture.mdc`, `fastapi-python.mdc`, and `security.mdc`.

## Checklist

```
- [ ] Inspect existing workers/adapters (preserve approved X choice if present)
- [ ] Normalize to internal raw-post shape
- [ ] Telegram: Telethon public channels
- [ ] X: adapter only unless repo/user already selected ntscraper vs official API
- [ ] Publish to Redis Streams stream:social:raw
- [ ] Failures logged; no silent drop; no secrets in git
- [ ] No Reddit in Phase 1
```

## Step 1 — Inspect

Search `workers/`, `backend/`, and config for Telethon, Redis, and any X client. Classify `COMPLETE | PARTIAL | MISSING`. Do not replace a working adapter.

## Step 2 — Raw-post shape

Every source must emit the same internal event (implementation schema; keep consistent):

- `platform`: `telegram` | `x`
- `external_id`, `timestamp` (source time, ISO-8601 UTC)
- `author`: `user_id`, `handle`, optional `bio`, `follower_count`
- `content`: `raw_text`, optional `hashtags`, `language`
- `engagement`: `likes`, `shares`, `views` when the source provides them
- `ingested_at`

Validate before publish. Preserve platform metadata. Drop/quarantine records missing `platform`, `external_id`, or `timestamp`.

## Step 3 — Telegram (confirmed)

Use Telethon / MTProto for **public channel** ingestion. Session strings and API id/hash come from env (`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION` or equivalent). Never commit session files.

Normalize channel messages → raw-post → Redis.

## Step 4 — X (unresolved)

1. If the repo already has an approved implementation, keep it and document it.
2. Otherwise implement an `XIngestionAdapter` with `ntscraper` and official-API placeholders; wire **one** behind config (`X_INGESTION_BACKEND`) without calling that choice “source-confirmed.”
3. Do not scrape in a way that embeds credentials in code.

## Step 5 — Redis Streams

Stream name: `stream:social:raw`. Serialize JSON (or msgpack if already established). Include `timestamp` and `platform`. Consumers must skip/malform-log bad frames and continue.

## Step 6 — Out of scope

Reddit: rejected for Phase 1. Instagram, Facebook, YouTube: do not implement unless the user explicitly expands scope.

Archive/demo JSON (`CHG-018`) is optional and must stay behind an explicit config flag — never the default live path.

## Done when

A valid Telegram (and, if selected, X) event can be normalized and appears on `stream:social:raw`; worker crashes and source errors are visible in logs.
