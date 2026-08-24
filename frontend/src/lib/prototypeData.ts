import type {
  DemographicsResponse,
  GraphDeltaPayload,
  NetworkGraphResponse,
  NewPostPayload,
  TimelineResponse,
  TrendSpikePayload,
  TrendingResponse,
} from '../types/contracts'

export const PROTOTYPE_NOTICE =
  'Preview data — live API is empty or unreachable. Connect Colab later with VITE_MODEL_URL.'

const hoursAgoIso = (hours: number): string =>
  new Date(Date.now() - hours * 3600 * 1000).toISOString()

export function prototypeTimeline(): TimelineResponse {
  const buckets = Array.from({ length: 24 }, (_, index) => {
    const hour = 23 - index
    const wave = Math.sin(index / 3.2) * 0.35
    const count = Math.round(42 + wave * 28 + (index % 5) * 3)
    const average_sentiment = Number(
      (-0.12 + wave * 0.55 + (index % 7) * 0.02).toFixed(3),
    )
    const top_emotions =
      average_sentiment >= 0
        ? [
            { label: 'optimism', score: 0.31 },
            { label: 'approval', score: 0.22 },
            { label: 'neutral', score: 0.18 },
          ]
        : [
            { label: 'annoyance', score: 0.29 },
            { label: 'fear', score: 0.21 },
            { label: 'neutral', score: 0.17 },
          ]
    return {
      timestamp: hoursAgoIso(hour),
      count,
      average_sentiment,
      top_emotions,
    }
  })
  return { buckets }
}

export function prototypeGraph(): NetworkGraphResponse {
  return {
    nodes: [
      { id: 'u1', handle: 'reliefops', platform: 'x', pagerank: 0.18, community: 'civic' },
      { id: 'u2', handle: 'citywatch', platform: 'telegram', pagerank: 0.14, community: 'civic' },
      { id: 'u3', handle: 'griddesk', platform: 'x', pagerank: 0.11, community: 'infra' },
      { id: 'u4', handle: 'floodcell', platform: 'telegram', pagerank: 0.1, community: 'weather' },
      { id: 'u5', handle: 'airindex', platform: 'x', pagerank: 0.09, community: 'weather' },
      { id: 'u6', handle: 'northdesk', platform: 'x', pagerank: 0.08, community: 'infra' },
      { id: 'u7', handle: 'portnews', platform: 'telegram', pagerank: 0.07, community: 'infra' },
      { id: 'u8', handle: 'volunteerin', platform: 'x', pagerank: 0.06, community: 'civic' },
      { id: 'u9', handle: 'transitbot', platform: 'x', pagerank: 0.05, community: 'infra' },
      { id: 'u10', handle: 'hydroalert', platform: 'telegram', pagerank: 0.05, community: 'weather' },
      { id: 'u11', handle: 'localpulse', platform: 'x', pagerank: 0.04, community: 'civic' },
      { id: 'u12', handle: 'satlayer', platform: 'x', pagerank: 0.03, community: 'infra' },
    ],
    links: [
      { source: 'u1', target: 'u2', type: 'mention', timestamp: hoursAgoIso(1), weight: 3.2 },
      { source: 'u1', target: 'u8', type: 'mention', timestamp: hoursAgoIso(2), weight: 2.4 },
      { source: 'u2', target: 'u4', type: 'reply', timestamp: hoursAgoIso(1), weight: 2.1 },
      { source: 'u4', target: 'u10', type: 'mention', timestamp: hoursAgoIso(3), weight: 2.8 },
      { source: 'u3', target: 'u6', type: 'mention', timestamp: hoursAgoIso(2), weight: 1.9 },
      { source: 'u3', target: 'u9', type: 'reply', timestamp: hoursAgoIso(4), weight: 1.6 },
      { source: 'u6', target: 'u7', type: 'mention', timestamp: hoursAgoIso(5), weight: 1.4 },
      { source: 'u7', target: 'u12', type: 'mention', timestamp: hoursAgoIso(6), weight: 1.2 },
      { source: 'u5', target: 'u10', type: 'mention', timestamp: hoursAgoIso(2), weight: 2.0 },
      { source: 'u5', target: 'u11', type: 'reply', timestamp: hoursAgoIso(3), weight: 1.1 },
      { source: 'u8', target: 'u11', type: 'mention', timestamp: hoursAgoIso(4), weight: 1.5 },
      { source: 'u9', target: 'u3', type: 'mention', timestamp: hoursAgoIso(1), weight: 1.3 },
      { source: 'u12', target: 'u1', type: 'mention', timestamp: hoursAgoIso(7), weight: 0.9 },
      { source: 'u2', target: 'u3', type: 'mention', timestamp: hoursAgoIso(8), weight: 1.0 },
    ],
  }
}

