# ProjectX

**AI-Driven Social Media Analytics Framework**  
Smart India Hackathon 2026 · Problem **26152** · National Technical Research Organisation (NTRO)

ProjectX is an OSINT console for intelligence analysts. It turns public social posts into a live picture of **emotion, topics, people, and geography** — not a marketing dashboard.

Phase 1 sources are **Telegram** and **X**. Reddit is out of scope for this PoC.

---

## What you get

| Analyst view | What it shows |
|---|---|
| Timeline | Root posts vs comments over time, plus average polarity |
| Emotions | GoEmotions mix for the selected window |
| Network | Handles sized by influence, colored by dominant emotion |
| Demographics | Country density, profession, language (aggregate / inferred) |
| Trending | Topics ranked by velocity (`velocity > 2.5` **and** `sample size > 50` for spikes) |
| Live feed | Incoming posts and comments (`event:new_post`) |
| Emotion model | Score a snippet with GoEmotions (Colab URL or local preview) |

The dashboard has **light** and **dark** themes. First visit is light; the choice is stored in `localStorage` as `projectx-theme`. Toggle from the header.

---

## Architecture

```text
Telegram / X
        │
        ▼
Ingestion workers (Python / Telethon)
        │
        ▼
Redis Streams   stream:social:raw
        │
        ▼
Inference (GoEmotions · polarity · topics · NER)
        │
        ├──► MongoDB   posts + NLP fields
        └──► Neo4j     User / Topic graph
                │
                ▼
        FastAPI  REST + native WebSockets
                │
                ▼
        React + TypeScript dashboard
```

The original diagrams used Node.js + Express + Socket.io. This repo uses **FastAPI and native WebSockets** as the gateway. There is no Socket.io client.

```text
frontend/     React + TypeScript + Vite + Tailwind
backend/      FastAPI REST + /ws
workers/      Ingestion + AI pipeline
```

---

## Two ways to run it

### 1. Demo (recommended for a recording)

No Telegram, Redis, MongoDB, or Neo4j required. The API loads a flood-relief thread (posts, comments, emotions) and ticks new comments on an interval.

**Requirements:** Python 3.11+, Node.js 20+

