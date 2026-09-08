import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { DemographicsResponse } from '../types/contracts'
import { ChoroplethMap } from './ChoroplethMap'

const PALETTE = ['#0f172a', '#1e3a8a', '#f97316', '#0f766e', '#dc2626', '#64748b']

export function DemographicsPanel({ data }: { data: DemographicsResponse }) {
  return (
    <div className="space-y-5">
      <ChoroplethMap slices={data.country} />
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <p className="mb-2 text-[11px] font-medium tracking-wide text-muted uppercase">
            Profession
          </p>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.profession}
                  dataKey="count"
                  nameKey="key"
                  innerRadius={38}
                  outerRadius={56}
                  paddingAngle={2}
                >
                  {data.profession.map((item, index) => (
                    <Cell key={item.key} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <p className="mb-2 text-[11px] font-medium tracking-wide text-muted uppercase">
            Language
          </p>
          <ul className="space-y-1.5 text-sm">
            {data.language.map((item) => (
              <li key={item.key} className="flex justify-between">
                <span className="text-ink">{item.key}</span>
                <span className="tabular text-muted">{item.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
