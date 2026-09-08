import { formatCount } from '../lib/format'

export function MetricStrip({
  posts,
  comments,
  topEmotion,
  topics,
}: {
  posts: number
  comments: number
  topEmotion: string
  topics: number
}) {
  const items = [
    { label: 'Posts', value: formatCount(posts), hint: 'root posts in window' },
    { label: 'Comments', value: formatCount(comments), hint: 'replies in thread' },
    { label: 'Top emotion', value: topEmotion, hint: 'dominant in window' },
    { label: 'Topics', value: formatCount(topics), hint: 'ranked now' },
  ]
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <article
          key={item.label}
          className="rounded-[20px] border border-line bg-surface px-5 py-4 card-shadow"
        >
          <p className="text-[12px] font-medium text-ink">{item.label}</p>
          <p className="mt-2 text-[32px] leading-none font-extrabold tracking-tight text-ink capitalize">
            {item.value}
          </p>
          <p className="mt-2 text-[12px] text-muted">{item.hint}</p>
        </article>
      ))}
    </div>
  )
}
