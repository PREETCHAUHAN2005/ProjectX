---
name: dashboard
description: Build the React TypeScript OSINT dashboard widgets — Recharts timeline, react-force-graph-2d network, demographic choropleth/donuts, live surveillance feed, and WebSocket filter dispatch. Use when working on frontend UI, charts, live feed, analyst filters, or dashboard loading/empty/error states.
---

# Dashboard

Playbook for `frontend/`. Follow `react-typescript.mdc` and `data-contract-review` for types.

## Checklist

```
- [ ] Inspect frontend (or scaffold React+TS+Tailwind if missing)
- [ ] Typed REST + WebSocket clients
- [ ] Timeline (Recharts) from GET /api/v1/analytics/timeline
- [ ] Network (react-force-graph-2d) from GET /api/v1/analytics/network-graph
- [ ] Demographics choropleth + donut from GET /api/v1/analytics/demographics
- [ ] Live feed from event:new_post
- [ ] Filters: topic, time window, severity → WS criteria + refetch
- [ ] Loading / empty / error on every widget
```

## Step 1 — Foundation (`CHG-001`)

If `frontend/` does not exist, scaffold React + TypeScript with Tailwind-compatible styling. Routing only as needed for the dashboard. Typed API and WS clients. **Vite is an implementation choice**, not a source requirement — document it if used. Do not add Redux/Zustand unless necessary.

No Socket.io client.

## Step 2 — Types

Create interfaces for timeline, network graph, demographics, trending topics, `event:new_post`, `event:trend_spike`, `event:graph_delta`. Align with Pydantic models. Unspecified envelopes go in one documented module — never `any`.

## Step 3 — Timeline (`CHG-010`)

Recharts dual-axis area/line: time-bucketed counts and average sentiment polarity. Time-window control updates the query and WS criteria. Handle load/empty/error.

## Step 4 — Network (`CHG-011`)

`react-force-graph-2d`: nodes, links, PageRank-scaled node size, community-cluster color. Honor centrality/weight filters from the API. Guard large and empty graphs.

## Step 5 — Demographics (`CHG-012`)

Choropleth for country density; donut for profession; surface language breakdown. Same empty/unavailable states.

## Step 6 — Live feed (`CHG-013`)

Scrolling feed of `event:new_post`. Cap DOM nodes (windowed/virtualized or max-N). Malformed events: skip and log, do not crash.

## Step 7 — Analyst interaction

On topic / time window / severity change: dispatch WS filter criteria and refresh REST widgets. Do not keep a purely local fake graph that ignores the backend.

## Step 8 — Trending

Consume `GET /api/v1/topics/trending` (velocity/acceleration order) and `event:trend_spike` when wiring alerts/highlights. Thresholds live on the backend — do not reimplement a different spike rule in the UI.

## Done when

All four widgets render from backend contracts (or clearly show empty/error), filters round-trip, and the feed stays responsive.
