# cursor.md

## Project Identity

**Project:** AI-Driven Social Media Analytics Framework  
**Problem Statement ID:** 26152  
**Organization:** National Technical Research Organisation (NTRO)  
**Programme:** Smart India Hackathon (SIH) 2026  
**Primary Users:** NTRO / intelligence analysts  
**Product Type:** Open-Source Intelligence (OSINT) and Social Media Intelligence dashboard

## Executive Summary

The system is an event-driven, automated intelligence center that processes social-media data to provide real-time intelligence views. Its confirmed capabilities are:

- continuous, time-stamped social-data collection and timeline management,
- multi-dimensional sentiment/emotion inference,
- aggregate anonymized demographic profiling,
- real-time trend/topic detection and prediction,
- link/network analysis and information-flow visualization.

The confirmed Phase-1 social sources are X (formerly Twitter) and Telegram. Instagram and Facebook are desirable, while YouTube is appreciable. Reddit ingestion for the Phase-1 PoC was explicitly rejected.

## Product Objective

Combine sentiment analysis, demographics, trend tracking, and link analysis to extract actionable audience intelligence from raw platform data.

## Core Confirmed Features

### 1. Continuous Data Collection & Timeline Management
Multi-platform ingestion with structured, time-stamped historical data.

### 2. Multi-Dimensional Sentiment Inference
Detect nuanced emotions such as sarcasm, anxiety, fear, etc., and map results along a timeline.

### 3. Automated Demographic Profiling
Infer aggregate, anonymized follower demographics such as age, geography, language, and profession from public indicators.

### 4. Real-Time Trend & Topic Detection
Identify, rank, and predict viral keywords and shifting discussions.

### 5. Link Analysis & Network Topology
Map relationships, identify high-influence nodes / KOLs, and visualize sentiment spread.

## Supported Platforms

| Platform | Status | Notes |
|---|---|---|
| X / Twitter | MUST-HAVE | Ingestion implementation was proposed as `ntscraper` or the official API; exact choice remains unresolved. |
| Telegram | MUST-HAVE | Real-time public-channel ingestion via Telegram MTProto / Telethon is confirmed. |
| Instagram | DESIRABLE | Not specified further. |
| Facebook | DESIRABLE | Not specified further. |
| YouTube | APPRECIABLE | YouTube Data API v3 was mentioned. |
| Reddit | REJECTED for Phase 1 PoC | Reddit API restrictions in 2026 and Devvit suitability concerns were explicitly cited. |

## Sentiment / NLP Pipeline

Confirmed preprocessing:
- Regex-based text cleaning.
- URL stripping.
- Maximum text length of 512 tokens/characters as described in the source; preserve the implementation intent and verify the exact tokenizer-length interpretation before production.

Confirmed model:
- Hugging Face `SamLowe/roberta-base-go_emotions`.

Confirmed inference:
- 28-dimensional multi-label emotion vector.

Confirmed polarity mapping:
- Positive, negative, or neutral bucket derived from the dominant fine-grained emotion.

## Confirmed Data Flow

```text
Raw Social Post (Telegram / X)
        ↓
API / Scraper Ingestion Worker (Python / Telethon)
        ↓
Redis Streams Message Bus (`stream:social:raw`)
        ↓
Distributed AI Inference Pipeline (Python)
        ├── RoBERTa (Emotions)
        ├── BERTopic (Clustering)
        └── spaCy NER Profiler
        ↓
Dual Database Write
        ├── MongoDB (documents / NLP data)
        └── Neo4j (graph data)
        ↓
Backend API / WebSocket
        ↓
React Intelligence Dashboard
```

## Architecture

### Ingestion Layer
Workers for X, Telegram, Reddit, and YouTube were represented in the original architecture. Phase-1 confirmed priority is X + Telegram; Reddit is rejected for Phase 1.

### Message Broker
Redis Streams (or Kafka) was proposed in the source. Redis Streams is explicitly used in the detailed data-flow notation.

### AI Processing
Python, PyTorch and Hugging Face Transformers are part of the stated AI pipeline. The detailed flow also includes BERTopic and spaCy NER.

### Data Stores
- MongoDB for raw posts and NLP-oriented documents.
- Neo4j for graph/network analysis.
- Redis for time-series/pub-sub or message-bus responsibilities.

### API / Real-Time Layer
The source architecture originally used Node.js + Express + Socket.io, but the project constraint mandates **FastAPI + Python**. Therefore the backend gateway must be implemented with FastAPI and native WebSockets, replacing the Node.js/Express + Socket.io gateway while preserving the intended API/realtime behavior.

### Frontend
React is confirmed. The source also names:
- TypeScript (project-level constraint)
- Tailwind
- Recharts
- `react-force-graph-2d`

## Frontend Requirements

### Timeline Scrubber
Dual-axis area/line chart using Recharts for sentiment polarity over time.

### Network Topology Canvas
Force-directed graph using `react-force-graph-2d`; nodes represent influential users/KOLs, scaled by PageRank and colored by community cluster.

