import { DemographicsPanel } from './components/DemographicsPanel'
import { EmotionModelPanel } from './components/EmotionModelPanel'
import { LiveFeed } from './components/LiveFeed'
import { MetricStrip } from './components/MetricStrip'
import { NetworkCanvas } from './components/NetworkCanvas'
import { TimelineChart } from './components/TimelineChart'
import { TrendingList } from './components/TrendingList'
import { WidgetPanel } from './components/WidgetPanel'
import { hoursAgo } from './lib/format'
import { PROTOTYPE_NOTICE } from './lib/prototypeData'
import { useDashboard } from './lib/useDashboard'

function StatusChip({
  label,
  tone,
}: {
  label: string
  tone: 'live' | 'preview' | 'warn'
}) {
  const color =
    tone === 'live' ? 'bg-good' : tone === 'warn' ? 'bg-bad' : 'bg-warn'
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 text-[11px] font-medium text-ink">
      <span className={`h-1.5 w-1.5 rounded-full ${color}`} />
      {label}
    </span>
  )
}

export default function App() {
  const dashboard = useDashboard()
  const field =
    'mt-1 w-full rounded-xl border border-line bg-canvas px-3 py-2 text-[13px] text-ink outline-none focus:border-ink'

  return (
    <div className="min-h-svh bg-canvas text-ink">
      <div className="flex min-h-svh">
        <aside className="hidden w-[248px] shrink-0 border-r border-line bg-surface px-5 py-6 lg:block">
          <p className="font-serif text-[28px] leading-none">ProjectX</p>
          <p className="mt-1 text-[12px] text-muted">Social intelligence</p>
          <nav className="mt-10 space-y-1 text-[13px]">
            {['Overview', 'Timeline', 'Network', 'Demographics', 'Live feed'].map(
              (item, index) => (
                <div
                  key={item}
                  className={`rounded-xl px-3 py-2 ${index === 0 ? 'bg-canvas font-medium' : 'text-muted'}`}
                >
                  {item}
                </div>
              ),
            )}
          </nav>
          <div className="mt-10 rounded-2xl bg-canvas px-3 py-3 text-[12px] text-muted">
            Colab model attaches through VITE_MODEL_URL. The console stays usable without it.
          </div>
        </aside>

        <div className="min-w-0 flex-1">
          <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4 lg:px-8">
            <div>
              <p className="text-[11px] font-medium tracking-[0.14em] text-muted uppercase">
                Analyst console
              </p>
              <h1 className="font-serif text-[32px] leading-none">Intelligence</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip
                label={`API ${dashboard.apiStatus}`}
                tone={dashboard.dataMode === 'live' ? 'live' : 'preview'}
              />
              <StatusChip
                label={`WS ${dashboard.wsStatus}`}
                tone={dashboard.wsStatus === 'connected' ? 'live' : 'preview'}
              />
              <button
                type="button"
                onClick={() => {
                  dashboard.setPreferPrototype(!dashboard.preferPrototype)
                }}
                className="rounded-full border border-line px-3 py-1.5 text-[12px] font-medium"
              >
                {dashboard.preferPrototype ? 'Using preview' : 'Force preview'}
              </button>
            </div>
          </header>

          {dashboard.dataMode === 'prototype' ? (
            <p className="border-b border-line bg-accent-soft px-5 py-2 text-[12px] text-ink lg:px-8">
              {PROTOTYPE_NOTICE}
            </p>
          ) : null}

          {dashboard.spikeNotice ? (
            <div className="flex items-center justify-between gap-3 border-b border-line bg-bad-soft px-5 py-2 text-[12px] lg:px-8">
              <span>Spike: {dashboard.spikeNotice}</span>
              <button type="button" className="underline" onClick={dashboard.clearSpike}>
                Dismiss
              </button>
            </div>
          ) : null}

          <div className="space-y-5 px-5 py-5 lg:px-8">
            <form
              className="grid gap-3 rounded-2xl border border-line bg-surface p-4 md:grid-cols-4"
              onSubmit={(event) => {
                event.preventDefault()
                void dashboard.reload()
              }}
            >
              <label className="text-[11px] font-medium text-muted">
                Topic
                <input
                  className={field}
                  value={dashboard.topic}
                  placeholder="flood relief"
                  onChange={(event) => {
                    dashboard.setTopic(event.target.value)
                  }}
                />
              </label>
              <label className="text-[11px] font-medium text-muted">
                From
                <input
                  type="datetime-local"
                  className={field}
                  value={dashboard.from}
                  onChange={(event) => {
                    dashboard.setFrom(event.target.value)
                  }}
                />
              </label>
              <label className="text-[11px] font-medium text-muted">
                To
                <input
                  type="datetime-local"
                  className={field}
                  value={dashboard.to}
                  onChange={(event) => {
                    dashboard.setTo(event.target.value)
                  }}
                />
              </label>
              <label className="text-[11px] font-medium text-muted">
                Severity
                <select
                  className={field}
                  value={dashboard.severity}
                  onChange={(event) => {
                    dashboard.setSeverity(event.target.value)
                  }}
                >
                  <option value="">All</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>
              <div className="flex flex-wrap items-end gap-2 md:col-span-4">
                {[6, 24, 168].map((hours) => (
                  <button
                    key={hours}
                    type="button"
                    className="rounded-full border border-line px-3 py-1.5 text-[12px]"
                    onClick={() => {
                      dashboard.setFrom(hoursAgo(hours))
                      dashboard.setTo(hoursAgo(0))
                    }}
                  >
                    {hours === 168 ? '7d' : `${hours}h`}
                  </button>
                ))}
                <button
                  type="submit"
                  className="rounded-full bg-ink px-4 py-1.5 text-[12px] font-medium text-white"
                >
                  Apply
                </button>
              </div>
            </form>

            <MetricStrip
              volume={dashboard.metrics.volume}
              polarity={dashboard.metrics.polarity}
              topics={dashboard.metrics.topics}
              nodes={dashboard.metrics.nodes}
            />

            <div className="grid gap-4 xl:grid-cols-2">
              <WidgetPanel
                title="Timeline"
                description="Volume and polarity"
                state={dashboard.timeline}
              >
                {dashboard.timeline.data ? (
                  <TimelineChart data={dashboard.timeline.data} />
                ) : null}
              </WidgetPanel>
              <WidgetPanel
                title="Network"
                description="PageRank-scaled influence"
                state={dashboard.graph}
              >
                {dashboard.graph.data ? (
                  <NetworkCanvas data={dashboard.graph.data} />
                ) : null}
              </WidgetPanel>
              <WidgetPanel
                title="Demographics"
                description="Country density, profession, language"
                state={dashboard.demographics}
              >
                {dashboard.demographics.data ? (
                  <DemographicsPanel data={dashboard.demographics.data} />
                ) : null}
              </WidgetPanel>
              <WidgetPanel
                title="Trending"
                description="Velocity ranked topics"
                state={dashboard.trending}
              >
                {dashboard.trending.data ? (
                  <TrendingList
                    data={dashboard.trending.data}
                    onSelect={(topic) => {
                      dashboard.setTopic(topic)
                    }}
                  />
                ) : null}
              </WidgetPanel>
              <section className="rounded-2xl border border-line bg-surface p-5">
                <h2 className="mb-1 text-[13px] font-semibold">Live feed</h2>
                <p className="mb-3 text-[12px] text-muted">event:new_post · capped at 50</p>
                <LiveFeed posts={dashboard.feed} />
              </section>
              <section className="rounded-2xl border border-line bg-surface p-5">
                <h2 className="mb-1 text-[13px] font-semibold">Emotion model</h2>
                <p className="mb-3 text-[12px] text-muted">
                  Slot for the Colab GoEmotions export
                </p>
                <EmotionModelPanel />
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
