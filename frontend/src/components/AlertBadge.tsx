// Dibantu AI: AlertBadge
import './AlertBadge.css'

type AlertBadgeProps = {
  count: number
  tone?: 'neutral' | 'warning' | 'critical'
}

export default function AlertBadge({ count, tone = 'neutral' }: AlertBadgeProps) {
  const safeCount = Math.max(0, count)
  const labelText = `${safeCount} alert aktif`

  return (
    <span className={`alert-badge ${tone}`} role="status" aria-label={labelText}>
      {safeCount}
    </span>
  )
}

export type { AlertBadgeProps }
