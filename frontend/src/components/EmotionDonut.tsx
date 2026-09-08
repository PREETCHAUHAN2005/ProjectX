import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { EmotionScore } from '../types/contracts'
import { emotionColor } from './NetworkCanvas'

export function EmotionDonut({ emotions }: { emotions: EmotionScore[] }) {
  const rows = emotions.slice(0, 6)
  if (rows.length === 0) {
    return <p className="text-sm text-muted">No emotion scores in this window.</p>
  }
  const total = rows.reduce((sum, row) => sum + row.score, 0) || 1

  return (
    <div className="grid gap-4 md:grid-cols-[1fr_1fr] items-center">
      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={rows}
              dataKey="score"
              nameKey="label"
              innerRadius={48}
              outerRadius={68}
              paddingAngle={2}
            >
              {rows.map((item) => (
                <Cell key={item.label} fill={emotionColor(item.label)} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="space-y-2 text-[13px]">
        {rows.map((item) => (
          <li key={item.label} className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 capitalize text-ink">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ background: emotionColor(item.label) }}
              />
              {item.label}
            </span>
            <span className="tabular text-muted">
              {((item.score / total) * 100).toFixed(0)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
