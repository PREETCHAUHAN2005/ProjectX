/**
 * Shared frontend/backend contracts.
 *
 * CONFIRMED (cursor.md / changes.md): event names, REST purposes, polarity labels.
 * IMPLEMENTATION: JSON envelopes, query param names, WS filter frame, numeric
 * average_sentiment mapping. Do not treat implementation fields as source-confirmed.
 */

export type Polarity = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
export type Platform = 'telegram' | 'x'

export interface EmotionScore {
  label: string
  score: number
}

/** IMPLEMENTATION query params for GET /api/v1/analytics/timeline */
export interface TimelineQuery {
  from?: string
  to?: string
  bucket?: 'hour' | 'day'
  topic?: string
  severity?: string
}

export interface TimelineBucket {
  timestamp: string
  count: number
  average_sentiment: number
  top_emotions: EmotionScore[]
  /** IMPLEMENTATION split of `count` for posts vs comments. */
  post_count?: number
  comment_count?: number
}

export interface TimelineResponse {
  buckets: TimelineBucket[]
}

/** IMPLEMENTATION query params for GET /api/v1/analytics/network-graph */
export interface NetworkGraphQuery {
  min_centrality?: number
  min_weight?: number
  topic?: string
  severity?: string
}

export interface GraphNode {
  id: string
  handle: string
  platform: string
  pagerank: number
  community: string
}

export interface GraphLink {
  source: string
  target: string
  type: string
  timestamp: string
  weight: number
}

export interface NetworkGraphResponse {
  nodes: GraphNode[]
  links: GraphLink[]
}

export interface DemographicSlice {
  key: string
  count: number
}

export interface DemographicsResponse {
  country: DemographicSlice[]
  language: DemographicSlice[]
  profession: DemographicSlice[]
}

export interface TrendingTopic {
  topic_id: string
  topic_name: string
  velocity: number
  acceleration: number
  sample_size: number
}

export interface TrendingResponse {
  topics: TrendingTopic[]
}

export interface Author {
  user_id: string
  handle: string
  bio?: string
  follower_count?: number
}

export interface NewPostPayload {
  platform: Platform
  external_id: string
  timestamp: string
  author: Author
  content: {
    raw_text: string
    hashtags?: string[]
    language?: string
  }
  /** IMPLEMENTATION extras for the demo live feed (not source-confirmed). */
  topic_id?: string
  topic_name?: string
  severity?: string
  thread_role?: 'post' | 'comment' | string
  in_reply_to?: string
  polarity?: Polarity
  emotions?: EmotionScore[]
}

export interface TrendSpikePayload {
  topic_id: string
  topic_name: string
  velocity: number
  sample_size: number
}

export interface GraphDeltaPayload {
  nodes: GraphNode[]
  links: GraphLink[]
}

export type WsEventName =
  | 'event:new_post'
  | 'event:trend_spike'
  | 'event:graph_delta'

/** IMPLEMENTATION envelope — source confirmed the event names only. */
export interface WsEnvelope {
  event: WsEventName
  payload: NewPostPayload | TrendSpikePayload | GraphDeltaPayload
}

/** IMPLEMENTATION client→server filter frame. */
export interface WsFilterCriteria {
  type: 'filter'
  topic?: string
  time_window?: {
    from?: string
    to?: string
  }
  severity?: string
}

export interface HealthResponse {
  status: string
}

export interface ApiErrorBody {
  detail: string
}
