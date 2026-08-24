---
name: production-review
description: Run the ProjectX Definition of Done, security/production gap, performance claims, open-decision audit, and multi-role self-review before calling a feature or Phase 1 complete. Use when reviewing for ship, merge, production readiness, or writing the end-of-cycle report.
---

# Production review

Final gate from `cursor-agent-prompt.md` and `changes.md` Definition of Done. Follow **all** `.cursor/rules/` during this review.

## Checklist (copy and tick)

```
[ ] Requirement implemented (CHG / feature id)
[ ] API contract verified (data-contract-review)
[ ] Typecheck passed (actually run)
[ ] Lint passed where configured (actually run)
[ ] Relevant tests passed (actually run)
[ ] Production build succeeded (frontend) / app imports (backend)
[ ] Error handling reviewed at I/O boundaries
[ ] Security reviewed (CHG-016)
[ ] Responsive UI / empty-load-error states
[ ] No regression on adjacent widgets or routes
[ ] Implementation choices documented; open decisions not fake-confirmed
```

If a box was not executed, leave it unchecked and say so.

## Security / production gap (`CHG-016`)

Must explicitly record status of:

- backend API authentication
- rate limiting
- secret management
- input validation
- safe error responses
- external API credentials (Telegram, X, HF)

Auth for the analyst dashboard was **not** a specified product feature. If you added it, label it `PRODUCTION DECISION`. If you did not, label API auth/rate-limit as `SHIP BLOCKER` or `ACCEPTED RISK` with owner — do not stay silent.

## Performance (`CHG-017`)

Confirm live WS updates and pre-inference truncation. Quote sub-20ms **only** with a measured number from this repo. Do not treat end-to-end latency as specified.

## Open decisions (must remain explicit)

X ingestion choice · dashboard auth · rate-limit policy · deploy infra · Mongo/Neo4j indexes · WS payload schema · 512 length interpretation · dashboard permission model · Instagram/Facebook/YouTube.

## Rejected / out of scope

- Phase-1 Reddit
- Node/Express/Socket.io gateway
- Optional archive datasets as the primary path (`CHG-018`) unless flagged and legally approved

## Role pass (fix what you find)

| Role | Ask |
|---|---|
| Product | Does the analyst get timeline, graph, demographics, live feed, trends? |
| Architect | Still FastAPI+WS, Redis, Mongo, Neo4j, GoEmotions, Telethon? |
| Engineer | Modules separated; no secret in source? |
| ML | Model, 28-d vector, polarity map, spike rule intact? |
| Security | Abuse, XSS, injection, credential leak, unauthenticated prod API? |
| QA | Failure, empty, disconnect, malformed event? |
| UX | Filters update all views; UI usable without fake data? |

## Phase-1 complete only if

Telegram ingestion works; X path exists behind an **explicit** choice; events hit `stream:social:raw`; inference + polarity persist; Mongo analytics + Neo4j graph APIs work; FastAPI REST+WS work; dashboard widgets + live feed; tests and type/build checks pass; security gap addressed or documented.

## Report template

Use the **FINAL REPORT** sections in `cursor-agent-prompt.md`: Implemented, Files created/modified, Dependencies, Env vars (names only), Validation, Remaining, Risks.
