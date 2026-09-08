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
  'Preview data — the API is unreachable. Start the FastAPI server with DEMO_SEED=true for the live demo.'

const hoursAgoIso = (hours: number): string =>
  new Date(Date.now() - hours * 3600 * 1000).toISOString()

export function prototypeTimeline(): TimelineResponse {
  const buckets = Array.from({ length: 12 }, (_, index) => {
    const hour = 11 - index
    const comments = Math.round(8 + (index % 5) * 6 + (hour < 3 ? 28 : 0))
    const posts = hour === 6 || hour === 5 || hour === 8 || hour === 3 ? 1 : 0
    const average_sentiment = Number((-0.18 + (index % 4) * 0.08).toFixed(3))
    const top_emotions =
      average_sentiment < 0
        ? [
            { label: 'fear', score: 0.34 },
            { label: 'approval', score: 0.22 },
            { label: 'anger', score: 0.16 },
          ]
        : [
            { label: 'approval', score: 0.31 },
            { label: 'relief', score: 0.24 },
            { label: 'neutral', score: 0.18 },
          ]
    return {
      timestamp: hoursAgoIso(hour),
      count: posts + comments,
      post_count: posts,
      comment_count: comments,
      average_sentiment,
      top_emotions,
    }
  })
  return { buckets }
}

export function prototypeGraph(): NetworkGraphResponse {
  return {
    nodes: [
      { id: 'imd', handle: 'IndiaMetDept', platform: 'x', pagerank: 0.18, community: 'fear' },
      { id: 'reliefops', handle: 'ReliefOpsIN', platform: 'telegram', pagerank: 0.16, community: 'approval' },
      { id: 'mumbaipolice', handle: 'MumbaiPolice', platform: 'x', pagerank: 0.12, community: 'realization' },
      { id: 'priya', handle: 'PriyaKamble', platform: 'x', pagerank: 0.09, community: 'fear' },
      { id: 'civicwatch', handle: 'CivicWatchMUM', platform: 'telegram', pagerank: 0.08, community: 'approval' },
      { id: 'meera', handle: 'MeeraDesai', platform: 'x', pagerank: 0.07, community: 'anger' },
      { id: 'anand', handle: 'AnandNair', platform: 'x', pagerank: 0.06, community: 'caring' },
      { id: 'griddesk', handle: 'GridDeskWest', platform: 'x', pagerank: 0.05, community: 'relief' },
      { id: 'hydroalert', handle: 'HydroAlert', platform: 'telegram', pagerank: 0.05, community: 'nervousness' },
      { id: 'volunteerin', handle: 'VolunteerIN', platform: 'x', pagerank: 0.04, community: 'caring' },
      { id: 'airindex', handle: 'AirIndexIN', platform: 'x', pagerank: 0.04, community: 'annoyance' },
      { id: 'transitbot', handle: 'TransitBot', platform: 'x', pagerank: 0.03, community: 'relief' },
    ],
    links: [
      { source: 'priya', target: 'imd', type: 'reply', timestamp: hoursAgoIso(1), weight: 2.4 },
      { source: 'mumbaipolice', target: 'imd', type: 'reply', timestamp: hoursAgoIso(1), weight: 3.1 },
      { source: 'civicwatch', target: 'reliefops', type: 'reply', timestamp: hoursAgoIso(2), weight: 2.2 },
      { source: 'meera', target: 'imd', type: 'reply', timestamp: hoursAgoIso(2), weight: 1.8 },
      { source: 'anand', target: 'mumbaipolice', type: 'mention', timestamp: hoursAgoIso(3), weight: 1.6 },
      { source: 'volunteerin', target: 'reliefops', type: 'reply', timestamp: hoursAgoIso(3), weight: 2.0 },
      { source: 'hydroalert', target: 'imd', type: 'reply', timestamp: hoursAgoIso(2), weight: 1.7 },
      { source: 'transitbot', target: 'mumbaipolice', type: 'mention', timestamp: hoursAgoIso(1), weight: 1.3 },
      { source: 'reliefops', target: 'imd', type: 'mention', timestamp: hoursAgoIso(5), weight: 2.8 },
      { source: 'griddesk', target: 'reliefops', type: 'mention', timestamp: hoursAgoIso(3), weight: 1.1 },
    ],
  }
}

