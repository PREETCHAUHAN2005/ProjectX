import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  getDemographics,
  getHealth,
  getNetworkGraph,
  getRecentFeed,
  getTimeline,
  getTrending,
  runIngest,
  toIsoParam,
} from '../api/client'
import { DashboardSocket } from '../api/wsClient'
import { isGraphDeltaPayload, isNewPostPayload, isTrendSpikePayload } from './guards'
import { fromResult, initialLoad, type LoadState } from './loadState'
import {
  nextPrototypePost,
  prototypeDemographics,
  prototypeFeed,
  prototypeGraph,
  prototypeGraphDelta,
  prototypeSpike,
  prototypeTimeline,
  prototypeTrending,
} from './prototypeData'
import {
  commentCountFromTimeline,
  emotionMixFromTimeline,
  featuredThread,
  postCountFromTimeline,
  topEmotionLabel,
} from './thread'
import { hoursAgo } from './format'
import type {
  DemographicsResponse,
  GraphDeltaPayload,
  HealthResponse,
  NetworkGraphResponse,
  NewPostPayload,
  TimelineResponse,
  TrendingResponse,
  WsEnvelope,
} from '../types/contracts'

export type DataMode = 'live' | 'prototype' | 'offline'

function seedPrototype(): {
  timeline: LoadState<TimelineResponse>
  graph: LoadState<NetworkGraphResponse>
  demographics: LoadState<DemographicsResponse>
  trending: LoadState<TrendingResponse>
} {
  const timeline = prototypeTimeline()
  const graph = prototypeGraph()
  const demographics = prototypeDemographics()
  const trending = prototypeTrending()
  return {
    timeline: fromResult(timeline, timeline.buckets.length === 0),
    graph: fromResult(graph, graph.nodes.length === 0),
    demographics: fromResult(
      demographics,
      demographics.country.length === 0 &&
        demographics.language.length === 0 &&
        demographics.profession.length === 0,
    ),
    trending: fromResult(trending, trending.topics.length === 0),
  }
}

function mergeGraph(
  current: NetworkGraphResponse,
  delta: GraphDeltaPayload,
): NetworkGraphResponse {
  const nodes = [...current.nodes]
  const links = [...current.links]
  const seenNodes = new Set(nodes.map((node) => node.id))
  for (const node of delta.nodes) {
    if (!seenNodes.has(node.id)) {
      nodes.push(node)
      seenNodes.add(node.id)
    }
  }
  const seenLinks = new Set(links.map((link) => `${link.source}->${link.target}`))
  for (const link of delta.links) {
    const key = `${link.source}->${link.target}`
    if (!seenLinks.has(key)) {
      links.push(link)
      seenLinks.add(key)
    }
  }
  return { nodes, links }
}

function failed<T>(message: string): LoadState<T> {
  return { status: 'error', data: null, error: message }
}

