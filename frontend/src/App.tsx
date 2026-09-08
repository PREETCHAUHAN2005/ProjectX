import { ThemeToggle } from './components/ThemeToggle'
import { DemographicsPanel } from './components/DemographicsPanel'
import { EmotionDonut } from './components/EmotionDonut'
import { EmotionModelPanel } from './components/EmotionModelPanel'
import { LiveFeed } from './components/LiveFeed'
import { MetricStrip } from './components/MetricStrip'
import { NetworkCanvas } from './components/NetworkCanvas'
import { PostDetails } from './components/PostDetails'
import { Sidebar, type SidebarSection } from './components/Sidebar'
import { TimelineChart } from './components/TimelineChart'
import { TrendingList } from './components/TrendingList'
import { WidgetPanel } from './components/WidgetPanel'
import { hoursAgo } from './lib/format'
import { PROTOTYPE_NOTICE } from './lib/prototypeData'
import { useDashboard } from './lib/useDashboard'
import { useState } from 'react'

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
    <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-inset px-2.5 py-1 text-[11px] font-medium text-ink">
      <span className={`h-1.5 w-1.5 rounded-full ${color}`} />
      {label}
    </span>
  )
}

export default function App() {
  const dashboard = useDashboard()
  const [section, setSection] = useState<SidebarSection>('overview')
  const field =
    'mt-1 w-full rounded-2xl border border-line bg-inset px-3 py-2 text-[13px] text-ink outline-none focus:border-accent'

  function goTo(id: SidebarSection): void {
    setSection(id)
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="min-h-svh bg-canvas text-ink">
      <div className="flex min-h-svh">
        <Sidebar
          active={section}
          onNavigate={goTo}
          dataMode={dashboard.dataMode}
          apiStatus={dashboard.apiStatus}
          wsStatus={dashboard.wsStatus}
          volume={dashboard.metrics.posts + dashboard.metrics.comments}
          topicCount={dashboard.metrics.topics}
          preferPrototype={dashboard.preferPrototype}
          onTogglePreview={() => {
            dashboard.setPreferPrototype(!dashboard.preferPrototype)
          }}
        />

        <div className="min-w-0 flex-1">
          <div className="flex gap-2 overflow-x-auto border-b border-line px-4 py-2 md:hidden">
            {['overview', 'timeline', 'network', 'live', 'model'].map((id) => (
              <button
                key={id}
                type="button"
                className="shrink-0 rounded-full border border-line bg-surface px-3 py-1 text-[12px] capitalize text-ink"
                onClick={() => {
                  goTo(id as SidebarSection)
                }}
              >
                {id}
              </button>
            ))}
          </div>
          <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-sidebar/80 px-5 py-4 backdrop-blur-sm lg:px-8">
            <div>
              <p className="text-[11px] font-medium tracking-[0.14em] text-muted uppercase">
                Social intelligence
              </p>
              <h1 className="text-[32px] font-extrabold leading-none tracking-tight text-ink">
                Analytics
              </h1>
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
              <ThemeToggle />
            </div>
          </header>

          {dashboard.dataMode === 'prototype' ? (
            <p className="border-b border-line bg-accent-soft px-5 py-2 text-[12px] text-ink lg:px-8">
              {PROTOTYPE_NOTICE}
            </p>
          ) : null}

          {dashboard.spikeNotice ? (
            <div className="flex items-center justify-between gap-3 border-b border-line bg-bad-soft px-5 py-2 text-[12px] text-ink lg:px-8">
              <span>Spike: {dashboard.spikeNotice}</span>
              <button type="button" className="underline" onClick={dashboard.clearSpike}>
                Dismiss
              </button>
            </div>
          ) : null}

          <div className="space-y-5 px-5 py-5 lg:px-8">
            <form
              id="overview"
              className="scroll-mt-4 grid gap-3 rounded-[20px] border border-line bg-surface p-4 text-ink card-shadow md:grid-cols-4"
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
                    className="rounded-full border border-line bg-inset px-3 py-1.5 text-[12px] text-ink hover:bg-surface"
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
                  className="rounded-full bg-accent px-4 py-1.5 text-[12px] font-semibold text-white"
                >
                  Apply
                </button>
              </div>
            </form>

            <MetricStrip
              posts={dashboard.metrics.posts}
              comments={dashboard.metrics.comments}
              topEmotion={dashboard.metrics.topEmotion}
              topics={dashboard.metrics.topics}
            />

            <div id="timeline" className="scroll-mt-4">
              <WidgetPanel
                title="Post and comment volume"
                description="Root posts vs thread comments over time"
                state={dashboard.timeline}
              >
                {dashboard.timeline.data ? (
                  <TimelineChart data={dashboard.timeline.data} />
                ) : null}
              </WidgetPanel>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <WidgetPanel
                title="Emotions in window"
                description="Mix of dominant GoEmotions labels"
                state={dashboard.timeline}
              >
                <EmotionDonut emotions={dashboard.emotions} />
              </WidgetPanel>
              <WidgetPanel
                title="Post details"
                description="Featured thread — post, comments, polarity"
                state={dashboard.timeline}
              >
                <PostDetails thread={dashboard.thread} />
              </WidgetPanel>
              <div id="network" className="scroll-mt-4">
                <WidgetPanel
                  title="People in the thread"
                  description="Handles sized by influence, colored by emotion"
                  state={dashboard.graph}
                >
                  {dashboard.graph.data ? (
                    <NetworkCanvas data={dashboard.graph.data} />
                  ) : null}
                </WidgetPanel>
              </div>
              <div id="demographics" className="scroll-mt-4">
                <WidgetPanel
                  title="Demographics"
                  description="Country density, profession, language"
                  state={dashboard.demographics}
                >
                  {dashboard.demographics.data ? (
                    <DemographicsPanel data={dashboard.demographics.data} />
                  ) : null}
                </WidgetPanel>
              </div>
              <div id="trending" className="scroll-mt-4">
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
              </div>
              <section
                id="live"
                className="scroll-mt-4 rounded-[20px] border border-line bg-surface p-5 text-ink card-shadow"
              >
                <h2 className="mb-1 text-[15px] font-bold">Live feed</h2>
                <p className="mb-4 text-[12px] text-muted">Posts and comments · event:new_post</p>
                <LiveFeed posts={dashboard.feed} />
              </section>
              <section
                id="model"
                className="scroll-mt-4 rounded-[20px] border border-line bg-surface p-5 text-ink card-shadow"
              >
                <h2 className="mb-1 text-[15px] font-bold">Emotion model</h2>
                <p className="mb-3 text-[13px] leading-5 text-muted">
                  Score a post with GoEmotions (Colab slot or preview)
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