### Demographic Heatmaps
Interactive choropleth geographic density visualization plus donut charts for professional sectors.

### Raw Surveillance Feed
Live scrolling feed of incoming raw posts.

### Confirmed Analyst Interaction
Analyst can select topic and time window on the dashboard scrubber. Severity filtering is part of the stated workflow.

The frontend then dispatches the WebSocket criteria and re-renders timeline, graph, and demographic visualizations from backend results.

## Backend API Contract

Confirmed REST endpoints:

### `GET /api/v1/analytics/timeline`
Returns:
- time-bucketed counts,
- average sentiment,
- top 3 dominant emotions.

### `GET /api/v1/analytics/network-graph`
Returns:
- graph nodes,
- graph links,
- filtering by centrality and weight.

### `GET /api/v1/analytics/demographics`
Returns aggregated breakdowns by:
- country,
- language,
- profession.

### `GET /api/v1/topics/trending`
Returns ranked topics sorted by velocity / acceleration.

### WebSocket Events
- `event:new_post`
- `event:trend_spike`
- `event:graph_delta`

Exact WebSocket message schemas are not established and must not be invented.

## Data Model

### MongoDB `posts` collection

Confirmed fields:

```text
_id: ObjectId
platform: String
external_id: String
timestamp: Date
author:
  user_id
  handle
  bio
  follower_count
content:
  raw_text
  clean_text
  hashtags
  language
analytics:
  sentiment:
    label
    score
  emotions:
    - label
      score
  topic_id
  topic_name
  demographics:
    inferred_country
    inferred_region
    inferred_profession
    confidence
engagement:
  likes
  shares
  views
```

### Neo4j

Confirmed nodes:
- `(:User {id, handle, platform})`
- `(:Topic {name})`

Confirmed relationship:
- `(:User)-[:INTERACTED {type, timestamp, weight}]->(:User)`

## Business Rules

### Polarity Mapping

After the emotion vector is generated:
- positive-dominant emotion → `POSITIVE`
- negative-dominant emotion → `NEGATIVE`
- otherwise → `NEUTRAL`

The source gives examples such as joy/love as positive and fear/anger as negative.

### Trend Velocity Spike

Flag a topic when:
- velocity > `2.5`
- sample size > `50`

## Performance / Real-Time Requirements

Confirmed:
- live processing and WebSocket-driven updates,
- text truncation configured to prevent model overflow,
- sub-20ms inference was stated as a live-streaming requirement.

The source does not establish a full end-to-end latency budget.

## Authentication / Authorization

No login, JWT, or dashboard role-based authorization was established in the source conversation.

Status: **NOT SPECIFIED**

Do not invent a dashboard authentication design as a confirmed requirement.

## Security Gap

The source explicitly identifies an implementation gap around:
- backend API authentication,
- rate limiting.

These must be treated as security decisions requiring implementation design before production exposure, not as already-established behavior.

## Environment / Deployment

Exact deployment infrastructure was **not specified**.

Examples such as Docker, AWS, Kubernetes, or a specific hosting provider must not be treated as confirmed architecture.

## Important Architectural Decision

The Gemini architecture proposed:

```text
Node.js / Express + Socket.io
```

but the project-level implementation constraint requires:

```text
FastAPI + Python
```

Therefore:

```text
Node.js / Express + Socket.io
        ↓
FastAPI + native WebSockets
```

This is the explicit architecture mapping required by the source specification. Preserve all intended backend responsibilities and realtime behavior.

## Rejected Requirements

Reddit ingestion for the Phase-1 PoC is rejected.

Do not reintroduce Reddit into the Phase-1 implementation unless the project requirements are later changed explicitly.

## Open Decisions

- Exact X ingestion implementation: `ntscraper` vs official X API.
- Exact API authentication mechanism.
- Exact backend rate-limiting design.
- Exact deployment infrastructure.
- Exact database connection/indexing configuration.
- Exact WebSocket event schemas.
- Exact implementation for desirable/appreciable platforms.
- Exact interpretation of the 512-length truncation requirement.
- Exact access/permission model for the dashboard.

## Project Development Rules

1. Do not replace the established architecture without an explicit requirement change.
2. Treat confirmed requirements as authoritative.
3. Treat rejected requirements as unavailable for Phase 1.
4. Do not present an implementation gap as a confirmed product decision.
5. Do not invent credentials, secrets, URLs, API contracts, or external capabilities.
6. Preserve frontend/backend API contract consistency.
7. Use React + TypeScript for the frontend.
8. Use FastAPI + Python for the backend.
9. Prefer native FastAPI WebSockets for the realtime channel replacing Socket.io.
10. Keep platform ingestion, AI inference, persistence, API delivery, and visualization logically separated.
11. Validate all external data before processing or persistence.
12. Keep the implementation production-oriented but do not add unnecessary infrastructure.

## Definition of Done

A feature is complete only when:
- its confirmed requirement is implemented,
- its integration path works,
- failure/empty/loading states are handled where applicable,
- type/build checks pass,
- relevant tests pass,
- security implications are reviewed,
- no established architectural requirement has been violated.

