import type {
  GraphDeltaPayload,
  NewPostPayload,
  TrendSpikePayload,
  WsEnvelope,
} from '../types/contracts'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

export function isNewPostPayload(value: unknown): value is NewPostPayload {
  if (!isRecord(value) || !isRecord(value.author) || !isRecord(value.content)) {
    return false
  }
  return (
    (value.platform === 'telegram' || value.platform === 'x') &&
    typeof value.external_id === 'string' &&
    typeof value.timestamp === 'string' &&
    typeof value.author.handle === 'string' &&
    typeof value.content.raw_text === 'string'
  )
}

export function isTrendSpikePayload(value: unknown): value is TrendSpikePayload {
  return (
    isRecord(value) &&
    typeof value.topic_id === 'string' &&
    typeof value.topic_name === 'string' &&
    typeof value.velocity === 'number' &&
    typeof value.sample_size === 'number'
  )
}

export function isGraphDeltaPayload(value: unknown): value is GraphDeltaPayload {
  return isRecord(value) && Array.isArray(value.nodes) && Array.isArray(value.links)
}

export function payloadForEvent(envelope: WsEnvelope): unknown {
  return envelope.payload
}
