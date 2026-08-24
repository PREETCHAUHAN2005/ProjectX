# Confirmed vs unspecified contracts

Source: `cursor.md` and `changes.md`. Anything not listed here is not a confirmed product field.

## MongoDB `posts` (confirmed)

```text
_id: ObjectId
platform: String
external_id: String
timestamp: Date
author:
  user_id, handle, bio, follower_count
content:
  raw_text, clean_text, hashtags, language
analytics:
  sentiment: label, score
  emotions: [ { label, score } ]
  topic_id, topic_name
  demographics:
    inferred_country, inferred_region, inferred_profession, confidence
engagement:
  likes, shares, views
```

Indexes, connection URI, and duplicate strategy: **open** (implementation).

## Neo4j (confirmed)

- `(:User {id, handle, platform})`
- `(:Topic {name})`
- `(:User)-[:INTERACTED {type, timestamp, weight}]->(:User)`

No other node/rel types as confirmed architecture.

## REST (confirmed purpose only)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/analytics/timeline` | time-bucketed counts, average sentiment, top 3 dominant emotions |
| GET | `/api/v1/analytics/network-graph` | nodes, links, centrality/weight filters |
| GET | `/api/v1/analytics/demographics` | country, language, profession breakdowns |
| GET | `/api/v1/topics/trending` | ranked by velocity/acceleration |

Unspecified: query parameter names, pagination, auth headers, error JSON envelope, HTTP codes beyond normal REST practice.

## WebSocket (confirmed names only)

- `event:new_post`
- `event:trend_spike`
- `event:graph_delta`

Unspecified: envelope, payload bodies, heartbeat, reconnect, auth, fan-out. Dashboard must still be able to send filter criteria: topic, time window, severity.

## Redis

Confirmed stream: `stream:social:raw`. Message body schema is implementation.

## TypeScript (`CHG-015`)

Must exist and stay aligned: timeline aggregates, network nodes/links, demographic aggregates, trending topics, raw post events, trend spikes, graph deltas.