export function useDashboard() {
  const [topic, setTopic] = useState('')
  const [from, setFrom] = useState(() => hoursAgo(24))
  const [to, setTo] = useState(() => hoursAgo(0))
  const [severity, setSeverity] = useState('')
  const [preferPrototype, setPreferPrototype] = useState(false)
  const [dataMode, setDataMode] = useState<DataMode>('live')
  const [apiStatus, setApiStatus] = useState('checking')
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [feed, setFeed] = useState<NewPostPayload[]>([])
  const [spikeNotice, setSpikeNotice] = useState<string | null>(null)
  const [fetchNotice, setFetchNotice] = useState<string | null>(null)
  const [fetching, setFetching] = useState(false)
  const [timeline, setTimeline] = useState<LoadState<TimelineResponse>>(initialLoad)
  const [graph, setGraph] = useState<LoadState<NetworkGraphResponse>>(initialLoad)
  const [demographics, setDemographics] =
    useState<LoadState<DemographicsResponse>>(initialLoad)
  const [trending, setTrending] = useState<LoadState<TrendingResponse>>(initialLoad)
  const tick = useRef(0)
  const liveFeedReset = useRef(false)
  const refreshTimer = useRef<number | null>(null)

  const applyPrototype = useCallback(() => {
    const proto = seedPrototype()
    setTimeline(proto.timeline)
    setGraph(proto.graph)
    setDemographics(proto.demographics)
    setTrending(proto.trending)
    setDataMode('prototype')
    setApiStatus('preview')
    setFeed(prototypeFeed())
  }, [])

  const refreshAnalytics = useCallback(async (): Promise<void> => {
    const query = {
      topic: topic || undefined,
      from: toIsoParam(from),
      to: toIsoParam(to),
      severity: severity || undefined,
    }
    const [timelineData, graphData, demoData, trendingData] = await Promise.all([
      getTimeline({ ...query, bucket: 'hour' }),
      getNetworkGraph({ topic: query.topic, severity: query.severity }),
      getDemographics(query.topic, query.severity),
      getTrending(),
    ])
    setTimeline(fromResult(timelineData, timelineData.buckets.length === 0))
    setGraph(fromResult(graphData, graphData.nodes.length === 0))
    setDemographics(
      fromResult(
        demoData,
        demoData.country.length === 0 &&
          demoData.language.length === 0 &&
          demoData.profession.length === 0,
      ),
    )
    setTrending(fromResult(trendingData, trendingData.topics.length === 0))
  }, [from, severity, to, topic])

  const scheduleAnalyticsRefresh = useCallback(() => {
    if (refreshTimer.current !== null) {
      window.clearTimeout(refreshTimer.current)
    }
    refreshTimer.current = window.setTimeout(() => {
      void refreshAnalytics().catch(() => undefined)
    }, 2000)
  }, [refreshAnalytics])

  const load = useCallback(async (): Promise<void> => {
    setTimeline(initialLoad())
    setGraph(initialLoad())
    setDemographics(initialLoad())
    setTrending(initialLoad())

    if (preferPrototype) {
      applyPrototype()
      return
    }

    try {
      const nextHealth = await getHealth()
      setHealth(nextHealth)
      setApiStatus(nextHealth.status)
    } catch {
      setHealth(null)
      setDataMode('offline')
      setApiStatus('unreachable')
      setFeed([])
      const message = 'API unreachable. Start the local backend on port 8000.'
      setTimeline(failed(message))
      setGraph(failed(message))
      setDemographics(failed(message))
      setTrending(failed(message))
      return
    }

    try {
      await refreshAnalytics()
      const recent = await getRecentFeed(40)
      setFeed(recent.posts)
      setDataMode('live')
    } catch {
      const message = 'Analytics request failed'
      setTimeline(failed(message))
      setGraph(failed(message))
      setDemographics(failed(message))
      setTrending(failed(message))
      setDataMode('offline')
      setApiStatus('error')
    }
  }, [applyPrototype, preferPrototype, refreshAnalytics])

  const fetchPosts = useCallback(async (): Promise<void> => {
    setFetching(true)
    setFetchNotice(null)
    try {
      const result = await runIngest(topic || undefined, 12)
      setFetchNotice(`Ingested ${result.accepted} posts via ${result.source}`)
      await refreshAnalytics()
      const recent = await getRecentFeed(40)
      setFeed(recent.posts)
      setDataMode('live')
    } catch {
      setFetchNotice('Ingest failed — backend may be down')
    } finally {
      setFetching(false)
    }
  }, [refreshAnalytics, topic])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    return () => {
      if (refreshTimer.current !== null) {
        window.clearTimeout(refreshTimer.current)
      }
    }
  }, [])

  useEffect(() => {
    if (dataMode === 'prototype') {
      setWsStatus('preview')
      const timer = window.setInterval(() => {
        tick.current += 1
        setFeed((current) => [nextPrototypePost(tick.current), ...current].slice(0, 50))
        if (tick.current % 6 === 0) {
          const spike = prototypeSpike()
          setSpikeNotice(`${spike.topic_name} · velocity ${spike.velocity.toFixed(1)}`)
          const delta = prototypeGraphDelta()
          setGraph((current) => {
            if (current.data === null) {
              return current
            }
            return {
              status: 'ready',
              data: mergeGraph(current.data, delta),
              error: null,
            }
          })
        }
      }, 4500)
      return () => {
        window.clearInterval(timer)
      }
    }

    if (dataMode === 'offline') {
      setWsStatus('disconnected')
      return
    }

    const socket = new DashboardSocket({
      onOpen: () => {
        setWsStatus('connected')
        liveFeedReset.current = true
        socket.sendFilter({
          type: 'filter',
          topic: topic || undefined,
          time_window: {
            from: toIsoParam(from),
            to: toIsoParam(to),
          },
          severity: severity || undefined,
        })
      },
      onClose: () => {
        setWsStatus('disconnected')
      },
      onError: () => {
        setWsStatus('error')
      },
      onMalformed: () => undefined,
      onEvent: (envelope: WsEnvelope) => {
        if (envelope.event === 'event:new_post') {
          const incoming = envelope.payload
          if (!isNewPostPayload(incoming)) {
            return
          }
          setFeed((current) => {
            const next = liveFeedReset.current ? [] : current
            liveFeedReset.current = false
            const exists = next.some(
              (item) =>
                item.platform === incoming.platform && item.external_id === incoming.external_id,
            )
            if (exists) {
              return next
            }
            return [incoming, ...next].slice(0, 50)
          })
          scheduleAnalyticsRefresh()
          return
        }
        if (envelope.event === 'event:trend_spike') {
          const payload = envelope.payload
          if (!isTrendSpikePayload(payload)) {
            return
          }
          setSpikeNotice(`${payload.topic_name} · velocity ${payload.velocity.toFixed(1)}`)
          scheduleAnalyticsRefresh()
          return
        }
        if (envelope.event === 'event:graph_delta') {
          const payload = envelope.payload
          if (!isGraphDeltaPayload(payload)) {
            return
          }
          setGraph((current) => {
            if (current.data === null) {
              return fromResult(payload, payload.nodes.length === 0)
            }
            return {
              status: 'ready',
              data: mergeGraph(current.data, payload),
              error: null,
            }
          })
        }
      },
    })
    liveFeedReset.current = true
    socket.connect()
    return () => {
      socket.disconnect()
    }
  }, [dataMode, from, scheduleAnalyticsRefresh, severity, to, topic])

  const emotions = useMemo(() => emotionMixFromTimeline(timeline.data), [timeline.data])
  const thread = useMemo(() => featuredThread(feed), [feed])

  const metrics = useMemo(() => {
    return {
      posts: postCountFromTimeline(timeline.data),
      comments: commentCountFromTimeline(timeline.data),
      topEmotion: topEmotionLabel(emotions),
      topics: trending.data?.topics.length ?? 0,
    }
  }, [emotions, timeline.data, trending.data])

  return {
    topic,
    setTopic,
    from,
    setFrom,
    to,
    setTo,
    severity,
    setSeverity,
    preferPrototype,
    setPreferPrototype,
    dataMode,
    apiStatus,
    wsStatus,
    health,
    feed,
    spikeNotice,
    fetchNotice,
    fetching,
    fetchPosts,
    clearSpike: () => {
      setSpikeNotice(null)
    },
    timeline,
    graph,
    demographics,
    trending,
    metrics,
    emotions,
    thread,
    reload: load,
  }
}
