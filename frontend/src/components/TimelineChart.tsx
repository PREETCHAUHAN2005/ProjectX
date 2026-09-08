import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TimelineResponse } from '../types/contracts'
import { useChartColors } from '../lib/theme'
import { ChartTooltip } from './ChartTooltip'

function tickLabel(value: string): string {
  const stamp = Date.parse(value)
  if (Number.isNaN(stamp)) {
    return value.slice(11, 16)
  }
  return new Date(stamp).toLocaleString('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
  })
}

export function TimelineChart({ data }: { data: TimelineResponse }) {
  const colors = useChartColors()
  const rows = data.buckets.map((bucket) => ({
    label: tickLabel(bucket.timestamp),
    Posts: bucket.post_count ?? 0,
    Comments: bucket.comment_count ?? Math.max(bucket.count - (bucket.post_count ?? 0), 0),
    Polarity: bucket.average_sentiment,
  }))

  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke={colors.grid} strokeDasharray="3 6" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: colors.tick }}
            axisLine={false}
            tickLine={false}
            minTickGap={28}
            label={{
              value: 'Time',
              position: 'insideBottomRight',
              offset: -2,
              fontSize: 11,
              fill: colors.tick,
            }}
          />
          <YAxis
            yAxisId="count"
            tick={{ fontSize: 11, fill: colors.tick }}
            axisLine={false}
            tickLine={false}
            width={36}
            label={{
              value: 'Count',
              angle: -90,
              position: 'insideLeft',
              fontSize: 11,
              fill: colors.tick,
            }}
          />
          <YAxis
            yAxisId="sentiment"
            orientation="right"
            domain={[-1, 1]}
            tick={{ fontSize: 11, fill: colors.tick }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip content={<ChartTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ fontSize: 12, color: colors.legend, paddingBottom: 8 }}
          />
          <Line
            yAxisId="count"
            type="monotone"
            dataKey="Posts"
            stroke="#1e3a8a"
            strokeWidth={2.4}
            dot={{ r: 3, fill: '#1e3a8a', strokeWidth: 0 }}
          />
          <Line
            yAxisId="count"
            type="monotone"
            dataKey="Comments"
            stroke="#f97316"
            strokeWidth={2.4}
            dot={{ r: 3, fill: '#f97316', strokeWidth: 0 }}
          />
          <Line
            yAxisId="sentiment"
            type="monotone"
            dataKey="Polarity"
            stroke="#0f766e"
            strokeWidth={1.6}
            strokeDasharray="5 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