export function prototypeDemographics(): DemographicsResponse {
  return {
    country: [
      { key: 'India', count: 420 },
      { key: 'United States', count: 88 },
      { key: 'United Kingdom', count: 41 },
      { key: 'UAE', count: 36 },
      { key: 'Bangladesh', count: 29 },
      { key: 'Singapore', count: 18 },
      { key: 'Germany', count: 14 },
    ],
    language: [
      { key: 'English', count: 310 },
      { key: 'Hindi', count: 240 },
      { key: 'Bengali', count: 42 },
      { key: 'Tamil', count: 31 },
      { key: 'Arabic', count: 19 },
    ],
    profession: [
      { key: 'Public sector', count: 160 },
      { key: 'Media', count: 120 },
      { key: 'Engineering', count: 98 },
      { key: 'Research', count: 72 },
      { key: 'Logistics', count: 54 },
      { key: 'Other', count: 40 },
    ],
  }
}

export function prototypeTrending(): TrendingResponse {
  return {
    topics: [
      {
        topic_id: 't-flood',
        topic_name: 'flood relief',
        velocity: 3.4,
        acceleration: 0.8,
        sample_size: 186,
      },
      {
        topic_id: 't-grid',
        topic_name: 'power outage',
        velocity: 2.9,
        acceleration: 0.4,
        sample_size: 142,
      },
      {
        topic_id: 't-air',
        topic_name: 'air quality',
        velocity: 2.1,
        acceleration: 0.2,
        sample_size: 97,
      },
      {
        topic_id: 't-roads',
        topic_name: 'border roads',
        velocity: 1.7,
        acceleration: -0.1,
        sample_size: 64,
      },
      {
        topic_id: 't-port',
        topic_name: 'port congestion',
        velocity: 1.4,
        acceleration: 0.1,
        sample_size: 51,
      },
    ],
  }
}

const FEED: Array<{
  platform: 'telegram' | 'x'
  handle: string
  user_id: string
  text: string
  tags: string[]
}> = [
  {
    platform: 'x',
    handle: 'reliefops',
    user_id: 'u1',
    text: 'Relief kits staged at three municipal schools. Roads east of the river still slow.',
    tags: ['floodrelief'],
  },
  {
    platform: 'telegram',
    handle: 'citywatch',
    user_id: 'u2',
    text: 'Public advisory: avoid low-lying underpasses until 18:00 IST. Pumps are active.',
    tags: ['civic'],
  },
  {
    platform: 'x',
    handle: 'griddesk',
    user_id: 'u3',
    text: 'Load shedding window shortened in two districts after feeder repair.',
    tags: ['power'],
  },
  {
    platform: 'telegram',
    handle: 'floodcell',
    user_id: 'u4',
    text: 'Hourly gauge: river up 12 cm vs yesterday. Volunteer boats on standby.',
    tags: ['weather'],
  },
  {
    platform: 'x',
    handle: 'airindex',
    user_id: 'u5',
    text: 'AQI 312 in the north cluster. Construction pause requested through Friday.',
    tags: ['airquality'],
  },
  {
    platform: 'x',
    handle: 'volunteerin',
    user_id: 'u8',
    text: 'Need dry ration for 40 families near the bus depot. Coordination with the district office.',
    tags: ['floodrelief'],
  },
  {
    platform: 'telegram',
    handle: 'portnews',
    user_id: 'u7',
    text: 'Berth 4 delay 6h. Perishable cargo rerouted. Not a security incident.',
    tags: ['logistics'],
  },
  {
    platform: 'x',
    handle: 'transitbot',
    user_id: 'u9',
    text: 'Suburban line 2 resumed at 40% frequency after water receded from the yard.',
    tags: ['transit'],
  },
]

export function prototypeFeed(limit = 8): NewPostPayload[] {
  return FEED.slice(0, limit).map((item, index) => ({
    platform: item.platform,
    external_id: `proto-${index}-${item.user_id}`,
    timestamp: hoursAgoIso(index * 0.35),
    author: {
      user_id: item.user_id,
      handle: item.handle,
      follower_count: 1200 + index * 340,
    },
    content: {
      raw_text: item.text,
      hashtags: item.tags,
      language: 'en',
    },
  }))
}

export function nextPrototypePost(tick: number): NewPostPayload {
  const item = FEED[tick % FEED.length]
  return {
    platform: item.platform,
    external_id: `live-${tick}-${item.user_id}`,
    timestamp: new Date().toISOString(),
    author: { user_id: item.user_id, handle: item.handle },
    content: { raw_text: item.text, hashtags: item.tags, language: 'en' },
  }
}

export function prototypeSpike(): TrendSpikePayload {
  return {
    topic_id: 't-flood',
    topic_name: 'flood relief',
    velocity: 3.4,
    sample_size: 186,
  }
}

export function prototypeGraphDelta(): GraphDeltaPayload {
  return {
    nodes: [
      {
        id: 'u13',
        handle: 'districtcell',
        platform: 'telegram',
        pagerank: 0.04,
        community: 'civic',
      },
    ],
    links: [
      {
        source: 'u1',
        target: 'u13',
        type: 'mention',
        timestamp: new Date().toISOString(),
        weight: 1.2,
      },
    ],
  }
}
