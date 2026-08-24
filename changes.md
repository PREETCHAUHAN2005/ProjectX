# changes.md

# 1. Purpose

This document converts the verified Gemini project specification into an implementation contract for a working full-stack website.

Source basis:
- Gemini project specification supplied for this task.
- Project constraints: React + TypeScript frontend and FastAPI + Python backend.

This document does not replace the existing architecture; it maps the established architecture to the required implementation stack.

---

# 2. Scope

## In Scope

The first implementation target is the OSINT/social-media analytics dashboard centered on:

- X / Twitter data,
- Telegram data,
- sentiment/emotion analytics,
- timeline analytics,
- demographic analytics,
- trend/topic analytics,
- network/link analysis,
- live surveillance feed,
- real-time WebSocket updates.

## Explicitly Rejected for Phase 1

- Reddit ingestion.

## Desirable / Future Scope

- Instagram,
- Facebook.

## Appreciable / Later Scope

- YouTube.

These platform priorities must not be interpreted as fully implemented integrations unless the source explicitly defines them.

---

# 3. Architecture Contract

## 3.1 Source Architecture

```text
Social Sources
    ↓
Ingestion Workers
    ↓
Redis Streams
    ↓
AI Inference Pipeline
    ↓
MongoDB + Neo4j
    ↓
Backend API / WebSocket
    ↓
React Dashboard
```

## 3.2 Required Implementation Mapping

The original gateway proposal used:

```text
Node.js + Express + Socket.io
```

The project constraint requires:

```text
FastAPI + Python
```

Therefore the implementation must use:

```text
FastAPI REST API
+
FastAPI native WebSockets
```

while preserving the original responsibilities of the gateway.

Do not introduce Node.js merely to preserve the old diagram.

---

# 4. Implementation Phases

## Phase 0 — Repository and Environment

### Change CHG-000

**Objective:** Establish or inspect the repository before implementation.

Requirements:
- inspect current files,
- inspect existing frontend/backend code,
- inspect configuration,
- inspect environment files,
- inspect tests,
- inspect documentation,
- preserve existing work.

Acceptance:
- current repository state is understood before modification.

---

## Phase 1 — Frontend Foundation

### Change CHG-001

Create/configure the React + TypeScript application if it does not already exist.

Required capabilities:
- React,
- TypeScript,
- routing as needed for the dashboard,
- styling system consistent with the stated Tailwind direction,
- typed API client,
- typed WebSocket client.

Do not add additional state-management infrastructure unless required by the implementation.

Acceptance:
- frontend starts,
- TypeScript checks,
- production build succeeds.

---

## Phase 2 — Backend Foundation

### Change CHG-002

Create/configure the FastAPI backend if it does not already exist.

Required:
- FastAPI application entry point,
- API routing,
- configuration management,
- request/response validation,
- exception handling,
- CORS configuration as required by deployment,
- WebSocket support,
- testing foundation.

Acceptance:
- FastAPI application starts,
- API routes load,
- WebSocket endpoint can accept connections.

---

## Phase 3 — Data Ingestion Foundation

### Change CHG-003

Implement the ingestion abstraction required for the confirmed Phase-1 platforms.

### Telegram
Use Telethon / Telegram MTProto as the confirmed real-time public-channel ingestion mechanism.

### X
Create an ingestion abstraction because the exact implementation is unresolved between `ntscraper` and the official API.

The implementation must not hard-code an unapproved X integration choice as final architecture.

Acceptance:
- source events can be normalized into the internal raw-post representation,
- platform metadata is preserved,
- failures do not silently disappear.

---

## Phase 4 — Message Bus

### Change CHG-004

Implement the Redis Streams path:

```text
stream:social:raw
```

Requirements:
- serialize normalized raw social posts,
- publish to the stream,
- make consumers resilient to malformed input,
- preserve event timestamps and platform identifiers.

Acceptance:
- a valid ingestion event reaches the stream,
- downstream processing can consume it.

---

## Phase 5 — AI Inference Pipeline

### Change CHG-005

Implement the Python AI processing pipeline.

Required components:

- preprocessing,
- RoBERTa emotion inference,
- BERTopic clustering as established in the architecture,
- spaCy NER profiler as established in the architecture.

### Emotion Model

Use:

```text
SamLowe/roberta-base-go_emotions
```

### Preprocessing

Implement:
- regex cleaning,
- URL stripping,
- length control.

Important:
The source says `512 max length` and also mentions `truncation=True`. Before treating this as a production contract, verify the tokenizer-specific interpretation.

### Emotion Output

Persist:
- emotion label,
- emotion score,
- polarity.

Acceptance:
- valid text reaches inference,
- the 28-dimensional model output is represented,
- polarity mapping is deterministic according to the stated rule.

---

## Phase 6 — MongoDB Persistence

### Change CHG-006

Implement persistence for the confirmed `posts` document shape.

Required top-level areas:

```text
_id
platform
external_id
timestamp
author
content
analytics
engagement
```

Acceptance:
- processed posts can be stored,
- existing fields are preserved,
- duplicate handling is explicitly considered,
- connection/index configuration remains an implementation decision if not already specified.

---

## Phase 7 — Neo4j Graph Persistence

### Change CHG-007

Implement the confirmed graph representation:

```text
(:User {id, handle, platform})
(:Topic {name})

(:User)-[:INTERACTED {type, timestamp, weight}]->(:User)
```

Acceptance:
- graph relationships can be persisted,
- graph queries can support network analytics,
- centrality/weight filtering can be surfaced to the API.

Do not invent additional graph semantics without documenting them as implementation gaps.

---

# 5. REST API

## Change CHG-008

Implement the confirmed endpoints.

### API-001

`GET /api/v1/analytics/timeline`

