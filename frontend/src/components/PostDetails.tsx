import type { FeaturedThread } from '../lib/thread'

export function PostDetails({ thread }: { thread: FeaturedThread | null }) {
  if (!thread) {
    return <p className="text-sm text-muted">No post in the live feed yet.</p>
  }
  const rows = [
    { label: 'Author', value: `@${thread.post.author.handle}` },
    { label: 'Platform', value: thread.post.platform },
    { label: 'Comments', value: String(thread.comments.length) },
    { label: 'Polarity', value: thread.polarity },
    {
      label: 'Top emotion',
      value: thread.topEmotions[0]?.label ?? '—',
    },
    { label: 'Topic', value: thread.post.topic_name ?? '—' },
  ]

  return (
    <div>
      <p className="mb-3 text-[13px] leading-5 text-ink">{thread.post.content.raw_text}</p>
      <table className="w-full text-left text-[13px]">
        <thead>
          <tr className="text-[11px] uppercase tracking-wide text-muted">
            <th className="pb-2 font-medium">Signal</th>
            <th className="pb-2 font-medium">Value</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-t border-line">
              <td className="py-2 text-muted">{row.label}</td>
              <td className="py-2 font-semibold capitalize text-ink">{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
