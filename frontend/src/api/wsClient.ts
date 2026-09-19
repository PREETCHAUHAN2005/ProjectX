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
  private closedByUser = false
  private attempt = 0
  private timer: number | null = null
  private readonly handlers: WsHandlers

  constructor(handlers: WsHandlers) {
    this.handlers = handlers
  }

  connect(): void {
    this.closedByUser = false
    this.attempt = 0
    this.open()
  }

  private open(): void {
    this.disconnectSocketOnly()
    const socket = new WebSocket(wsUrl())
    this.socket = socket

    socket.onopen = () => {
      this.attempt = 0
      this.handlers.onOpen()
    }
    socket.onclose = () => {
      this.handlers.onClose()
      if (!this.closedByUser) {
        this.scheduleReconnect()
      }
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

  private scheduleReconnect(): void {
    if (this.timer !== null) {
      window.clearTimeout(this.timer)
    }
    const delay = Math.min(8000, 600 * 2 ** this.attempt)
    this.attempt += 1
    this.timer = window.setTimeout(() => {
      this.open()
    }, delay)
  }

  sendFilter(criteria: WsFilterCriteria): void {
    if (this.socket === null || this.socket.readyState !== WebSocket.OPEN) {
      return
    }
    this.socket.send(JSON.stringify(criteria))
  }

  disconnect(): void {
    this.closedByUser = true
    if (this.timer !== null) {
      window.clearTimeout(this.timer)
      this.timer = null
    }
    this.disconnectSocketOnly()
  }

  private disconnectSocketOnly(): void {
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
