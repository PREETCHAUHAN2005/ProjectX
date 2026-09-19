import type {
  ApiErrorBody,
  DemographicsResponse,
  HealthResponse,
  IngestResponse,
  NetworkGraphQuery,
  NetworkGraphResponse,
  NlpPredictResponse,
  RecentFeedResponse,
  TimelineQuery,
  TimelineResponse,
  TrendingResponse,
} from '../types/contracts'
import { apiBaseUrl } from './config'

/** Convert datetime-local values to ISO so REST time filters compare correctly. */
export function toIsoParam(value?: string): string | undefined {
  if (!value) {
    return undefined
  }
  if (/[zZ]$/.test(value) || /[+-]\d{2}:\d{2}$/.test(value)) {
    return value
  }
  const parsed = Date.parse(value)
  if (Number.isNaN(parsed)) {
    return undefined
  }
  return new Date(parsed).toISOString()
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === '') {
      continue
    }
    search.set(key, String(value))
  }
  const encoded = search.toString()
  return encoded.length > 0 ? `?${encoded}` : ''
}

async function parseError(response: Response): Promise<string> {
  let detail = `Request failed (${response.status})`
  try {
    const body = (await response.json()) as ApiErrorBody
    if (typeof body.detail === 'string' && body.detail.length > 0) {
      detail = body.detail
    }
  } catch {
    // keep generic detail; never surface stack traces
  }
  return detail
}

async function fetchWithTimeout(path: string, init?: RequestInit, timeoutMs = 8000): Promise<Response> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fetch(`${apiBaseUrl()}${path}`, { ...init, signal: controller.signal })
  } finally {
    window.clearTimeout(timer)
  }
}

async function getJson<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetchWithTimeout(path)
  } catch {
    throw new ApiError(0, 'Network error contacting API')
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }

  return (await response.json()) as T
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetchWithTimeout(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }, 20000)
  } catch {
    throw new ApiError(0, 'Network error contacting API')
  }
  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }
  return (await response.json()) as T
}

export function getHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>('/health')
}

export function getTimeline(query: TimelineQuery = {}): Promise<TimelineResponse> {
  return getJson<TimelineResponse>(
    `/api/v1/analytics/timeline${queryString({
      from: toIsoParam(query.from),
      to: toIsoParam(query.to),
      bucket: query.bucket,
      topic: query.topic,
      severity: query.severity,
    })}`,
  )
}

export function getNetworkGraph(
  query: NetworkGraphQuery = {},
): Promise<NetworkGraphResponse> {
  return getJson<NetworkGraphResponse>(
    `/api/v1/analytics/network-graph${queryString({
      min_centrality: query.min_centrality,
      min_weight: query.min_weight,
      topic: query.topic,
      severity: query.severity,
    })}`,
  )
}

export function getDemographics(
  topic?: string,
  severity?: string,
): Promise<DemographicsResponse> {
  return getJson<DemographicsResponse>(
    `/api/v1/analytics/demographics${queryString({ topic, severity })}`,
  )
}

export function getTrending(limit?: number): Promise<TrendingResponse> {
  return getJson<TrendingResponse>(
    `/api/v1/topics/trending${queryString({ limit })}`,
  )
}

export function getRecentFeed(limit = 40): Promise<RecentFeedResponse> {
  return getJson<RecentFeedResponse>(
    `/api/v1/feed/recent${queryString({ limit })}`,
  )
}

export function runIngest(query?: string, limit = 12): Promise<IngestResponse> {
  return postJson<IngestResponse>('/api/v1/ingest/run', { query, limit })
}

export function predictNlp(text: string): Promise<NlpPredictResponse> {
  return postJson<NlpPredictResponse>('/api/v1/nlp/predict', { text })
}
