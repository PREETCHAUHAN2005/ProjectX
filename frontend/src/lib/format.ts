export function formatCount(value: number): string {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value)
}

export function formatScore(value: number): string {
  return value.toFixed(2)
}

export function polarityWord(value: number): 'Positive' | 'Negative' | 'Neutral' {
  if (value > 0.08) {
    return 'Positive'
  }
  if (value < -0.08) {
    return 'Negative'
  }
  return 'Neutral'
}

export function relativeTime(iso: string): string {
  const then = Date.parse(iso)
  if (Number.isNaN(then)) {
    return iso
  }
  const delta = Date.now() - then
  const minutes = Math.max(0, Math.round(delta / 60000))
  if (minutes < 1) {
    return 'just now'
  }
  if (minutes < 60) {
    return `${minutes}m`
  }
  const hours = Math.round(minutes / 60)
  if (hours < 24) {
    return `${hours}h`
  }
  return `${Math.round(hours / 24)}d`
}

export function toDateTimeLocal(date: Date): string {
  const pad = (part: number): string => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function hoursAgo(hours: number): string {
  return toDateTimeLocal(new Date(Date.now() - hours * 3600 * 1000))
}
