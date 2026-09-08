import type { TrendingResponse } from '../types/contracts'

export function TrendingList({
  data,
  onSelect,
}: {
  data: TrendingResponse
  onSelect?: (topic: string) => void
}) {
  const peak = Math.max(...data.topics.map((topic) => topic.velocity), 1)
  return (
    <ul className="space-y-2">
      {data.topics.map((topic, index) => (
        <li key={topic.topic_id}>
          <button
            type="button"
            className="w-full rounded-2xl border border-transparent px-2 py-2 text-left hover:border-line hover:bg-slate-50"
            onClick={() => onSelect?.(topic.topic_name)}
          >
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-[13px] font-semibold text-ink">
                <span className="mr-2 tabular text-muted">{String(index + 1).padStart(2, '0')}</span>
                {topic.topic_name}
              </span>
              <span className="tabular text-[12px] text-muted">
                {topic.velocity.toFixed(2)} · n {topic.sample_size}
              </span>
            </div>
            <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${(topic.velocity / peak) * 100}%` }}
              />
            </div>
          </button>
        </li>
      ))}
    </ul>
  )
}
