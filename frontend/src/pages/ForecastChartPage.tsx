// dibantu AI: ForecastChartPage
import { useMemo, useState } from 'react'
import {
  Area,
  CartesianGrid,
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './ForecastChartPage.css'
import type { ForecastChartSeries } from '../types'

type ForecastChartPageProps = {
  series: ForecastChartSeries[]
  isLoading?: boolean
}

type ChartDatum = {
  transactionDate: string
  actualValue: number | null
  predictedValue: number | null
  lowerBound: number
  confidenceBand: number
}

const bandRatio = 0.12

const numberFormatter = new Intl.NumberFormat('id-ID', {
  maximumFractionDigits: 1,
})

function formatNumber(value: number) {
  return numberFormatter.format(value)
}

const dateFormatter = new Intl.DateTimeFormat('id-ID', {
  day: '2-digit',
  month: 'short',
})

function formatShortDate(value: string) {
  return dateFormatter.format(new Date(value))
}

export default function ForecastChartPage({ series, isLoading = false }: ForecastChartPageProps) {
  const availableSkus = useMemo(() => series.map((itemValue) => itemValue.skuId), [series])
  const [selectedSku, setSelectedSku] = useState(availableSkus[0] ?? '')
  const activeSku = availableSkus.includes(selectedSku) ? selectedSku : availableSkus[0] ?? ''
  const activeSeries = series.find((itemValue) => itemValue.skuId === activeSku)
  const horizonDays = Math.min(7, activeSeries?.points.length ?? 0)
  const chartData = useMemo<ChartDatum[]>(() => {
    if (!activeSeries) {
      return []
    }

    return activeSeries.points.slice(0, horizonDays).map((pointValue) => {
      const predictedValue = pointValue.predictedValue ?? 0
      const lowerBound =
        pointValue.lowerBound ?? predictedValue * (1 - bandRatio)
      const upperBound =
        pointValue.upperBound ?? predictedValue * (1 + bandRatio)
      const confidenceBand = Math.max(upperBound - lowerBound, 0)

      return {
        transactionDate: pointValue.transactionDate,
        actualValue: pointValue.actualValue ?? null,
        predictedValue: pointValue.predictedValue ?? null,
        lowerBound,
        confidenceBand,
      }
    })
  }, [activeSeries, horizonDays])

  if (isLoading) {
    return (
      <section className="forecast-chart-panel">
        <div className="forecast-chart-header">
          <div>
            <p className="forecast-chart-eyebrow">Forecast</p>
            <h2 className="forecast-chart-title">Prediksi 7 hari</h2>
          </div>
        </div>
        <div className="forecast-chart-skeleton" aria-label="Memuat chart forecast" />
      </section>
    )
  }

  if (!activeSeries || chartData.length === 0) {
    return (
      <section className="forecast-chart-panel">
        <div className="forecast-chart-header">
          <div>
            <p className="forecast-chart-eyebrow">Forecast</p>
            <h2 className="forecast-chart-title">Prediksi 7 hari</h2>
          </div>
        </div>
        <div className="forecast-chart-empty">Data forecast belum tersedia.</div>
      </section>
    )
  }

  const unitLabel = activeSeries.unitLabel || 'unit'

  return (
    <section className="forecast-chart-panel">
      <div className="forecast-chart-header">
        <div>
          <p className="forecast-chart-eyebrow">Forecast</p>
          <h2 className="forecast-chart-title">Prediksi 7 hari</h2>
        </div>
        <div className="forecast-chart-toolbar">
          <label className="forecast-chart-label">
            SKU
            <select
              className="forecast-chart-select"
              value={activeSku}
              onChange={(eventValue) => setSelectedSku(eventValue.target.value)}
              aria-label="Pilih SKU forecast"
            >
              {availableSkus.map((skuValue) => (
                <option key={skuValue} value={skuValue}>
                  {skuValue}
                </option>
              ))}
            </select>
          </label>
          <span className="forecast-chart-badge">Horizon 7 hari</span>
        </div>
      </div>

      <div className="forecast-chart-meta">
        <div className="forecast-chart-legend">
          <span className="forecast-chart-dot actual" />
          <span>Aktual ({unitLabel})</span>
        </div>
        <div className="forecast-chart-legend">
          <span className="forecast-chart-dot predicted" />
          <span>Prediksi ({unitLabel})</span>
        </div>
        <div className="forecast-chart-legend">
          <span className="forecast-chart-dot band" />
          <span>Confidence interval</span>
        </div>
      </div>

      <div
        className="forecast-chart-figure"
        role="img"
        aria-label="Chart aktual dan prediksi"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
            <XAxis
              dataKey="transactionDate"
              tickFormatter={formatShortDate}
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <YAxis
              tickFormatter={(value: number) => formatNumber(value)}
              tick={{ fill: '#64748b', fontSize: 12 }}
              width={48}
            />
            <Tooltip
              formatter={(value: number | string, name: string) => {
                if (name === 'confidenceBand' || name === 'lowerBound') {
                  return null
                }
                if (typeof value !== 'number') {
                  return ['-', name]
                }
                return [formatNumber(value), name]
              }}
              labelFormatter={(labelValue) => `Tanggal ${formatShortDate(String(labelValue))}`}
              contentStyle={{ borderRadius: 10, borderColor: '#e2e8f0' }}
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stackId="confidence"
              stroke="none"
              fill="transparent"
              legendType="none"
            />
            <Area
              type="monotone"
              dataKey="confidenceBand"
              name="confidenceBand"
              stackId="confidence"
              stroke="none"
              fill="rgba(249, 115, 22, 0.18)"
              legendType="none"
            />
            <Line
              type="monotone"
              dataKey="actualValue"
              name="Aktual"
              stroke="#0f766e"
              strokeWidth={3}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="predictedValue"
              name="Prediksi"
              stroke="#f97316"
              strokeWidth={3}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
