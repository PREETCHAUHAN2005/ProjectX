export function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ name?: string; value?: number | string; color?: string }>
  label?: string
}) {
  if (!active || !payload?.length) {
    return null
  }
  return (
    <div className="rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-sm text-ink">
      {label ? <p className="mb-1 text-muted">{label}</p> : null}
      {payload.map((item, index) => {
        const value =
          typeof item.value === 'number'
            ? item.name === 'Polarity' || !Number.isInteger(item.value)
              ? item.value.toFixed(2)
              : String(item.value)
            : String(item.value ?? '')
        return (
          <p key={`${item.name ?? 'item'}-${index}`} className="tabular text-ink">
            {item.color ? (
              <span
                className="mr-2 inline-block h-2 w-2 rounded-full"
                style={{ background: item.color }}
              />
            ) : null}
            {item.name}: {value}
          </p>
        )
      })}
    </div>
  )
}
