---
name: data-contract-review
description: Review and keep MongoDB posts, Neo4j graph, FastAPI Pydantic models, and TypeScript interfaces consistent. Use when changing API JSON, WebSocket envelopes, database documents, graph properties, or frontend types — and when checking confirmed vs invented fields.
---

# Data contract review

Use this skill whenever a field, endpoint, or event payload changes. Confirmed shapes: [contracts.md](contracts.md).

## Checklist

```
- [ ] List fields the source confirmed vs implementation-only
- [ ] MongoDB posts top-level areas match cursor.md
- [ ] Neo4j User / Topic / INTERACTED only (unless gap is documented)
- [ ] Pydantic models ↔ TypeScript interfaces (same names and nullability)
- [ ] REST purpose matches CHG-008 (no silent extra product APIs)
- [ ] WS event names exact; envelope documented if invented
- [ ] No `any`, no extra polarity labels, no extra graph rel types
```

## Review steps

1. **Read source** — `cursor.md` Data Model + Backend API Contract; `changes.md` CHG-006–009, CHG-015.
2. **Diff repo** — Pydantic schemas, TS types, Mongo writes, Cypher.
3. **Classify each field**
   - `CONFIRMED` — in cursor.md / changes.md
   - `IMPLEMENTATION` — needed, documented, consistent FE/BE
   - `INVENTED-AS-CONFIRMED` — **must fix** (rename comments / docs)
4. **Parity** — every REST/WS payload the UI consumes has a TS interface and a Pydantic model. Optional source fields stay optional in both.
5. **Duplicates** — `platform` + `external_id` uniqueness must be an explicit decision (upsert vs insert). Index details are open; document the choice.
6. **Report** — table of mismatches; do not “fix” open decisions by pretending the source specified them.

## Hard constraints

- Polarity strings: `POSITIVE` | `NEGATIVE` | `NEUTRAL`
- WS event type strings: `event:new_post` | `event:trend_spike` | `event:graph_delta`
- Mongo top-level: `_id`, `platform`, `external_id`, `timestamp`, `author`, `content`, `analytics`, `engagement`
- Neo4j: `(:User {id, handle, platform})`, `(:Topic {name})`, `(:User)-[:INTERACTED {type, timestamp, weight}]->(:User)`

## Output format

```text
Contract review
- Confirmed preserved: …
- Implementation fields added: … (why)
- Drift to fix: …
- Open decisions still open: …
```
