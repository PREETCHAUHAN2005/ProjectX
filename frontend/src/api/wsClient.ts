import type { WsEnvelope, WsFilterCriteria } from '../types/contracts'
import { wsUrl } from './config'

const EVENT_NAMES = new Set([
  'event:new_post',
  'event:trend_spike',
  'event:graph_delta',
])

function isWsEnvelope(value: unknown): value is WsEnvelope {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const record = value as { event?: unknown; payload?: unknown }
  return (
    typeof record.event === 'string' &&
    EVENT_NAMES.has(record.event) &&
    record.payload !== undefined
  )
}

export type WsHandlers = {
  onEvent: (envelope: WsEnvelope) => void
  onMalformed: (raw: string) => void
  onOpen: () => void
  onClose: () => void
  onError: () => void
}

export class DashboardSocket {
  private socket: WebSocket | null = null
  private readonly handlers: WsHandlers

  constructor(handlers: WsHandlers) {
    this.handlers = handlers
  }

  connect(): void {
    this.disconnect()
    const socket = new WebSocket(wsUrl())
    this.socket = socket

    socket.onopen = () => {
      this.handlers.onOpen()
    }
    socket.onclose = () => {
      this.handlers.onClose()
    }
    socket.onerror = () => {
      this.handlers.onError()
    }
    socket.onmessage = (message: MessageEvent<string>) => {
      const raw = typeof message.data === 'string' ? message.data : ''
      try {
        const parsed: unknown = JSON.parse(raw)
        if (!isWsEnvelope(parsed)) {
          this.handlers.onMalformed(raw)
          return
        }
        this.handlers.onEvent(parsed)
      } catch {
        this.handlers.onMalformed(raw)
      }
    }
  }

  sendFilter(criteria: WsFilterCriteria): void {
    if (this.socket === null || this.socket.readyState !== WebSocket.OPEN) {
      return
    }
    this.socket.send(JSON.stringify(criteria))
  }

  disconnect(): void {
    if (this.socket !== null) {
      this.socket.onopen = null
      this.socket.onclose = null
      this.socket.onerror = null
      this.socket.onmessage = null
      this.socket.close()
      this.socket = null
    }
  }
}