export function prototypeDemographics(): DemographicsResponse {
  return {
    country: [
      { key: 'India', count: 86 },
      { key: 'United States', count: 8 },
      { key: 'UAE', count: 6 },
      { key: 'Bangladesh', count: 4 },
      { key: 'United Kingdom', count: 3 },
    ],
    language: [
      { key: 'English', count: 78 },
      { key: 'Hindi', count: 18 },
      { key: 'Bengali', count: 4 },
      { key: 'Tamil', count: 3 },
    ],
    profession: [
      { key: 'Public sector', count: 28 },
      { key: 'Other', count: 24 },
      { key: 'Media', count: 16 },
      { key: 'Engineering', count: 14 },
      { key: 'Logistics', count: 10 },
      { key: 'Research', count: 8 },
    ],
  }
}

export function prototypeTrending(): TrendingResponse {
  return {
    topics: [
      {
        topic_id: 'flood relief',
        topic_name: 'flood relief',
        velocity: 2.6,
        acceleration: 0.9,
        sample_size: 52,
      },
      {
        topic_id: 'power outage',
        topic_name: 'power outage',
        velocity: 1.4,
        acceleration: 0.2,
        sample_size: 8,
      },
      {
        topic_id: 'air quality',
        topic_name: 'air quality',
        velocity: 1.1,
        acceleration: 0.0,
        sample_size: 6,
      },
      {
        topic_id: 'port congestion',
        topic_name: 'port congestion',
        velocity: 1.0,
        acceleration: 0.0,
        sample_size: 2,
      },
    ],
  }
}

const FEED: NewPostPayload[] = [
  {
    platform: 'x',
    external_id: 'imd-rain-alert',
    timestamp: hoursAgoIso(6.2),
    author: { user_id: 'imd', handle: 'IndiaMetDept', follower_count: 1840 },
    content: {
      raw_text:
        'Orange alert: heavy rain over Mumbai and Pune until 10pm IST. Avoid coastal roads and underpasses. Updates with @MumbaiPolice.',
      hashtags: ['floodrelief'],
      language: 'English',
    },
    thread_role: 'post',
    topic_name: 'flood relief',
    polarity: 'NEGATIVE',
    severity: 'high',
    emotions: [
      { label: 'fear', score: 0.64 },
      { label: 'neutral', score: 0.2 },
    ],
  },
  {
    platform: 'telegram',
    external_id: 'relief-camps-open',
    timestamp: hoursAgoIso(5.4),
    author: { user_id: 'reliefops', handle: 'ReliefOpsIN' },
    content: {
      raw_text:
        'Three relief camps are open at municipal schools in Dadar, Kurla, and Andheri. Dry rations staged. Coordinating with @IndiaMetDept.',
      hashtags: ['floodrelief'],
      language: 'English',
    },
    thread_role: 'post',
    topic_name: 'flood relief',
    polarity: 'POSITIVE',
    emotions: [{ label: 'approval', score: 0.64 }],
  },
  {
    platform: 'x',
    external_id: 'c-priya-lobby',
    timestamp: hoursAgoIso(5.7),
    author: { user_id: 'priya', handle: 'PriyaKamble' },
    content: {
      raw_text:
        'Water entered our building lobby in Wadala. Need pumps. Please send help @ReliefOpsIN',
      hashtags: ['floodrelief'],
    },
    thread_role: 'comment',
    in_reply_to: 'imd-rain-alert',
    topic_name: 'flood relief',
    polarity: 'NEGATIVE',
    emotions: [{ label: 'fear', score: 0.7 }],
  },
  {
    platform: 'x',
    external_id: 'c-police-divert',
    timestamp: hoursAgoIso(5.9),
    author: { user_id: 'mumbaipolice', handle: 'MumbaiPolice' },
    content: {
      raw_text:
        'Traffic diversions on Western Express Highway. Do not use flooded underpasses. @IndiaMetDept',
    },
    thread_role: 'comment',
    in_reply_to: 'imd-rain-alert',
    polarity: 'NEUTRAL',
    emotions: [{ label: 'realization', score: 0.58 }],
  },
  {
    platform: 'telegram',
    external_id: 'c-civic-camps',
    timestamp: hoursAgoIso(5.1),
    author: { user_id: 'civicwatch', handle: 'CivicWatchMUM' },
    content: {
      raw_text:
        'Confirmed: camps at three schools are taking families. Volunteers at the Dadar gate. @ReliefOpsIN',
    },
    thread_role: 'comment',
    in_reply_to: 'relief-camps-open',
    polarity: 'POSITIVE',
    emotions: [{ label: 'approval', score: 0.61 }],
  },
  {
    platform: 'x',
    external_id: 'c-meera-anger',
    timestamp: hoursAgoIso(4.4),
    author: { user_id: 'meera', handle: 'MeeraDesai' },
    content: {
      raw_text: 'Drains were not cleared before the alert. This happens every monsoon. @IndiaMetDept',
    },
    thread_role: 'comment',
    in_reply_to: 'imd-rain-alert',
    polarity: 'NEGATIVE',
    emotions: [{ label: 'anger', score: 0.66 }],
  },
  {
    platform: 'x',
    external_id: 'c-volunteer-ration',
    timestamp: hoursAgoIso(3.0),
    author: { user_id: 'volunteerin', handle: 'VolunteerIN' },
    content: {
      raw_text:
        'Need dry ration for 40 families near the bus depot. Coordination with the district office. @ReliefOpsIN',
    },
    thread_role: 'comment',
    in_reply_to: 'relief-camps-open',
    polarity: 'NEGATIVE',
    emotions: [{ label: 'caring', score: 0.55 }],
  },
  {
    platform: 'x',
    external_id: 'c-grid-feeder',
    timestamp: hoursAgoIso(3.6),
    author: { user_id: 'griddesk', handle: 'GridDeskWest' },
    content: {
      raw_text:
        'Load shedding shortened in two districts after feeder repair. Crews still in Kurla. @ReliefOpsIN',
      hashtags: ['power'],
    },
    thread_role: 'post',
    topic_name: 'power outage',
    polarity: 'POSITIVE',
    emotions: [{ label: 'relief', score: 0.6 }],
  },
]

