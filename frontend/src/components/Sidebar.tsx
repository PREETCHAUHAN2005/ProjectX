import { isModelConfigured } from '../lib/modelClient'
import type { DataMode } from '../lib/useDashboard'

export type SidebarSection =
  | 'overview'
  | 'timeline'
  | 'network'
  | 'demographics'
  | 'trending'
  | 'live'
  | 'model'

const NAV: Array<{
  id: SidebarSection
  label: string
  hint: string
  icon: string
}> = [
  { id: 'overview', label: 'Overview', hint: 'KPIs and filters', icon: 'grid' },
  { id: 'timeline', label: 'Timeline', hint: 'Posts · comments', icon: 'pulse' },
  { id: 'network', label: 'Network', hint: 'People · emotions', icon: 'nodes' },
  { id: 'demographics', label: 'People', hint: 'Geo · language', icon: 'globe' },
  { id: 'trending', label: 'Trending', hint: 'Velocity rank', icon: 'trend' },
  { id: 'live', label: 'Live feed', hint: 'Incoming posts', icon: 'feed' },
  { id: 'model', label: 'Emotion model', hint: 'GoEmotions slot', icon: 'spark' },
]

function NavIcon({ name }: { name: string }) {
  const common = {
    width: 16,
    height: 16,
    viewBox: '0 0 16 16',
    fill: 'none',
    'aria-hidden': true as const,
  }
  if (name === 'grid') {
    return (
      <svg {...common}>
        <rect x="2" y="2" width="5" height="5" rx="1.2" stroke="currentColor" strokeWidth="1.4" />
        <rect x="9" y="2" width="5" height="5" rx="1.2" stroke="currentColor" strokeWidth="1.4" />
        <rect x="2" y="9" width="5" height="5" rx="1.2" stroke="currentColor" strokeWidth="1.4" />
        <rect x="9" y="9" width="5" height="5" rx="1.2" stroke="currentColor" strokeWidth="1.4" />
      </svg>
    )
  }
  if (name === 'pulse') {
    return (
      <svg {...common}>
        <path
          d="M1 8h3l2-4 3 8 2-4h4"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
      </svg>
    )
  }
  if (name === 'nodes') {
    return (
      <svg {...common}>
        <circle cx="4" cy="4" r="2" stroke="currentColor" strokeWidth="1.4" />
        <circle cx="12" cy="5" r="2" stroke="currentColor" strokeWidth="1.4" />
        <circle cx="8" cy="12" r="2" stroke="currentColor" strokeWidth="1.4" />
        <path d="M5.6 5.2 10.4 6M5.5 5.8 7.2 10.4M10.5 6.8 9 10.4" stroke="currentColor" strokeWidth="1.2" />
      </svg>
    )
  }
  if (name === 'globe') {
    return (
      <svg {...common}>
        <circle cx="8" cy="8" r="5.2" stroke="currentColor" strokeWidth="1.4" />
        <path d="M3 8h10M8 3c1.8 1.8 2.6 3.6 2.6 5S9.8 11.2 8 13C6.2 11.2 5.4 9.4 5.4 8S6.2 4.8 8 3Z" stroke="currentColor" strokeWidth="1.2" />
      </svg>
    )
  }
  if (name === 'trend') {
    return (
      <svg {...common}>
        <path d="M2 12 6.5 7.5 9 10l5-6" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
        <path d="M10 4h4v4" stroke="currentColor" strokeWidth="1.4" />
      </svg>
    )
  }
  if (name === 'feed') {
    return (
      <svg {...common}>
        <path d="M3 4h10M3 8h10M3 12h6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      </svg>
    )
  }
  return (
    <svg {...common}>
      <path d="M8 2.5 9.2 6h3.6L10 8.4 11.2 12 8 9.8 4.8 12 6 8.4 3.2 6h3.6L8 2.5Z" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  )
}

