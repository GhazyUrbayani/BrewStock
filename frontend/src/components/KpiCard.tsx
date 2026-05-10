// Dibantu AI: KpiCard
import './KpiCard.css'
import type { KpiCardType } from '../types'

export default function KpiCard({
  label,
  value,
  trend,
  trendDirection,
  targetText,
  statusBadge,
  statusCondition,
}: KpiCardType) {
  return (
    <article className="kpi-card">
      <div className="kpi-card-header">
        <span className="kpi-card-label">{label}</span>
      </div>
      <div className="kpi-card-value">
        <strong>{value}</strong>
      </div>
      <div className={`kpi-card-delta ${trendDirection}`}>
        <span>{trend}</span>
      </div>
      <div className="kpi-card-target">
        <span className="kpi-card-target-label">{targetText}</span>
        <span className={`kpi-card-status ${statusCondition}`}>
          {statusBadge}
        </span>
      </div>
    </article>
  )
}
