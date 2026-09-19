import { useState } from 'react'
import { predictNlp } from '../api/client'
import {
  bucketForLabel,
  isModelConfigured,
  predictEmotions,
  previewEmotions,
  type EmotionBar,
} from '../lib/modelClient'

export function EmotionModelPanel() {
  const [text, setText] = useState(
    'Orange alert: heavy rain over Mumbai. Water entered our building lobby. Need pumps.',
  )
  const [rows, setRows] = useState<EmotionBar[]>(() => previewEmotions(text).slice(0, 8))
  const [mode, setMode] = useState<'preview' | 'live' | 'error'>('preview')
  const [busy, setBusy] = useState(false)
  const connected = isModelConfigured()

  async function run(): Promise<void> {
    setBusy(true)
    try {
      try {
        const local = await predictNlp(text)
        setRows(
          local.emotions.slice(0, 8).map((row) => ({
            label: row.label,
            score: row.score,
            bucket: bucketForLabel(row.label),
          })),
        )
        setMode('live')
        return
      } catch {
        // fall through to optional Colab URL
      }
      const remote = await predictEmotions(text)
      if (remote === null) {
        setRows(previewEmotions(text).slice(0, 8))
        setMode('preview')
        return
      }
      setRows(remote.slice(0, 8))
      setMode('live')
    } catch {
      setRows(previewEmotions(text).slice(0, 8))
      setMode('error')
    } finally {
      setBusy(false)
    }
  }

  const max = Math.max(...rows.map((row) => row.score), 0.001)

  return (
    <div className="space-y-3">
      <p className="text-[13px] leading-5 text-muted">
        Scores the 28 GoEmotions labels through the local FastAPI pipeline
        {connected ? ' (Colab URL also configured).' : '.'}
        {mode === 'error' ? ' Last call failed; showing preview.' : ''}
      </p>
      <textarea
        value={text}
        onChange={(event) => {
          setText(event.target.value)
        }}
        rows={3}
        className="w-full resize-none rounded-2xl border border-line bg-inset px-3.5 py-3 text-[13px] text-ink outline-none focus:border-accent"
      />
      <button
        type="button"
        disabled={busy || text.trim().length === 0}
        onClick={() => {
          void run()
        }}
        className="rounded-full bg-accent px-4 py-1.5 text-[12px] font-semibold text-white disabled:opacity-40"
      >
        {busy ? 'Scoring…' : 'Run pipeline'}
      </button>
      <ul className="space-y-1.5">
        {rows.map((row) => (
          <li key={row.label} className="grid grid-cols-[7rem_1fr_2.5rem] items-center gap-2 text-[12px]">
            <span className="truncate text-ink">{row.label}</span>
            <div className="h-1.5 overflow-hidden rounded-full bg-line">
              <div
                className={`h-full rounded-full ${row.bucket === 'NEGATIVE' ? 'bg-bad' : row.bucket === 'POSITIVE' ? 'bg-good' : 'bg-ink'}`}
                style={{ width: `${(row.score / max) * 100}%` }}
              />
            </div>
            <span className="tabular text-right text-muted">{row.score.toFixed(2)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
