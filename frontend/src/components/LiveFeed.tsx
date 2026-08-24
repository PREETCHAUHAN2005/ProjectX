import { relativeTime } from '../lib/format'
import type { NewPostPayload } from '../types/contracts'

export function LiveFeed({ posts }: { posts: NewPostPayload[] }) {
  if (posts.length === 0) {
    return (
      <p className="text-sm text-muted">Waiting for event:new_post…</p>
    )
  }

  return (
    <ul className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
      {posts.map((post) => (
        <li
          key={`${post.platform}:${post.external_id}`}
          className="rounded-xl border border-line bg-canvas/50 px-3 py-2.5"
        >
          <div className="mb-1 flex items-center justify-between gap-2 text-[11px]">
            <span className="font-medium text-ink">@{post.author.handle}</span>
            <span className="text-muted">
              {post.platform} · {relativeTime(post.timestamp)}
            </span>
          </div>
          <p className="text-[13px] leading-5 text-ink">{post.content.raw_text}</p>
          {post.content.hashtags && post.content.hashtags.length > 0 ? (
            <p className="mt-1 text-[11px] text-accent">
              {post.content.hashtags.map((tag) => `#${tag}`).join('  ')}
            </p>
          ) : null}
        </li>
      ))}
    </ul>
  )
}
