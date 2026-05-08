// Dibantu AI: AlertPanel
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { InventoryAlert } from '../types'
import AlertBadge from './AlertBadge'
import './AlertPanel.css'

type AlertPanelProps = {
  authRequest: <T>(
    pathValue: string,
    optionsValue?: { method?: string; body?: unknown },
  ) => Promise<T>
  pollIntervalMs?: number
}

type AlertResponse = InventoryAlert[] | { alerts: InventoryAlert[] }

type AlertSeverity = 'neutral' | 'warning' | 'critical'

const numberFormatter = new Intl.NumberFormat('id-ID', {
  maximumFractionDigits: 1,
})

const dateFormatter = new Intl.DateTimeFormat('id-ID', {
  day: '2-digit',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

function formatNumber(value: number) {
  return numberFormatter.format(value)
}

function formatDate(value: string) {
  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return '-'
  }
  return dateFormatter.format(parsedDate)
}

function readErrorMessage(errorValue: unknown) {
  if (errorValue instanceof Error) {
    return errorValue.message
  }
  return 'Alert tidak dapat dimuat'
}

function readAlertItems(payloadValue: unknown): InventoryAlert[] {
  if (Array.isArray(payloadValue)) {
    return payloadValue as InventoryAlert[]
  }

  if (
    typeof payloadValue === 'object' &&
    payloadValue !== null &&
    'alerts' in payloadValue &&
    Array.isArray((payloadValue as { alerts: unknown }).alerts)
  ) {
    return (payloadValue as { alerts: InventoryAlert[] }).alerts
  }

  return []
}

function readSeverity(alertValue: InventoryAlert): AlertSeverity {
  if (alertValue.recommendedRestock <= 0) {
    return 'neutral'
  }

  if (alertValue.currentStock <= 0) {
    return 'critical'
  }

  const ratioValue = alertValue.recommendedRestock / alertValue.currentStock
  if (ratioValue >= 1) {
    return 'critical'
  }
  return ratioValue >= 0.4 ? 'warning' : 'neutral'
}

function readSeverityLabel(severityValue: AlertSeverity) {
  if (severityValue === 'critical') {
    return 'Kritis'
  }
  if (severityValue === 'warning') {
    return 'Perlu perhatian'
  }
  return 'Stabil'
}

export default function AlertPanel({ authRequest, pollIntervalMs }: AlertPanelProps) {
  const [alertItems, setAlertItems] = useState<InventoryAlert[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const loadAlerts = useCallback(async () => {
    setIsLoading(true)
    setErrorMessage(null)
    try {
      const payloadValue = await authRequest<AlertResponse>('/api/v1/inventory/alerts')
      setAlertItems(readAlertItems(payloadValue))
    } catch (errorValue) {
      setErrorMessage(readErrorMessage(errorValue))
    } finally {
      setIsLoading(false)
    }
  }, [authRequest])

  useEffect(() => {
    void loadAlerts()
  }, [loadAlerts])

  useEffect(() => {
    if (!pollIntervalMs) {
      return
    }
    const intervalId = window.setInterval(() => {
      void loadAlerts()
    }, pollIntervalMs)
    return () => window.clearInterval(intervalId)
  }, [loadAlerts, pollIntervalMs])

  const severityItems = useMemo(() => alertItems.map((itemValue) => readSeverity(itemValue)), [alertItems])
  const criticalCount = severityItems.filter((itemValue) => itemValue === 'critical').length
  const warningCount = severityItems.filter((itemValue) => itemValue === 'warning').length
  const badgeTone: AlertSeverity =
    criticalCount > 0 ? 'critical' : warningCount > 0 ? 'warning' : 'neutral'

  return (
    <section className="alert-panel" role="region" aria-label="Notifikasi stok">
      <header className="alert-panel-header">
        <div>
          <p className="alert-panel-eyebrow">Alerts</p>
          <h2 className="alert-panel-title">Notifikasi stok</h2>
        </div>
        <div className="alert-panel-actions">
          <AlertBadge count={alertItems.length} tone={badgeTone} />
          <button
            type="button"
            className="ghost-button"
            onClick={() => void loadAlerts()}
            aria-label="Refresh alert stok"
          >
            Refresh
          </button>
        </div>
      </header>

      <div className="alert-panel-body" role="list">
        {isLoading ? (
          <div className="alert-panel-skeleton" aria-label="Memuat alert stok" />
        ) : errorMessage ? (
          <div className="alert-panel-error" role="alert">
            {errorMessage}
          </div>
        ) : alertItems.length === 0 ? (
          <div className="alert-panel-empty">Tidak ada alert aktif.</div>
        ) : (
          alertItems.map((itemValue, indexValue) => {
            const severityValue = readSeverity(itemValue)
            return (
              <article
                key={itemValue.alertId ?? `${itemValue.skuId}-${indexValue}`}
                className={`alert-panel-row ${severityValue}`}
                role="listitem"
              >
                <div className="alert-panel-row-main">
                  <span className="alert-panel-sku">{itemValue.skuId}</span>
                  <span className="alert-panel-detail">
                    Stok {formatNumber(itemValue.currentStock)} | Demand {formatNumber(itemValue.projectedDemand)}
                  </span>
                </div>
                <div className="alert-panel-row-meta">
                  <span className={`alert-panel-tag ${severityValue}`}>
                    {readSeverityLabel(severityValue)}
                  </span>
                  <span className="alert-panel-restock">
                    Restock {formatNumber(itemValue.recommendedRestock)}
                  </span>
                  {itemValue.createdAt ? (
                    <span className="alert-panel-time">{formatDate(itemValue.createdAt)}</span>
                  ) : null}
                </div>
              </article>
            )
          })
        )}
      </div>
    </section>
  )
}

export type { AlertPanelProps }
