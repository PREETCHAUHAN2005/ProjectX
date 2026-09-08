import type { DemographicSlice } from '../types/contracts'

const LAYOUT: Record<string, { x: number; y: number; r: number }> = {
  India: { x: 68, y: 48, r: 18 },
  'United States': { x: 22, y: 38, r: 14 },
  'United Kingdom': { x: 46, y: 32, r: 8 },
  UAE: { x: 58, y: 44, r: 7 },
  Bangladesh: { x: 72, y: 46, r: 8 },
  Singapore: { x: 76, y: 56, r: 6 },
  Germany: { x: 49, y: 34, r: 8 },
}

export function ChoroplethMap({ slices }: { slices: DemographicSlice[] }) {
  const max = Math.max(...slices.map((item) => item.count), 1)
  return (
    <div className="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
      <svg viewBox="0 0 100 72" className="h-44 w-full rounded-2xl bg-slate-50" role="img" aria-label="Country density">
        <rect width="100" height="72" fill="#f1f5f9" />
        {slices.map((item) => {
          const point = LAYOUT[item.key] ?? {
            x: 12 + (item.key.length * 7) % 80,
            y: 18 + (item.count % 40),
            r: 6,
          }
          const intensity = item.count / max
          return (
            <g key={item.key}>
              <circle
                cx={point.x}
                cy={point.y}
                r={point.r * (0.55 + intensity * 0.7)}
                fill={`rgba(249, 115, 22, ${0.2 + intensity * 0.65})`}
                stroke="#0f172a"
                strokeOpacity="0.12"
              />
            </g>
          )
        })}
      </svg>
      <ul className="space-y-2">
        {slices.slice(0, 6).map((item) => (
          <li key={item.key}>
            <div className="mb-1 flex justify-between text-[12px]">
              <span className="text-ink">{item.key}</span>
              <span className="tabular text-muted">{item.count}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${(item.count / max) * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
