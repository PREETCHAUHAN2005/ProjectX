import type { ReactNode } from 'react'
import type { LoadState } from '../lib/loadState'

export function WidgetPanel({
  title,
  description,
  state,
  children,
  className = '',
  action,
}: {
  title: string
  description?: string
  state: LoadState<unknown>
  children: ReactNode
  className?: string
  action?: ReactNode
}) {
  return (
    <section
      className={`flex min-h-[320px] flex-col rounded-2xl border border-line bg-surface p-5 shadow-[0_1px_2px_rgba(20,20,19,0.04)] ${className}`}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-[13px] font-semibold tracking-wide text-ink">{title}</h2>
          {description ? (
            <p className="mt-0.5 text-[12px] text-muted">{description}</p>
          ) : null}
        </div>
        {action}
      </div>
      {state.status === 'loading' ? (
        <div className="flex flex-1 flex-col justify-end gap-2">
          <div className="h-24 animate-pulse rounded-xl bg-[#eeeae2]" />
          <div className="h-3 w-2/3 animate-pulse rounded bg-[#eeeae2]" />
          <div className="h-3 w-1/3 animate-pulse rounded bg-[#eeeae2]" />
        </div>
      ) : null}
      {state.status === 'error' ? (
        <p className="text-sm text-bad">{state.error ?? 'Request failed'}</p>
      ) : null}
      {state.status === 'empty' ? (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-line bg-canvas/60">
          <p className="text-sm text-muted">No records for this window.</p>
        </div>
      ) : null}
      {state.status === 'ready' ? <div className="min-h-0 flex-1">{children}</div> : null}
    </section>
  )
}
