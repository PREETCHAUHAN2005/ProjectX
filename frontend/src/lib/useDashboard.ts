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

export function useDashboard() {
  const [topic, setTopic] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [severity, setSeverity] = useState('')
  const [preferPrototype, setPreferPrototype] = useState(false)
  const [dataMode, setDataMode] = useState<DataMode>('prototype')
  const [apiStatus, setApiStatus] = useState('checking')
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [feed, setFeed] = useState<NewPostPayload[]>(() => prototypeFeed())
  const [spikeNotice, setSpikeNotice] = useState<string | null>(null)
  const [timeline, setTimeline] = useState<LoadState<TimelineResponse>>(initialLoad)
  const [graph, setGraph] = useState<LoadState<NetworkGraphResponse>>(initialLoad)
  const [demographics, setDemographics] =
    useState<LoadState<DemographicsResponse>>(initialLoad)
  const [trending, setTrending] = useState<LoadState<TrendingResponse>>(initialLoad)
  const tick = useRef(0)

  const load = useCallback(async (): Promise<void> => {
    setTimeline(initialLoad())
    setGraph(initialLoad())
    setDemographics(initialLoad())
    setTrending(initialLoad())

    if (preferPrototype) {
      const proto = seedPrototype()
      setTimeline(proto.timeline)
      setGraph(proto.graph)
      setDemographics(proto.demographics)
      setTrending(proto.trending)
      setDataMode('prototype')
      setApiStatus('preview')
      setFeed(prototypeFeed())
      return
    }

    try {
      const health = await getHealth()
      setApiStatus(health.status)
    } catch {
      const proto = seedPrototype()
      setTimeline(proto.timeline)
      setGraph(proto.graph)
      setDemographics(proto.demographics)
      setTrending(proto.trending)
      setDataMode('prototype')
      setApiStatus('unreachable')
      setFeed(prototypeFeed())
      return
    }

    const query = {
      topic: topic || undefined,
      from: from || undefined,
      to: to || undefined,
    }

    try {
      const [timelineData, graphData, demoData, trendingData] = await Promise.all([
        getTimeline({ ...query, bucket: 'hour' }),
        getNetworkGraph({ topic: query.topic }),
        getDemographics(query.topic),
        getTrending(),
      ])
      const empty =
        timelineData.buckets.length === 0 &&
        graphData.nodes.length === 0 &&
        demoData.country.length === 0 &&
        trendingData.topics.length === 0
      if (empty) {
        const proto = seedPrototype()
        setTimeline(proto.timeline)
        setGraph(proto.graph)
        setDemographics(proto.demographics)
        setTrending(proto.trending)
        setDataMode('prototype')
        setApiStatus('empty-preview')
        setFeed(prototypeFeed())
        return
      }
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
    } catch {
      const proto = seedPrototype()
      setTimeline(proto.timeline)
      setGraph(proto.graph)
      setDemographics(proto.demographics)
      setTrending(proto.trending)
      setDataMode('prototype')
      setApiStatus('unreachable')
      setFeed(prototypeFeed())
    }
  }, [from, preferPrototype, to, topic])

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
          setFeed((current) => [envelope.payload, ...current].slice(0, 50))
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
          setGraph((current) => {
            if (current.data === null) {
              return fromResult(envelope.payload, envelope.payload.nodes.length === 0)
            }
            return {
              status: 'ready',
              data: mergeGraph(current.data, envelope.payload),
              error: null,
            }
          })
        }
      },
    })
    socket.connect()
    return () => {
      socket.disconnect()
    }
  }, [dataMode, from, severity, to, topic])

  const metrics = useMemo(() => {
    const buckets = timeline.data?.buckets ?? []
    const volume = buckets.reduce((sum, bucket) => sum + bucket.count, 0)
    const polarity =
      buckets.length === 0
        ? 0
        : buckets.reduce((sum, bucket) => sum + bucket.average_sentiment, 0) /
          buckets.length
    return {
      volume,
      polarity,
      topics: trending.data?.topics.length ?? 0,
      nodes: graph.data?.nodes.length ?? 0,
    }
  }, [graph.data, timeline.data, trending.data])

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
    reload: load,
  }
}