Returns:
- time-bucketed counts,
- average sentiment,
- top 3 dominant emotions.

### API-002

`GET /api/v1/analytics/network-graph`

Returns:
- nodes,
- links,
- filters by centrality and weight.

### API-003

`GET /api/v1/analytics/demographics`

Returns:
- country breakdown,
- language breakdown,
- profession breakdown.

### API-004

`GET /api/v1/topics/trending`

Returns:
- ranked topics,
- velocity/acceleration ordering.

### Contract Rule

Exact query parameters, pagination, authentication headers, error schema, and exact JSON envelope are not fully established by the source. Do not present invented fields as confirmed.

---

# 6. WebSocket / Realtime Layer

## Change CHG-009

Implement FastAPI WebSockets to deliver the established event types:

```text
event:new_post
event:trend_spike
event:graph_delta
```

The frontend filtering workflow must support:
- topic,
- time window,
- severity.

The source indicates that WebSocket criteria are dispatched when an analyst changes the dashboard filter state.

### Missing Contract

Exact:
- event envelope,
- payload schema,
- reconnection behavior,
- authorization,
- heartbeat,
- fan-out strategy

are not specified.

These are implementation decisions and must be documented.

---

# 7. Dashboard UI

## Change CHG-010 — Timeline

Implement the timeline scrubber with Recharts.

Required:
- area/line visualization,
- sentiment polarity over time,
- time-window interaction.

Acceptance:
- historical timeline data is retrieved from the backend,
- changes in the time window update the view,
- loading/error/empty states exist.

---

## Change CHG-011 — Network Topology

Implement the force-directed graph with `react-force-graph-2d`.

Required:
- nodes,
- links,
- PageRank-scaled node sizing,
- community-cluster coloring.

Acceptance:
- graph data loads from the backend,
- centrality/weight filtering is reflected,
- large or empty graph states are handled.

---

## Change CHG-012 — Demographics

Implement:
- geographic density choropleth,
- professional-sector donut charts.

Data source:
`GET /api/v1/analytics/demographics`

Acceptance:
- aggregated country/language/profession information renders,
- empty and unavailable-data states are handled.

---

## Change CHG-013 — Raw Surveillance Feed

Implement a live scrolling feed for incoming posts.

Data source:
`event:new_post`

Acceptance:
- new posts appear dynamically,
- feed does not freeze the page,
- malformed events do not crash the dashboard.

---

# 8. Trend Analytics

## Change CHG-014

Implement the established velocity-spike rule:

```text
velocity > 2.5
AND
sample size > 50
```

When the rule is met:
- classify the topic as a trend spike,
- expose it through the realtime event channel.

No additional prediction algorithm should be invented beyond what the source establishes.

---

# 9. Frontend/Backend Type Contract

## Change CHG-015

Create strongly typed TypeScript interfaces corresponding to backend response schemas.

At minimum represent:
- timeline aggregates,
- network graph nodes/links,
- demographic aggregates,
- trending topics,
- raw post events,
- trend spikes,
- graph deltas.

Where the backend contract is still unspecified, isolate the schema behind a clearly documented interface.

---

# 10. Security

## Change CHG-016

Address the identified security gap before production exposure.

Required design review:
- backend API authentication,
- rate limiting,
- secret management,
- input validation,
- safe error responses,
- secure external API credentials.

Important:
Authentication and authorization were not specified as an existing dashboard requirement. Any implementation chosen here is a security/production decision, not a confirmed original product feature.

---

# 11. Performance

## Change CHG-017

Preserve the stated performance requirements:

- live WebSocket updates,
- text truncation before model inference,
- sub-20ms inference target as stated in the source.

Do not claim end-to-end sub-20ms latency unless actually measured.

Validation must measure:
- inference latency,
- API latency,
- WebSocket delivery latency where practical.

---

# 12. Fallback Data

## Change CHG-018

Implement the proposed archive fallback as an explicitly optional resilience mechanism.

Possible source archive:
- Sentiment140,
- COVID-19 Twitter stream JSON,
- or another project-approved pre-ingested JSON archive.

Status:
**PROPOSED — NOT A CONFIRMED CORE REQUIREMENT**

Use it for a live pitch/demo fallback only if the team approves the dataset and legal/use constraints.

---

# 13. Testing

## Change CHG-019

Test the system at relevant levels.

### Frontend
- component tests,
- API integration tests,
- dashboard interaction tests.

### Backend
- inference/polarity unit tests,
- API tests,
- WebSocket tests,
- persistence integration tests.

### End-to-End
Validate:
1. ingestion,
2. stream publication,
3. inference,
4. persistence,
5. API retrieval,
6. WebSocket event,
7. dashboard rendering.

---

# 14. Open Decisions Before Production

The following remain unresolved in the supplied source:

- X integration choice,
- dashboard authentication model,
- API rate limiting,
- exact deployment infrastructure,
- exact MongoDB and Neo4j indexes,
- exact WebSocket payload contracts,
- exact permission model,
- exact implementation of desirable platforms,
- exact 512-length interpretation.

These must not be silently finalized as established product requirements.

---

# 15. Definition of Done

The Phase-1 dashboard is considered implementation-complete only when:

- Telegram ingestion works,
- X ingestion is implemented according to an explicitly selected integration,
- raw events reach Redis Streams,
- AI inference produces the required emotion outputs,
- polarity mapping works,
- processed data is persisted,
- MongoDB-backed analytics are available,
- Neo4j-backed graph analytics are available,
- FastAPI REST endpoints work,
- FastAPI WebSocket events work,
- React + TypeScript dashboard renders all required widgets,
- live feed works,
- error/loading/empty states are handled,
- tests pass,
- build/type checks pass,
- security gaps are addressed or explicitly documented.
