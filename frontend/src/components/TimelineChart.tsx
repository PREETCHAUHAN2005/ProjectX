import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TimelineResponse } from '../types/contracts'

function tickLabel(value: string): string {
  const stamp = Date.parse(value)
  if (Number.isNaN(stamp)) {
    return value.slice(11, 16)
  }
  return new Date(stamp).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function ChartTip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ name: string; value: number; color: string }>
  label?: string
}) {
  if (!active || !payload?.length) {
    return null
  }
  return (
    <div className="rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-sm">
      <p className="mb-1 text-muted">{label}</p>
      {payload.map((item) => (
        <p key={item.name} className="tabular text-ink">
          <span className="mr-2 inline-block h-2 w-2 rounded-full" style={{ background: item.color }} />
          {item.name}: {typeof item.value === 'number' ? item.value.toFixed(2) : item.value}
        </p>
      ))}
    </div>
  )
}

export function TimelineChart({ data }: { data: TimelineResponse }) {
  const rows = data.buckets.map((bucket) => ({
    ...bucket,
    label: tickLabel(bucket.timestamp),
  }))

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={rows} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="volumeFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3d3ce0" stopOpacity={0.22} />
              <stop offset="100%" stopColor="#3d3ce0" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e6e1d6" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: '#6f6b64' }}
            axisLine={false}
            tickLine={false}
            minTickGap={24}
          />
          <YAxis
            yAxisId="count"
            tick={{ fontSize: 11, fill: '#6f6b64' }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <YAxis
            yAxisId="sentiment"
            orientation="right"
            domain={[-1, 1]}
            tick={{ fontSize: 11, fill: '#6f6b64' }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip content={<ChartTip />} />
          <Area
            yAxisId="count"
            type="monotone"
            dataKey="count"
            fill="url(#volumeFill)"
            stroke="#3d3ce0"
            strokeWidth={2}
            name="Volume"
          />
          <Line
            yAxisId="sentiment"
            type="monotone"
            dataKey="average_sentiment"
            stroke="#141413"
            strokeWidth={1.6}
            dot={false}
            name="Polarity"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
