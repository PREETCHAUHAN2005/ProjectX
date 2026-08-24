declare module 'react-force-graph-2d' {
  import type { ComponentType } from 'react'

  export type ForceGraphProps = {
    graphData: {
      nodes: Array<Record<string, unknown>>
      links: Array<Record<string, unknown>>
    }
    width?: number
    height?: number
    backgroundColor?: string
    nodeLabel?: string
    nodeVal?: string
    nodeColor?: string | ((node: Record<string, unknown>) => string)
    linkColor?: string | ((link: Record<string, unknown>) => string)
    linkWidth?: number
    linkDirectionalArrowLength?: number
    cooldownTicks?: number
    enableNodeDrag?: boolean
    d3VelocityDecay?: number
    nodeCanvasObject?: (
      node: Record<string, unknown> & { x?: number; y?: number },
      ctx: CanvasRenderingContext2D,
      globalScale: number,
    ) => void
  }

  const ForceGraph2D: ComponentType<ForceGraphProps>
  export default ForceGraph2D
}
