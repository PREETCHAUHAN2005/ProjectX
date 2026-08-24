# GoEmotions polarity map

Source-confirmed examples: joy/love → positive; fear/anger → negative. The remaining labels are an **implementation contract** so mapping stays deterministic — not a source-confirmed table. Do not silently change buckets.

Output taxonomy: `POSITIVE` | `NEGATIVE` | `NEUTRAL` only.

Model: `SamLowe/roberta-base-go_emotions` (28 labels).

| Label | Bucket |
|---|---|
| admiration | POSITIVE |
| amusement | POSITIVE |
| anger | NEGATIVE |
| annoyance | NEGATIVE |
| approval | POSITIVE |
| caring | POSITIVE |
| confusion | NEUTRAL |
| curiosity | NEUTRAL |
| desire | POSITIVE |
| disappointment | NEGATIVE |
| disapproval | NEGATIVE |
| disgust | NEGATIVE |
| embarrassment | NEGATIVE |
| excitement | POSITIVE |
| fear | NEGATIVE |
| gratitude | POSITIVE |
| grief | NEGATIVE |
| joy | POSITIVE |
| love | POSITIVE |
| nervousness | NEGATIVE |
| optimism | POSITIVE |
| pride | POSITIVE |
| realization | NEUTRAL |
| relief | POSITIVE |
| remorse | NEGATIVE |
| sadness | NEGATIVE |
| surprise | NEUTRAL |
| neutral | NEUTRAL |

Rule: dominant label by score → bucket above. If scores tie, prefer `NEUTRAL` rather than inventing a tie-break product rule.