**Backend** (from `backend/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEMO_SEED="true"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DEMO_SEED=true python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`DEMO_SEED` defaults to on in development. `DEMO_TICK_SECONDS` (default `4`) controls how often a new comment is emitted.

**Frontend** (from `frontend/`):

```powershell
copy .env.example .env
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

You should see **API ok** and **Socket connected**. If the API is down, the UI falls back to built-in preview data so the layout still works — use **Force preview data** in the sidebar only when you want that on purpose.

Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Full pipeline (ingestion → Redis → inference → stores)

This path is for live collection. Fill `.env` from the root [`.env.example`](.env.example) — **names only; never commit secrets**.

| Piece | Role | Notes |
|---|---|---|
| Redis | `stream:social:raw` | Required for live ingest |
| MongoDB | Post documents | Optional until wired; app starts without it |
| Neo4j | Network graph | Optional until wired |
| Telethon | Public Telegram channels | `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`, `TELEGRAM_CHANNELS` |
| X adapter | Ingestion switch | `X_INGESTION_BACKEND=ntscraper` or `official_api` — choice is still open |
| Hugging Face | `SamLowe/roberta-base-go_emotions` | `pip install -r workers/requirements-ml.txt` |

Workers live under `workers/ingestion/` and `workers/inference/`. Unit tests do **not** download the model; they use fakes.

Optional dashboard model slot: set `VITE_MODEL_URL` to a service that accepts `POST { "text": "..." }` and returns `{ "emotions": [{ "label", "score" }] }`.

---

## REST and WebSocket

Confirmed analytics routes:

| Method | Path |
|---|---|
| `GET` | `/api/v1/analytics/timeline` |
| `GET` | `/api/v1/analytics/network-graph` |
| `GET` | `/api/v1/analytics/demographics` |
| `GET` | `/api/v1/topics/trending` |

Useful query params on analytics routes: `topic`, `from`, `to`, `severity`. Timeline also takes `bucket=hour|day`. Network graph also takes `min_centrality` and `min_weight`.

WebSocket: `ws://127.0.0.1:8000/ws`

| Event | Meaning |
|---|---|
| `event:new_post` | New post or comment |
| `event:trend_spike` | Spike — only when velocity **> 2.5** and sample size **> 50** |
| `event:graph_delta` | Graph increment |

Clients may send a filter frame (`topic`, time window, `severity`). Exact envelope extras that are not in the product spec are marked **IMPLEMENTATION** in code.

CORS defaults to `http://127.0.0.1:5173` and `http://localhost:5173`. Override with `CORS_ORIGINS`.

---

## Environment

Copy [`.env.example`](.env.example) (repo root) and [`frontend/.env.example`](frontend/.env.example). Do not commit `.env`.

| Variable | Used by | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | Frontend | REST origin (default `http://127.0.0.1:8000`) |
| `VITE_WS_URL` | Frontend | WebSocket URL (default `ws://127.0.0.1:8000/ws`) |
| `VITE_MODEL_URL` | Frontend | Optional GoEmotions HTTP service |
| `APP_ENV` | Backend | `development` / other |
| `API_HOST` / `API_PORT` | Backend | Bind address |
| `CORS_ORIGINS` | Backend | Comma-separated origins |
| `DEMO_SEED` | Backend | Load demo thread |
| `DEMO_TICK_SECONDS` | Backend | Demo comment interval |
| `REDIS_URL` | Backend / workers | Redis |
| `MONGODB_URI` | Backend | Mongo (optional) |
| `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` | Backend | Neo4j (optional) |
| `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` / `TELEGRAM_SESSION` / `TELEGRAM_CHANNELS` | Workers | Telethon |
| `X_INGESTION_BACKEND` / `X_BEARER_TOKEN` | Workers | X adapter |

---

## Tests

From the **repository root** (uses root `pytest.ini`):

```powershell
# backend API, WebSocket, demo seed
backend\.venv\Scripts\python.exe -m pytest backend/tests

# polarity, trend-spike rule, ingest/inference units
backend\.venv\Scripts\python.exe -m pytest workers/tests
```

Frontend:

```powershell
cd frontend
npm run typecheck
```

Do not use production credentials in tests. Trend spikes must satisfy **both** `velocity > 2.5` and `sample size > 50`.

---

## NLP rules (Phase 1)

- Emotion model: **`SamLowe/roberta-base-go_emotions`** (28 labels). Do not swap it.
- Polarity buckets: `POSITIVE` · `NEGATIVE` · `NEUTRAL` from the dominant emotion.
- Preprocess: regex clean, URL strip, truncate for the model.
- Topics: BERTopic when the ML extra deps are installed; otherwise an unavailable stub.
- Demographics: spaCy NER profiler when available; otherwise a stub. Values are **inferred and aggregated**, not identity records.

---

## What is not claimed

These are **open or out of scope** — they are not product features just because a README mentioned them:

- Dashboard login / JWT / RBAC (not specified)
- Production API auth and rate limiting (required before any public exposure)
- Reddit ingestion (rejected for Phase 1)
- Instagram / Facebook / YouTube (later, if requested)
- Docker / cloud hosting (not specified)
- Sub-20ms inference (not measured in this repo)

Before production: secrets handling, injection, XSS, SSRF on any URL-fetching worker, and data exposure all need a real review. See [cursor.md](cursor.md) for confirmed vs open decisions.

---

## Specs (deeper than this README)

| File | Role |
|---|---|
| [cursor.md](cursor.md) | Product, architecture, confirmed vs open |
| [changes.md](changes.md) | Implementation contract (`CHG-000` … `CHG-019`) |
| [AGENTS.md](AGENTS.md) | How automated agents should work in this repo |

---

## License

No license file is in the repository yet. Treat the code as SIH project source until the team adds one.
