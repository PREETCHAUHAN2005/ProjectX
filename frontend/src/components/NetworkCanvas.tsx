import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { NetworkGraphResponse } from '../types/contracts'

const MAX_NODES = 200

const COMMUNITY_COLORS: Record<string, string> = {
  civic: '#3d3ce0',
  infra: '#0f7a5a',
  weather: '#9a6700',
}

function communityColor(community: string): string {
  if (community in COMMUNITY_COLORS) {
    return COMMUNITY_COLORS[community]
  }
  let hash = 0
  for (let i = 0; i < community.length; i += 1) {
    hash = (hash * 31 + community.charCodeAt(i)) >>> 0
  }
  return `hsl(${hash % 360} 45% 38%)`
}

export function NetworkCanvas({ data }: { data: NetworkGraphResponse }) {
  const wrap = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState({ width: 520, height: 280 })

  useEffect(() => {
    const node = wrap.current
    if (!node) {
      return
    }
    const update = (): void => {
      setSize({ width: node.clientWidth, height: Math.max(node.clientHeight, 280) })
    }
    update()
    const observer = new ResizeObserver(update)
    observer.observe(node)
    return () => {
      observer.disconnect()
    }
  }, [])

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
        color: communityColor(node.community),
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

  if (data.nodes.length > MAX_NODES) {
    return (
      <p className="text-sm text-muted">
        Graph truncated at {MAX_NODES} nodes for canvas performance.
      </p>
    )
  }

  return (
    <div ref={wrap} className="h-[280px] w-full overflow-hidden rounded-xl bg-[#f7f4ee]">
      <ForceGraph2D
        width={size.width}
        height={size.height}
        backgroundColor="#f7f4ee"
        graphData={graphData}
        nodeLabel="handle"
        nodeVal="val"
        linkColor={() => 'rgba(20,20,19,0.18)'}
        linkWidth={1}
        cooldownTicks={48}
        d3VelocityDecay={0.35}
        enableNodeDrag
        nodeCanvasObject={(node, ctx, scale) => {
          const x = node.x ?? 0
          const y = node.y ?? 0
          const rank = typeof node.pagerank === 'number' ? node.pagerank : 0.04
          const radius = Math.max(3.5, rank * 28)
          ctx.beginPath()
          ctx.arc(x, y, radius, 0, 2 * Math.PI)
          ctx.fillStyle = typeof node.color === 'string' ? node.color : '#3d3ce0'
          ctx.fill()
          ctx.strokeStyle = '#fffcf7'
          ctx.lineWidth = 1.2
          ctx.stroke()
          if (scale > 1.4 && typeof node.handle === 'string') {
            ctx.font = `${11 / scale}px Inter, sans-serif`
            ctx.fillStyle = '#141413'
            ctx.textAlign = 'center'
            ctx.fillText(node.handle, x, y + radius + 8 / scale)
          }
        }}
      />
    </div>
  )
}
