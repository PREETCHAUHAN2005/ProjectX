import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { useChartColors, useTheme } from '../lib/theme'
import type { NetworkGraphResponse } from '../types/contracts'

const MAX_NODES = 200

const EMOTION_COLORS: Record<string, string> = {
  fear: '#f97316',
  anger: '#dc2626',
  annoyance: '#ea580c',
  approval: '#1e3a8a',
  optimism: '#0f766e',
  relief: '#c2410c',
  sadness: '#2563eb',
  caring: '#0369a1',
  gratitude: '#15803d',
  nervousness: '#a16207',
  realization: '#334155',
  disappointment: '#7c3aed',
  curiosity: '#0e7490',
  neutral: '#64748b',
  joy: '#ca8a04',
}

export function emotionColor(community: string): string {
  const key = community.toLowerCase()
  if (key in EMOTION_COLORS) {
    return EMOTION_COLORS[key]
  }
  let hash = 0
  for (let i = 0; i < community.length; i += 1) {
    hash = (hash * 31 + community.charCodeAt(i)) >>> 0
  }
  return `hsl(${hash % 360} 45% 38%)`
}

export function NetworkCanvas({ data }: { data: NetworkGraphResponse }) {
  const wrap = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState({ width: 520, height: 300 })
  const { theme } = useTheme()
  const colors = useChartColors()

  useEffect(() => {
    const node = wrap.current
    if (!node) {
      return
    }
    const update = (): void => {
      setSize({ width: node.clientWidth, height: Math.max(node.clientHeight, 300) })
    }
    update()
    const observer = new ResizeObserver(update)
    observer.observe(node)
    return () => {
      observer.disconnect()
    }
  }, [])

  const truncated = data.nodes.length > MAX_NODES
  const graphData = useMemo(() => {
    const nodes = data.nodes.slice(0, MAX_NODES)
    const allowed = new Set(nodes.map((item) => item.id))
    return {
      nodes: nodes.map((node) => ({
        id: node.id,
        handle: node.handle,
        pagerank: node.pagerank,
        community: node.community,
        val: Math.max(node.pagerank, 0.001) * 140,
        color: emotionColor(node.community),
      })),
      links: data.links
        .filter((link) => allowed.has(link.source) && allowed.has(link.target))
        .map((link) => ({
          source: link.source,
          target: link.target,
          weight: link.weight,
        })),
    }
  }, [data])

  const legend = useMemo(() => {
    const seen = new Map<string, string>()
    for (const node of graphData.nodes) {
      if (!seen.has(node.community)) {
        seen.set(node.community, node.color)
      }
    }
    return [...seen.entries()].slice(0, 8)
  }, [graphData.nodes])

  if (data.nodes.length === 0) {
    return <p className="text-sm text-muted">No graph nodes for this window.</p>
  }

  return (
    <div className="space-y-2">
      {truncated ? (
        <p className="text-[12px] text-muted">
          Showing {MAX_NODES} of {data.nodes.length} people for canvas performance.
        </p>
      ) : null}
      <div className="flex flex-wrap gap-2">
        {legend.map(([label, color]) => (
          <span key={label} className="inline-flex items-center gap-1.5 text-[11px] capitalize text-muted">
            <span className="h-2 w-2 rounded-full" style={{ background: color }} />
            {label}
          </span>
        ))}
      </div>
      <div ref={wrap} className="h-[300px] w-full overflow-hidden rounded-2xl bg-inset">
        <ForceGraph2D
          key={theme}
          width={size.width}
          height={size.height}
          backgroundColor={colors.canvas}
          graphData={graphData}
          nodeLabel="handle"
          nodeVal="val"
          linkColor={() => colors.link}
          linkWidth={1.2}
          cooldownTicks={48}
          d3VelocityDecay={0.35}
          enableNodeDrag
          nodeCanvasObject={(node, ctx, scale) => {
            const x = node.x ?? 0
            const y = node.y ?? 0
            const rank = typeof node.pagerank === 'number' ? node.pagerank : 0.04
            const radius = Math.max(4, rank * 32)
            ctx.beginPath()
            ctx.arc(x, y, radius, 0, 2 * Math.PI)
            ctx.fillStyle = typeof node.color === 'string' ? node.color : '#1e3a8a'
            ctx.fill()
            ctx.strokeStyle = colors.nodeStroke
            ctx.lineWidth = 1.4
            ctx.stroke()
            const handle = typeof node.handle === 'string' ? node.handle : ''
            if (handle) {
              ctx.font = `${Math.max(9, 11 / Math.max(scale, 0.7))}px Inter, sans-serif`
              ctx.fillStyle = colors.ink
              ctx.textAlign = 'center'
              ctx.fillText(handle, x, y + radius + 10 / Math.max(scale, 0.7))
            }
          }}
        />
      </div>
    </div>
  )
}
