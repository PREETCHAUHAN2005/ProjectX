---
name: sentiment-analysis
description: Implement the Python NLP pipeline — regex/URL preprocess, SamLowe/roberta-base-go_emotions, 28-d emotion vector, polarity mapping, BERTopic, spaCy NER demographics, and the velocity trend-spike rule. Use when working on inference workers, emotion/sentiment, clustering, NER, polarity, or trend spikes.
---

# Sentiment analysis

Playbook for `workers/` AI inference. Model substitution is forbidden.

## Checklist

```
- [ ] Consume stream:social:raw
- [ ] Preprocess: regex clean, strip URLs, truncate before the model
- [ ] Run SamLowe/roberta-base-go_emotions (28-d multi-label)
- [ ] Map dominant emotion → POSITIVE | NEGATIVE | NEUTRAL
- [ ] BERTopic clustering; spaCy NER profiler
- [ ] Persist analytics onto the posts document / graph as applicable
- [ ] Trend spike: velocity > 2.5 AND sample size > 50 → event:trend_spike
- [ ] Unit tests for polarity and spike rule
```

## Pipeline order

```text
raw_text → clean → truncate → RoBERTa GoEmotions
        → polarity from dominant emotion
        → BERTopic (topic_id, topic_name)
        → spaCy NER (demographic hints)
        → MongoDB posts + Neo4j as needed
```

Do not skip preprocessing. Do not call a different HF model “equivalent.”

## Truncation (open decision)

Source mentions `512` max length and `truncation=True`. **Verify tokenizer semantics** before treating 512 as characters vs tokens.

Until verified: use the model tokenizer with `truncation=True` and `max_length=512` (Hugging Face token convention). Document this in code comments as an implementation choice. Never claim the source settled character vs token.

## Polarity

After the 28-d vector, take the **dominant** non-`neutral` emotion (highest score). Map via [polarity-map.md](polarity-map.md). If dominant is `neutral` or the mapped bucket is unclear → `NEUTRAL`.

Persist:

- `analytics.sentiment.label` (`POSITIVE` | `NEGATIVE` | `NEUTRAL`)
- `analytics.sentiment.score`
- `analytics.emotions[]` with `label` + `score` (full 28-d represented, not a single substitute label)

Do not invent extra polarity values (`MIXED`, 1–5 stars, etc.).

## BERTopic / spaCy

Use BERTopic for clustering and spaCy NER for aggregate, anonymized demographic hints (`inferred_country`, `inferred_region`, `inferred_profession`, `confidence`). Do not store identifiable profiling beyond the confirmed `posts.analytics.demographics` fields.

## Trend spike

Flag a topic only when **both** are true: `velocity > 2.5` and `sample size > 50`. Then publish `event:trend_spike`. Do not add another predictor.

## Performance

Optimize inference toward the stated sub-20ms target. **Do not claim it was achieved** unless benchmarked in this repo. Truncate *before* the forward pass.

## Tests

- Deterministic polarity for joy/love → `POSITIVE`, fear/anger → `NEGATIVE`
- Spike rule boundary: `n=50` false, `n=51` and `velocity=2.51` true
- Empty/whitespace text does not crash; no fake emotions on failure
