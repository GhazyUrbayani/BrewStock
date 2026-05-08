// Dibantu AI: KpiCard
import './KpiCard.css'

type KpiCardProps = {
  label: string
  value: number
  unit: string
  delta: number
  deltaPercent: number
  target: number
  targetLabel: string
}

const numberFormatter = new Intl.NumberFormat('id-ID', {
  maximumFractionDigits: 1,
})

function formatNumber(value: number) {
  return numberFormatter.format(value)
}

export default function KpiCard({
  label,
  value,
  unit,
  delta,
  deltaPercent,
  target,
  targetLabel,
}: KpiCardProps) {
  const unitValue = unit.trim()
  const deltaTone =
    deltaPercent === 0 ? 'neutral' : deltaPercent > 0 ? 'positive' : 'negative'
  const deltaDirection = deltaPercent < 0 ? 'down' : 'up'
  const statusTone = value >= target ? 'positive' : 'negative'
  const statusText = value >= target ? 'Di atas target' : 'Di bawah target'
  const deltaSign = delta > 0 ? '+' : delta < 0 ? '-' : ''
  const formattedDelta = `${deltaSign}${formatNumber(Math.abs(delta))}`
  const formattedPercent = `${formatNumber(Math.abs(deltaPercent))}%`
  const formattedTarget = `${formatNumber(target)}${unitValue ? ` ${unitValue}` : ''}`

  return (
    <article className="kpi-card">
      <div className="kpi-card-header">
        <span className="kpi-card-label">{label}</span>
        <span className={`kpi-card-status ${statusTone}`}>{statusText}</span>
      </div>
      <div className="kpi-card-value">
        <strong>{formatNumber(value)}</strong>
        {unitValue ? <span className="kpi-card-unit">{unitValue}</span> : null}
      </div>
      <div className={`kpi-card-delta ${deltaTone}`}>
        <svg
          className={`kpi-card-delta-icon ${deltaDirection}`}
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M12 4l-6 6h4v10h4V10h4z" fill="currentColor" />
        </svg>
        <span>{formattedDelta}</span>
        <span className="kpi-card-delta-percent">{formattedPercent}</span>
      </div>
      <div className="kpi-card-target">
        <span className="kpi-card-target-label">{targetLabel}</span>
        <span className="kpi-card-target-value">{formattedTarget}</span>
      </div>
    </article>
  )
}

export type { KpiCardProps }
