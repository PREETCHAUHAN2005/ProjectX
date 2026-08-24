---
name: fastapi-production
description: Scaffold and harden the FastAPI gateway — routers, Pydantic schemas, exception handlers, CORS, config, native WebSockets, and /api/v1 analytics endpoints. Use when creating or changing the FastAPI app, REST routes, WebSocket endpoints, middleware, or Python API structure.
---

# FastAPI production

Playbook for `backend/`. Follow `fastapi-python.mdc` and `security.mdc`. Align payloads with `data-contract-review`.

## Checklist

```
- [ ] Inspect backend/ (preserve working app)
- [ ] App entry, settings, CORS from config
- [ ] Pydantic request/response models
- [ ] Exception handlers (safe client errors)
- [ ] REST: timeline, network-graph, demographics, trending
- [ ] Native WS: new_post, trend_spike, graph_delta + filter criteria
- [ ] Tests for routes and WS
```

## Step 1 — Foundation (`CHG-002`)

If missing, create a FastAPI app under `backend/` (e.g. `backend/app/main.py`) with:

- settings from env
- API router prefix `/api/v1`
- CORS allowlist from config (not `*` in production)
- dependency-injected Mongo/Neo4j/Redis clients
- pytest foundation

ASGI server (uvicorn) is an implementation choice. Do not add Express or Socket.io.

## Step 2 — Module layout (target)

```text
backend/app/
  main.py
  core/          # settings, exceptions
  api/v1/        # REST routers
  ws/            # WebSocket gateway
  schemas/       # Pydantic
  services/      # analytics queries
```

Workers stay in `workers/`, not inside request handlers. Inference must not run on the request thread as the default design.

## Step 3 — REST (`CHG-008`)

| Endpoint | Returns |
|---|---|
| `GET /api/v1/analytics/timeline` | time-bucketed counts, average sentiment, top 3 dominant emotions |
| `GET /api/v1/analytics/network-graph` | nodes, links, filterable by centrality and weight |
| `GET /api/v1/analytics/demographics` | country, language, profession breakdowns |
| `GET /api/v1/topics/trending` | ranked topics by velocity/acceleration |

Query params, pagination, auth headers, and error envelope are **not** source-confirmed. Define them once, document in `schemas/`, match the TypeScript client. See [contracts.md](../data-contract-review/contracts.md).

## Step 4 — WebSockets (`CHG-009`)

Native FastAPI WebSockets. Event names exactly:

- `event:new_post`
- `event:trend_spike`
- `event:graph_delta`

Support filter criteria from the dashboard: topic, time window, severity.

Must implement: connect, disconnect, payload validation, ignore malformed client messages, reconnection-safe server behavior. Envelope schema is an implementation contract — write it down and share it with the frontend.

## Step 5 — Auth / rate limit gap

Not a confirmed product login screen. Before production: add API authentication and rate limiting **or** record them as a ship blocker in the production-review report. If added, document as a production decision.

## Done when

App starts, routes load, WS accepts a connection, validation rejects bad input, tests cover handlers.