export function Sidebar({
  active,
  onNavigate,
  dataMode,
  apiStatus,
  wsStatus,
  volume,
  topicCount,
  onTogglePreview,
  preferPrototype,
}: {
  active: SidebarSection
  onNavigate: (id: SidebarSection) => void
  dataMode: DataMode
  apiStatus: string
  wsStatus: string
  volume: number
  topicCount: number
  onTogglePreview: () => void
  preferPrototype: boolean
}) {
  const modelOn = isModelConfigured()
  const live = dataMode === 'live'

  return (
    <aside className="sticky top-0 hidden h-svh w-[248px] shrink-0 flex-col border-r border-line bg-sidebar text-ink md:flex">
      <div className="flex items-center gap-3 border-b border-line px-4 py-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent text-[13px] font-bold text-white">
          PX
        </div>
        <div className="min-w-0">
          <p className="truncate text-[14px] font-semibold">ProjectX</p>
          <p className="truncate text-[11px] text-muted">NTRO · SIH 2026</p>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
        <p className="px-2 text-[10px] font-semibold tracking-[0.16em] text-muted uppercase">
          Console
        </p>
        <nav className="mt-2 space-y-0.5" aria-label="Dashboard sections">
          {NAV.map((item) => {
            const selected = item.id === active
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onNavigate(item.id)
                }}
                className={`flex w-full items-center gap-2.5 rounded-2xl px-2.5 py-2 text-left transition-colors ${
                  selected ? 'bg-accent text-white' : 'text-ink hover:bg-inset'
                }`}
              >
                <span className={selected ? 'text-white' : 'text-muted'}>
                  <NavIcon name={item.icon} />
                </span>
                <span className="min-w-0">
                  <span className="block text-[13px] font-medium">{item.label}</span>
                  <span className={`block text-[11px] ${selected ? 'text-white/80' : 'text-muted'}`}>
                    {item.hint}
                  </span>
                </span>
              </button>
            )
          })}
        </nav>

        <p className="mt-6 px-2 text-[10px] font-semibold tracking-[0.16em] text-muted uppercase">
          Sources
        </p>
        <ul className="mt-2 space-y-1.5 px-1">
          <li className="flex items-center justify-between rounded-2xl bg-inset px-3 py-2 text-[12px]">
            <span>Telegram</span>
            <span className={`font-medium ${live ? 'text-good' : 'text-warn'}`}>
              {live ? 'live' : 'preview'}
            </span>
          </li>
          <li className="flex items-center justify-between rounded-2xl bg-inset px-3 py-2 text-[12px]">
            <span>X / Twitter</span>
            <span className="font-medium text-muted">adapter</span>
          </li>
        </ul>

        <p className="mt-6 px-2 text-[10px] font-semibold tracking-[0.16em] text-muted uppercase">
          Session
        </p>
        <div className="mt-2 space-y-2 rounded-2xl bg-inset px-3 py-3 text-[12px]">
          <div className="flex justify-between gap-2">
            <span className="text-muted">Items in window</span>
            <span className="tabular font-medium">{volume.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted">Active topics</span>
            <span className="tabular font-medium">{topicCount}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted">API</span>
            <span className="truncate font-medium">{apiStatus}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted">Socket</span>
            <span className="truncate font-medium">{wsStatus}</span>
          </div>
          <div className="flex justify-between gap-2">
            <span className="text-muted">GoEmotions</span>
            <span className={`font-medium ${modelOn ? 'text-good' : 'text-muted'}`}>
              {modelOn ? 'connected' : 'offline'}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onTogglePreview}
          className="mt-3 w-full rounded-2xl border border-line bg-surface px-3 py-2 text-[12px] font-medium text-ink hover:bg-inset"
        >
          {preferPrototype ? 'Using preview data' : 'Force preview data'}
        </button>
      </div>

      <div className="border-t border-line px-4 py-3">
        <p className="text-[13px] font-medium">Analyst workspace</p>
        <p className="text-[11px] text-muted">Local console · not production auth</p>
      </div>
    </aside>
  )
}
