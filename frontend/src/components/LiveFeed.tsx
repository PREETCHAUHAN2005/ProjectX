import { relativeTime } from '../lib/format'
import type { NewPostPayload } from '../types/contracts'

function dominantEmotion(post: NewPostPayload): string | null {
  if (!post.emotions || post.emotions.length === 0) {
    return null
  }
  return [...post.emotions].sort((a, b) => b.score - a.score)[0]?.label ?? null
}

function polarityClass(polarity: string): string {
  if (polarity === 'POSITIVE') {
    return 'bg-good-soft text-good'
  }
  if (polarity === 'NEGATIVE') {
    return 'bg-bad-soft text-bad'
  }
  return 'bg-surface text-muted ring-1 ring-line'
}

export function LiveFeed({ posts }: { posts: NewPostPayload[] }) {
  if (posts.length === 0) {
    return <p className="text-sm text-muted">Waiting for event:new_post…</p>
  }

  return (
    <ul className="max-h-[420px] space-y-2.5 overflow-y-auto pr-1">
      {posts.map((post) => {
        const role = post.thread_role === 'comment' ? 'Comment' : 'Post'
        const emotion = dominantEmotion(post)
        return (
          <li
            key={`${post.platform}:${post.external_id}`}
            className="rounded-2xl border border-line bg-inset px-3.5 py-3"
          >
            <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2 text-[11px]">
              <span className="flex items-center gap-2 font-semibold text-ink">
                @{post.author.handle}
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
                    role === 'Post' ? 'bg-navy text-white' : 'bg-accent-soft text-accent'
                  }`}
                >
                  {role}
                </span>
              </span>
              <span className="text-muted">
                {post.platform} · {relativeTime(post.timestamp)}
              </span>
            </div>
            <p className="text-[13px] leading-5 text-ink">{post.content.raw_text}</p>
            <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
              {emotion ? (
                <span className="rounded-full bg-surface px-2 py-0.5 capitalize text-muted ring-1 ring-line">
                  {emotion}
                </span>
              ) : null}
              {post.polarity ? (
                <span className={`rounded-full px-2 py-0.5 ${polarityClass(post.polarity)}`}>
                  {post.polarity}
                </span>
              ) : null}
              {post.content.hashtags?.map((tag) => (
                <span key={tag} className="text-accent">
                  #{tag}
                </span>
              ))}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
