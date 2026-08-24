import type {
  ApiErrorBody,
  DemographicsResponse,
  HealthResponse,
  NetworkGraphQuery,
  NetworkGraphResponse,
  TimelineQuery,
  TimelineResponse,
  TrendingResponse,
} from '../types/contracts'
import { apiBaseUrl } from './config'

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

async function getJson<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${apiBaseUrl()}${path}`)
  } catch (cause) {
    throw new ApiError(0, 'Network error contacting API')
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = (await response.json()) as ApiErrorBody
      if (typeof body.detail === 'string' && body.detail.length > 0) {
        detail = body.detail
      }
    } catch {
      // keep generic detail; never surface stack traces
    }
    throw new ApiError(response.status, detail)
  }

  return (await response.json()) as T
}

export function getHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>('/health')
}

export function getTimeline(query: TimelineQuery = {}): Promise<TimelineResponse> {
  return getJson<TimelineResponse>(
    `/api/v1/analytics/timeline${queryString({
      from: query.from,
      to: query.to,
      bucket: query.bucket,
      topic: query.topic,
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
    })}`,
  )
}

export function getDemographics(topic?: string): Promise<DemographicsResponse> {
  return getJson<DemographicsResponse>(
    `/api/v1/analytics/demographics${queryString({ topic })}`,
  )
}

export function getTrending(limit?: number): Promise<TrendingResponse> {
  return getJson<TrendingResponse>(
    `/api/v1/topics/trending${queryString({ limit })}`,
  )
}
