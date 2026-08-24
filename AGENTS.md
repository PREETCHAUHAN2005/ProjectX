# ProjectX — Agent Instructions

**Product:** AI-Driven Social Media Analytics Framework (SIH 2026, NTRO, problem 26152)  
**Stack:** React + TypeScript dashboard · FastAPI + native WebSockets · Redis Streams · MongoDB · Neo4j · RoBERTa GoEmotions · Telethon

This file is the router. Specs define *what* to build. Rules define *constraints*. Skills define *how* to do a class of work.

## Source of truth (read in this order)

1. The current user/project request
2. This repository as it actually exists
3. [cursor.md](cursor.md) — product, architecture, confirmed vs open
4. [changes.md](changes.md) — implementation contract (`CHG-000` … `CHG-019`)
5. [cursor-agent-prompt.md](cursor-agent-prompt.md) — operating protocol, phases, validation gate
6. `.cursor/rules/*.mdc` — MUST / MUST NOT
7. `.cursor/skills/<name>/SKILL.md` — playbook for that work

Never invent a requirement. If the source is silent, implement only what is needed to proceed, document the choice, and do not label it “confirmed.”

Priority when they conflict: **user request > repo reality > established architecture > cursor.md > changes.md > convention > assumption.**

## Repository reality

Inspect before every substantial change (`CHG-000`). Classify areas as `COMPLETE | PARTIAL | BROKEN | MISSING | DEPRECATED | UNKNOWN`.

**Greenfield:** this workspace had no application code when the agent stack was created (no `package.json`, no FastAPI app, no tests). Until code exists, create it in the target layout in `.cursor/rules/architecture.mdc`. Do not copy Node/Express, Manus, or AgentGuard patterns from sibling folders.

## Route: rules vs skills

**Rules** are always-on or glob-scoped constraints. Follow them; do not restate them as essays.  
**Skills** are procedural playbooks. Read `SKILL.md` *before* implementing that kind of work. Read a skill’s extra files only when needed.

| When the work is… | Rules | Skill |
|---|---|---|
| Any change | `architecture`, `security` | — |
| React, TypeScript, Tailwind, Recharts, force-graph, dashboard widgets | `architecture`, `react-typescript`, `security` | `dashboard` |
| FastAPI app, REST `/api/v1/*`, native WebSockets, config, Python API | `architecture`, `fastapi-python`, `security` | `fastapi-production` |
| Telegram, X/Twitter, Redis `stream:social:raw`, ingestion workers | `architecture`, `fastapi-python`, `security` | `social-ingestion` |
| Preprocess, GoEmotions, polarity, BERTopic, spaCy NER, trend-spike rule | `architecture`, `fastapi-python` | `sentiment-analysis` |
| MongoDB `posts`, Neo4j graph, REST/WS envelopes, TS ↔ Pydantic parity | `architecture`, `react-typescript`, `fastapi-python` | `data-contract-review` |
| Tests (unit, API, WS, component, E2E) | `testing` + the stack rule for the code under test | — |
| Ship / review / DoD / security-prod gap | all five rules | `production-review` |

Skill paths: `.cursor/skills/<skill-name>/SKILL.md`

## Implementation order

Follow `cursor-agent-prompt.md`: inspect → frontend foundation → FastAPI foundation → Telegram → X adapter → Redis Streams → AI pipeline → MongoDB → Neo4j → REST → WebSockets → dashboard widgets → tests → production review.

Do not start a broad rewrite before Phase 0 inspection.

## Hard stops

- Do not use Node.js / Express / Socket.io as the API or realtime gateway.
- Do not implement Phase-1 Reddit ingestion.
- Do not substitute a different emotion model for `SamLowe/roberta-base-go_emotions`.
- Do not claim sub-20ms inference unless measured in this repo.
- Do not commit secrets, and do not commit unless the user asked.
- Do not silently finalize open decisions listed in `cursor.md`.

## After an implementation cycle

Report using the template in `cursor-agent-prompt.md` (Implemented, Files, Dependencies, Env vars without secret values, Validation actually run, Remaining, Risks). Never claim a check passed if it was not executed.
