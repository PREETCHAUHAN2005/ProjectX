import type {
  EmotionScore,
  NewPostPayload,
  TimelineResponse,
} from '../types/contracts'

export type FeaturedThread = {
  post: NewPostPayload
  comments: NewPostPayload[]
  polarity: string
  topEmotions: EmotionScore[]
}

export function postCountFromTimeline(data: TimelineResponse | null): number {
  if (!data) {
    return 0
  }
  return data.buckets.reduce((sum, bucket) => sum + (bucket.post_count ?? 0), 0)
}

export function commentCountFromTimeline(data: TimelineResponse | null): number {
  if (!data) {
    return 0
  }
  return data.buckets.reduce((sum, bucket) => {
    if (typeof bucket.comment_count === 'number') {
      return sum + bucket.comment_count
    }
    return sum
  }, 0)
}

export function emotionMixFromTimeline(data: TimelineResponse | null): EmotionScore[] {
  if (!data) {
    return []
  }
  const totals = new Map<string, number>()
  for (const bucket of data.buckets) {
    for (const emotion of bucket.top_emotions) {
      totals.set(emotion.label, (totals.get(emotion.label) ?? 0) + emotion.score)
    }
  }
  return [...totals.entries()]
    .map(([label, score]) => ({ label, score }))
    .sort((a, b) => b.score - a.score)
}

export function topEmotionLabel(emotions: EmotionScore[]): string {
  return emotions[0]?.label ?? '—'
}

export function featuredThread(feed: NewPostPayload[]): FeaturedThread | null {
  const posts = feed.filter((item) => item.thread_role !== 'comment')
  if (posts.length === 0 && feed.length === 0) {
    return null
  }
  const roots = posts.length > 0 ? posts : feed
  let best = roots[0]
  let bestComments: NewPostPayload[] = []
  for (const post of roots) {
    const comments = feed.filter(
      (item) => item.thread_role === 'comment' && item.in_reply_to === post.external_id,
    )
    if (comments.length >= bestComments.length) {
      best = post
      bestComments = comments
    }
  }
  const emotionMap = new Map<string, number>()
  for (const item of [best, ...bestComments]) {
    for (const emotion of item.emotions ?? []) {
      emotionMap.set(emotion.label, (emotionMap.get(emotion.label) ?? 0) + emotion.score)
    }
  }
  const topEmotions = [...emotionMap.entries()]
    .map(([label, score]) => ({ label, score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
  return {
    post: best,
    comments: bestComments,
    polarity: best.polarity ?? 'NEUTRAL',
    topEmotions,
  }
}
