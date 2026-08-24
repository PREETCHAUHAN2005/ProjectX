import { formatCount, formatScore, polarityWord } from '../lib/format'

export function MetricStrip({
  volume,
  polarity,
  topics,
  nodes,
}: {
  volume: number
  polarity: number
  topics: number
  nodes: number
}) {
  const items = [
    { label: 'Volume', value: formatCount(volume), hint: 'posts in window' },
    { label: 'Polarity', value: formatScore(polarity), hint: polarityWord(polarity) },
    { label: 'Topics', value: formatCount(topics), hint: 'ranked now' },
    { label: 'Graph', value: formatCount(nodes), hint: 'active nodes' },
  ]
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <article
          key={item.label}
          className="rounded-2xl border border-line bg-surface px-4 py-3 shadow-[0_1px_2px_rgba(20,20,19,0.04)]"
        >
          <p className="text-[11px] font-medium tracking-wide text-muted uppercase">{item.label}</p>
          <p className="mt-1 font-serif text-[28px] leading-none text-ink">{item.value}</p>
          <p className="mt-1 text-[12px] text-muted">{item.hint}</p>
        </article>
      ))}
    </div>
  )
}