export function prototypeFeed(limit = 8): NewPostPayload[] {
  return FEED.slice(0, limit)
}

const LIVE_TICKS: NewPostPayload[] = [
  {
    platform: 'x',
    external_id: 'live-1',
    timestamp: new Date().toISOString(),
    author: { user_id: 'priya', handle: 'PriyaKamble' },
    content: {
      raw_text: 'Update: municipal pump arrived at Wadala lobby. Water dropping. @ReliefOpsIN',
    },
    thread_role: 'comment',
    in_reply_to: 'imd-rain-alert',
    polarity: 'POSITIVE',
    topic_name: 'flood relief',
    emotions: [{ label: 'relief', score: 0.7 }],
  },
  {
    platform: 'telegram',
    external_id: 'live-2',
    timestamp: new Date().toISOString(),
    author: { user_id: 'civicwatch', handle: 'CivicWatchMUM' },
    content: {
      raw_text: 'Kurla camp now at 55 people. Still accepting families. @ReliefOpsIN',
    },
    thread_role: 'comment',
    in_reply_to: 'relief-camps-open',
    polarity: 'NEUTRAL',
    emotions: [{ label: 'realization', score: 0.5 }],
  },
]

export function nextPrototypePost(tick: number): NewPostPayload {
  const item = LIVE_TICKS[tick % LIVE_TICKS.length]
  return {
    ...item,
    external_id: `live-${tick}-${item.author.user_id}`,
    timestamp: new Date().toISOString(),
  }
}

export function prototypeSpike(): TrendSpikePayload {
  return {
    topic_id: 'flood relief',
    topic_name: 'flood relief',
    velocity: 2.6,
    sample_size: 52,
  }
}

export function prototypeGraphDelta(): GraphDeltaPayload {
  return {
    nodes: [
      {
        id: 'districtcell',
        handle: 'DistrictCell',
        platform: 'telegram',
        pagerank: 0.04,
        community: 'approval',
      },
    ],
    links: [
      {
        source: 'districtcell',
        target: 'reliefops',
        type: 'reply',
        timestamp: new Date().toISOString(),
        weight: 1.2,
      },
    ],
  }
}
