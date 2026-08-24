import { useState } from 'react'
import {
  isModelConfigured,
  predictEmotions,
  previewEmotions,
  type EmotionBar,
} from '../lib/modelClient'

export function EmotionModelPanel() {
  const [text, setText] = useState(
    'Relief operations expanded after overnight rain. Power restored in two districts.',
  )
  const [rows, setRows] = useState<EmotionBar[]>(() => previewEmotions(text).slice(0, 8))
  const [mode, setMode] = useState<'preview' | 'live' | 'error'>('preview')
  const [busy, setBusy] = useState(false)
  const connected = isModelConfigured()

  async function run(): Promise<void> {
    setBusy(true)
    try {
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
      <p className="text-[12px] text-muted">
        {connected
          ? 'Colab / FastAPI model is configured (`VITE_MODEL_URL`).'
          : 'Model offline — preview mapping only. Set VITE_MODEL_URL after Colab export.'}
        {mode === 'error' ? ' Last call failed; showing preview.' : ''}
      </p>
      <textarea
        value={text}
        onChange={(event) => {
          setText(event.target.value)
        }}
        rows={3}
        className="w-full resize-none rounded-xl border border-line bg-canvas px-3 py-2 text-[13px] outline-none focus:border-ink"
      />
      <button
        type="button"
        disabled={busy || text.trim().length === 0}
        onClick={() => {
          void run()
        }}
        className="rounded-full bg-ink px-4 py-1.5 text-[12px] font-medium text-white disabled:opacity-40"
      >
        {busy ? 'Scoring…' : connected ? 'Run model' : 'Preview scores'}
      </button>
      <ul className="space-y-1.5">
        {rows.map((row) => (
          <li key={row.label} className="grid grid-cols-[7rem_1fr_2.5rem] items-center gap-2 text-[12px]">
            <span className="truncate text-ink">{row.label}</span>
            <div className="h-1.5 overflow-hidden rounded-full bg-[#eeeae2]">
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
