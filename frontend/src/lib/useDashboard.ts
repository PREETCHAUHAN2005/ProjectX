import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  getDemographics,
  getHealth,
  getNetworkGraph,
  getTimeline,
  getTrending,
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
  NetworkGraphResponse,
  NewPostPayload,
  TimelineResponse,
  TrendingResponse,
  WsEnvelope,
} from '../types/contracts'

export type DataMode = 'live' | 'prototype'

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

function applyPrototypeWidgets(
  setTimeline: (value: LoadState<TimelineResponse>) => void,
  setGraph: (value: LoadState<NetworkGraphResponse>) => void,
  setDemographics: (value: LoadState<DemographicsResponse>) => void,
  setTrending: (value: LoadState<TrendingResponse>) => void,
  setFeed: (value: NewPostPayload[]) => void,
) {
  const proto = seedPrototype()
  setTimeline(proto.timeline)
  setGraph(proto.graph)
  setDemographics(proto.demographics)
  setTrending(proto.trending)
  setFeed(prototypeFeed())
}

export function useDashboard() {
  const [topic, setTopic] = useState('')
  const [from, setFrom] = useState(() => hoursAgo(24))
  const [to, setTo] = useState(() => hoursAgo(0))
  const [severity, setSeverity] = useState('')
  const [preferPrototype, setPreferPrototype] = useState(false)
  const [dataMode, setDataMode] = useState<DataMode>('prototype')
  const [apiStatus, setApiStatus] = useState('checking')
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [feed, setFeed] = useState<NewPostPayload[]>([])
  const [spikeNotice, setSpikeNotice] = useState<string | null>(null)
  const [timeline, setTimeline] = useState<LoadState<TimelineResponse>>(initialLoad)
  const [graph, setGraph] = useState<LoadState<NetworkGraphResponse>>(initialLoad)
  const [demographics, setDemographics] =
    useState<LoadState<DemographicsResponse>>(initialLoad)
  const [trending, setTrending] = useState<LoadState<TrendingResponse>>(initialLoad)
  const tick = useRef(0)
  const liveFeedReset = useRef(false)

  const load = useCallback(async (): Promise<void> => {
    setTimeline(initialLoad())
    setGraph(initialLoad())
    setDemographics(initialLoad())
    setTrending(initialLoad())

    if (preferPrototype) {
      applyPrototypeWidgets(setTimeline, setGraph, setDemographics, setTrending, setFeed)
      setDataMode('prototype')
      setApiStatus('preview')
      return
    }

    try {
      const health = await getHealth()
      setApiStatus(health.status)
    } catch {
      applyPrototypeWidgets(setTimeline, setGraph, setDemographics, setTrending, setFeed)
      setDataMode('prototype')
      setApiStatus('unreachable')
      return
    }

    const query = {
      topic: topic || undefined,
      from: from || undefined,
      to: to || undefined,
      severity: severity || undefined,
    }

    try {
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
      setDataMode('live')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Request failed'
      setTimeline({ status: 'error', data: null, error: message })
      setGraph({ status: 'error', data: null, error: message })
      setDemographics({ status: 'error', data: null, error: message })
      setTrending({ status: 'error', data: null, error: message })
      setDataMode('live')
      setApiStatus('error')
    }
  }, [from, preferPrototype, severity, to, topic])

  useEffect(() => {
    void load()
  }, [load])

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

    const socket = new DashboardSocket({
      onOpen: () => {
        setWsStatus('connected')
        liveFeedReset.current = true
        socket.sendFilter({
          type: 'filter',
          topic: topic || undefined,
          time_window: {
            from: from || undefined,
            to: to || undefined,
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
          if (!isNewPostPayload(envelope.payload)) {
            return
          }
          const incoming = envelope.payload
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
          return
        }
        if (envelope.event === 'event:trend_spike') {
          if (!isTrendSpikePayload(envelope.payload)) {
            return
          }
          setSpikeNotice(
            `${envelope.payload.topic_name} · velocity ${envelope.payload.velocity.toFixed(1)}`,
          )
          return
        }
        if (envelope.event === 'event:graph_delta' && isGraphDeltaPayload(envelope.payload)) {
          const delta = envelope.payload
          setGraph((current) => {
            if (current.data === null) {
              return fromResult(delta, delta.nodes.length === 0)
            }
            return {
              status: 'ready',
              data: mergeGraph(current.data, delta),
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
  }, [dataMode, from, severity, to, topic])

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
    feed,
    spikeNotice,
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
