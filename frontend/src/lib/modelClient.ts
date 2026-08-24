/** Optional Colab / FastAPI emotion service. IMPLEMENTATION — not a source contract. */

export const GO_EMOTION_LABELS = [
  'admiration',
  'amusement',
  'anger',
  'annoyance',
  'approval',
  'caring',
  'confusion',
  'curiosity',
  'desire',
  'disappointment',
  'disapproval',
  'disgust',
  'embarrassment',
  'excitement',
  'fear',
  'gratitude',
  'grief',
  'joy',
  'love',
  'nervousness',
  'optimism',
  'pride',
  'realization',
  'relief',
  'remorse',
  'sadness',
  'surprise',
  'neutral',
] as const

export type GoEmotionLabel = (typeof GO_EMOTION_LABELS)[number]

export type PolarityBucket = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'

export interface EmotionBar {
  label: string
  score: number
  bucket: PolarityBucket
}

const POSITIVE = new Set([
  'admiration',
  'amusement',
  'approval',
  'caring',
  'desire',
  'excitement',
  'gratitude',
  'joy',
  'love',
  'optimism',
  'pride',
  'relief',
])

const NEGATIVE = new Set([
  'anger',
  'annoyance',
  'disappointment',
  'disapproval',
  'disgust',
  'embarrassment',
  'fear',
  'grief',
  'nervousness',
  'remorse',
  'sadness',
])

export function bucketForLabel(label: string): PolarityBucket {
  const key = label.toLowerCase()
  if (POSITIVE.has(key)) {
    return 'POSITIVE'
  }
  if (NEGATIVE.has(key)) {
    return 'NEGATIVE'
  }
  return 'NEUTRAL'
}

function modelBaseUrl(): string {
  const raw = import.meta.env.VITE_MODEL_URL
  if (typeof raw === 'string' && raw.length > 0) {
    return raw.replace(/\/$/, '')
  }
  return ''
}

export function isModelConfigured(): boolean {
  return modelBaseUrl().length > 0
}

interface RemoteEmotion {
  label?: unknown
  score?: unknown
}

interface RemoteBody {
  emotions?: RemoteEmotion[]
}

export async function predictEmotions(text: string): Promise<EmotionBar[] | null> {
  const base = modelBaseUrl()
  if (!base) {
    return null
  }
  const response = await fetch(`${base}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    throw new Error(`Model HTTP ${response.status}`)
  }
  const body = (await response.json()) as RemoteBody
  if (!Array.isArray(body.emotions)) {
    throw new Error('Model response missing emotions[]')
  }
  return body.emotions
    .map((row) => {
      const label = typeof row.label === 'string' ? row.label : ''
      const score = typeof row.score === 'number' ? row.score : Number.NaN
      return {
        label,
        score,
        bucket: bucketForLabel(label),
      }
    })
    .filter((row) => row.label.length > 0 && Number.isFinite(row.score))
    .sort((a, b) => b.score - a.score)
}

/** Preview vector for the UI when Colab is not connected. Not claimed as model output. */
export function previewEmotions(text: string): EmotionBar[] {
  let hash = 0
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 33 + text.charCodeAt(i)) >>> 0
  }
  return GO_EMOTION_LABELS.map((label, index) => {
    const wave = ((hash >> (index % 16)) & 15) / 15
    const score = Number((0.03 + ((wave + index * 0.01) % 1) * 0.28).toFixed(3))
    return { label, score, bucket: bucketForLabel(label) }
  }).sort((a, b) => b.score - a.score)
}
