import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { ApiError, apiRequest } from './api'
import AlertPanel from './components/AlertPanel'
import './App.css'
import type {
  AuthMode,
  ForecastModelType,
  ForecastResponse,
  InventorySummary,
  TokenResponse,
  TransactionRecord,
} from './types'

type NoticeTone = 'success' | 'danger' | 'neutral'

type NoticeState = {
  tone: NoticeTone
  message: string
}

type TransactionFormState = {
  skuId: string
  transactionDate: string
  demandQuantity: string
}

type ForecastFormState = {
  skuId: string
  horizonDays: string
  modelType: ForecastModelType
  currentStock: string
  stockThreshold: string
}

const tokenStorageKey = 'brewstock.tokens'

function getTodayIso() {
  return new Date().toISOString().slice(0, 10)
}

function getDateOffsetIso(dayOffset: number) {
  const dateValue = new Date()
  dateValue.setDate(dateValue.getDate() + dayOffset)
  return dateValue.toISOString().slice(0, 10)
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('id-ID', {
    maximumFractionDigits: 1,
  }).format(value)
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('id-ID', {
    day: '2-digit',
    month: 'short',
  }).format(new Date(value))
}

function readStoredTokens() {
  const storedValue = localStorage.getItem(tokenStorageKey)
  if (!storedValue) {
    return null
  }

  try {
    return JSON.parse(storedValue) as TokenResponse
  } catch {
    localStorage.removeItem(tokenStorageKey)
    return null
  }
}

function readErrorMessage(errorValue: unknown) {
  if (errorValue instanceof Error) {
    return errorValue.message
  }
  return 'Terjadi kesalahan tidak terduga'
}

function mapAuthErrorMessage(authMode: AuthMode, messageValue: string) {
  if (authMode === 'login' && messageValue === 'Invalid credentials') {
    return 'Akun belum terdaftar atau password belum cocok. Untuk penggunaan pertama, pilih Register dulu.'
  }

  if (authMode === 'register' && messageValue === 'Email already exists') {
    return 'Akun ini sudah ada. Silakan masuk lewat tab Login.'
  }

  return messageValue
}

function buildDemoTransactions() {
  return [
    { skuId: 'arabica-beans', transactionDate: getDateOffsetIso(-6), demandQuantity: 12 },
    { skuId: 'arabica-beans', transactionDate: getDateOffsetIso(-5), demandQuantity: 15 },
    { skuId: 'arabica-beans', transactionDate: getDateOffsetIso(-4), demandQuantity: 11 },
    { skuId: 'arabica-beans', transactionDate: getDateOffsetIso(-3), demandQuantity: 18 },
    { skuId: 'arabica-beans', transactionDate: getDateOffsetIso(-2), demandQuantity: 16 },
    { skuId: 'fresh-milk', transactionDate: getDateOffsetIso(-5), demandQuantity: 22 },
    { skuId: 'fresh-milk', transactionDate: getDateOffsetIso(-3), demandQuantity: 25 },
    { skuId: 'fresh-milk', transactionDate: getDateOffsetIso(-1), demandQuantity: 24 },
  ]
}

function App() {
  const [tokens, setTokens] = useState<TokenResponse | null>(() => readStoredTokens())
  const [authMode, setAuthMode] = useState<AuthMode>('register')
  const [email, setEmail] = useState('owner@brewstock.id')
  const [password, setPassword] = useState('securePass123')
  const [healthState, setHealthState] = useState<'checking' | 'online' | 'offline'>('checking')
  const [notice, setNotice] = useState<NoticeState | null>(null)
  const [summaryItems, setSummaryItems] = useState<InventorySummary[]>([])
  const [transactionItems, setTransactionItems] = useState<TransactionRecord[]>([])
  const [selectedSku, setSelectedSku] = useState('all')
  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null)
  const [isAuthLoading, setIsAuthLoading] = useState(false)
  const [isDataLoading, setIsDataLoading] = useState(false)
  const [isForecasting, setIsForecasting] = useState(false)
  const [transactionForm, setTransactionForm] = useState<TransactionFormState>({
    skuId: 'arabica-beans',
    transactionDate: getTodayIso(),
    demandQuantity: '14',
  })
  const [forecastForm, setForecastForm] = useState<ForecastFormState>({
    skuId: 'arabica-beans',
    horizonDays: '14',
    modelType: 'xgboost',
    currentStock: '45',
    stockThreshold: '5',
  })

  const persistTokens = useCallback((nextTokens: TokenResponse | null) => {
    setTokens(nextTokens)
    if (nextTokens) {
      localStorage.setItem(tokenStorageKey, JSON.stringify(nextTokens))
    } else {
      localStorage.removeItem(tokenStorageKey)
    }
  }, [])

  const refreshAccessToken = useCallback(async () => {
    if (!tokens?.refreshToken) {
      throw new Error('Sesi belum aktif')
    }

    const nextTokens = await apiRequest<TokenResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      body: { refreshToken: tokens.refreshToken },
    })
    persistTokens(nextTokens)
    return nextTokens.accessToken
  }, [persistTokens, tokens])

  const authRequest = useCallback(
    async <TResponse,>(pathValue: string, optionsValue: { method?: string; body?: unknown } = {}) => {
      if (!tokens?.accessToken) {
        throw new Error('Sesi belum aktif')
      }

      try {
        return await apiRequest<TResponse>(pathValue, {
          ...optionsValue,
          accessToken: tokens.accessToken,
        })
      } catch (errorValue) {
        if (errorValue instanceof ApiError && errorValue.status === 401) {
          const nextAccessToken = await refreshAccessToken()
          return await apiRequest<TResponse>(pathValue, {
            ...optionsValue,
            accessToken: nextAccessToken,
          })
        }
        throw errorValue
      }
    },
    [refreshAccessToken, tokens],
  )

  const checkHealth = useCallback(async () => {
    setHealthState('checking')
    try {
      await apiRequest<{ status: string }>('/health')
      setHealthState('online')
    } catch {
      setHealthState('offline')
    }
  }, [])

  const loadDashboard = useCallback(async () => {
    if (!tokens) {
      return
    }

    setIsDataLoading(true)
    try {
      const [nextSummaryItems, nextTransactionItems] = await Promise.all([
        authRequest<InventorySummary[]>('/api/v1/inventory/summary'),
        authRequest<TransactionRecord[]>('/api/v1/inventory/transactions?limit=100'),
      ])
      setSummaryItems(nextSummaryItems)
      setTransactionItems(nextTransactionItems)
      setNotice({ tone: 'success', message: 'Data backend berhasil dimuat' })
      setForecastForm((previousValue) => {
        if (
          nextSummaryItems.length === 0 ||
          nextSummaryItems.some((itemValue) => itemValue.skuId === previousValue.skuId)
        ) {
          return previousValue
        }
        return { ...previousValue, skuId: nextSummaryItems[0].skuId }
      })
    } catch (errorValue) {
      setNotice({ tone: 'danger', message: readErrorMessage(errorValue) })
    } finally {
      setIsDataLoading(false)
    }
  }, [authRequest, tokens])

  useEffect(() => {
    void checkHealth()
  }, [checkHealth])

  useEffect(() => {
    if (tokens) {
      void loadDashboard()
    }
  }, [loadDashboard, tokens])

  const filteredTransactions = useMemo(() => {
    if (selectedSku === 'all') {
      return transactionItems
    }
    return transactionItems.filter((itemValue) => itemValue.skuId === selectedSku)
  }, [selectedSku, transactionItems])

  const dashboardTotals = useMemo(() => {
    const totalDemand = summaryItems.reduce(
      (sumValue, itemValue) => sumValue + itemValue.totalDemand,
      0,
    )
    const totalTransactions = summaryItems.reduce(
      (sumValue, itemValue) => sumValue + itemValue.transactionCount,
      0,
    )
    return {
      skuCount: summaryItems.length,
      totalDemand,
      totalTransactions,
      averagePerSku: summaryItems.length === 0 ? 0 : totalDemand / summaryItems.length,
    }
  }, [summaryItems])

  async function handleAuthSubmit(eventValue: FormEvent<HTMLFormElement>) {
    eventValue.preventDefault()
    setIsAuthLoading(true)
    setNotice(null)
    try {
      const nextTokens = await apiRequest<TokenResponse>(`/api/v1/auth/${authMode}`, {
        method: 'POST',
        body: { email, password },
      })
      persistTokens(nextTokens)
      setNotice({
        tone: 'success',
        message: authMode === 'login' ? 'Login berhasil' : 'Akun dibuat dan sesi aktif',
      })
    } catch (errorValue) {
      const messageValue = mapAuthErrorMessage(authMode, readErrorMessage(errorValue))
      if (authMode === 'register' && messageValue === 'Akun ini sudah ada. Silakan masuk lewat tab Login.') {
        setAuthMode('login')
      }
      setNotice({ tone: 'danger', message: messageValue })
    } finally {
      setIsAuthLoading(false)
    }
  }

  async function handleTransactionSubmit(eventValue: FormEvent<HTMLFormElement>) {
    eventValue.preventDefault()
    setNotice(null)
    try {
      await authRequest<TransactionRecord>('/api/v1/inventory/transactions', {
        method: 'POST',
        body: {
          skuId: transactionForm.skuId,
          transactionDate: transactionForm.transactionDate,
          demandQuantity: Number(transactionForm.demandQuantity),
        },
      })
      setForecastForm((previousValue) => ({
        ...previousValue,
        skuId: transactionForm.skuId,
      }))
      setTransactionForm((previousValue) => ({
        ...previousValue,
        transactionDate: getTodayIso(),
        demandQuantity: '',
      }))
      await loadDashboard()
      setNotice({ tone: 'success', message: 'Transaksi demand tersimpan' })
    } catch (errorValue) {
      setNotice({ tone: 'danger', message: readErrorMessage(errorValue) })
    }
  }

  async function handleSeedDemoData() {
    setNotice(null)
    try {
      await Promise.all(
        buildDemoTransactions().map((itemValue) =>
          authRequest<TransactionRecord>('/api/v1/inventory/transactions', {
            method: 'POST',
            body: itemValue,
          }),
        ),
      )
      await loadDashboard()
      setNotice({ tone: 'success', message: 'Sample demand coffee shop sudah masuk' })
    } catch (errorValue) {
      setNotice({ tone: 'danger', message: readErrorMessage(errorValue) })
    }
  }

  async function handleDeleteTransaction(transactionId: number) {
    setNotice(null)
    try {
      await authRequest<{ status: string }>(`/api/v1/inventory/transactions/${transactionId}`, {
        method: 'DELETE',
      })
      await loadDashboard()
      setNotice({ tone: 'success', message: 'Transaksi dihapus' })
    } catch (errorValue) {
      setNotice({ tone: 'danger', message: readErrorMessage(errorValue) })
    }
  }

  async function handleForecastSubmit(eventValue: FormEvent<HTMLFormElement>) {
    eventValue.preventDefault()
    setIsForecasting(true)
    setNotice(null)
    try {
      const nextForecastResult = await authRequest<ForecastResponse>('/api/v1/forecast/demand', {
        method: 'POST',
        body: {
          skuId: forecastForm.skuId,
          horizonDays: Number(forecastForm.horizonDays),
          modelType: forecastForm.modelType,
          historyData: [],
          currentStock: Number(forecastForm.currentStock),
          stockThreshold: Number(forecastForm.stockThreshold),
        },
      })
      setForecastResult(nextForecastResult)
      setNotice({ tone: 'success', message: 'Forecast demand berhasil dibuat' })
    } catch (errorValue) {
      setNotice({ tone: 'danger', message: readErrorMessage(errorValue) })
    } finally {
      setIsForecasting(false)
    }
  }

  function handleLogout() {
    persistTokens(null)
    setSummaryItems([])
    setTransactionItems([])
    setForecastResult(null)
    setNotice({ tone: 'neutral', message: 'Sesi ditutup' })
  }

  if (!tokens) {
    return (
      <main className="auth-screen">
        <section className="auth-panel" aria-labelledby="auth-title">
          <div className="brand-stack">
            <span className="brand-mark">BS</span>
            <div>
              <p className="eyebrow">BrewStock</p>
              <h1 id="auth-title">AI inventory assistant</h1>
            </div>
          </div>
          <p className="auth-copy">
            Hubungkan akun untuk mencatat demand, melihat ringkasan stok, dan menjalankan forecast dari backend FastAPI.
          </p>
          <p className="auth-hint">
            Pemakaian pertama dimulai dari <strong>Register</strong>, lalu sesi akan masuk otomatis.
          </p>

          <div className="mode-switch" role="tablist" aria-label="Mode autentikasi">
            <button
              type="button"
              className={authMode === 'login' ? 'active' : ''}
              onClick={() => setAuthMode('login')}
            >
              Login
            </button>
            <button
              type="button"
              className={authMode === 'register' ? 'active' : ''}
              onClick={() => setAuthMode('register')}
            >
              Register
            </button>
          </div>

          <form className="form-grid" onSubmit={handleAuthSubmit}>
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(eventValue) => setEmail(eventValue.target.value)}
                autoComplete="email"
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(eventValue) => setPassword(eventValue.target.value)}
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                minLength={8}
                required
              />
            </label>
            <button type="submit" className="primary-button" disabled={isAuthLoading}>
              {isAuthLoading ? 'Memproses...' : authMode === 'login' ? 'Masuk' : 'Buat akun'}
            </button>
          </form>

          <StatusStrip healthState={healthState} notice={notice} onRetry={checkHealth} />
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-stack compact">
          <span className="brand-mark">BS</span>
          <div>
            <p className="eyebrow">BrewStock</p>
            <h1>Inventory command center</h1>
          </div>
        </div>
        <div className="topbar-actions">
          <span className={`health-pill ${healthState}`}>{healthState}</span>
          <span className="user-pill">{email}</span>
          <button type="button" className="ghost-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <section className="metric-grid" aria-label="Ringkasan inventory">
        <MetricCard label="SKU aktif" value={formatNumber(dashboardTotals.skuCount)} />
        <MetricCard label="Total demand" value={formatNumber(dashboardTotals.totalDemand)} />
        <MetricCard label="Transaksi" value={formatNumber(dashboardTotals.totalTransactions)} />
        <MetricCard label="Rata-rata per SKU" value={formatNumber(dashboardTotals.averagePerSku)} />
      </section>

      <StatusStrip healthState={healthState} notice={notice} onRetry={checkHealth} />

      <AlertPanel authRequest={authRequest} />

      <section className="workspace-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Demand history</p>
              <h2>Catat transaksi</h2>
            </div>
            <button
              type="button"
              className="ghost-button"
              onClick={() => void handleSeedDemoData()}
            >
              Isi sample
            </button>
          </div>

          <form className="form-grid horizontal" onSubmit={handleTransactionSubmit}>
            <label>
              SKU
              <input
                value={transactionForm.skuId}
                onChange={(eventValue) =>
                  setTransactionForm((previousValue) => ({
                    ...previousValue,
                    skuId: eventValue.target.value,
                  }))
                }
                maxLength={64}
                required
              />
            </label>
            <label>
              Tanggal
              <input
                type="date"
                value={transactionForm.transactionDate}
                onChange={(eventValue) =>
                  setTransactionForm((previousValue) => ({
                    ...previousValue,
                    transactionDate: eventValue.target.value,
                  }))
                }
                required
              />
            </label>
            <label>
              Demand
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={transactionForm.demandQuantity}
                onChange={(eventValue) =>
                  setTransactionForm((previousValue) => ({
                    ...previousValue,
                    demandQuantity: eventValue.target.value,
                  }))
                }
                required
              />
            </label>
            <button type="submit" className="primary-button">
              Simpan
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Forecast</p>
              <h2>Prediksi restock</h2>
            </div>
            <button
              type="button"
              className="ghost-button"
              onClick={() => void loadDashboard()}
              disabled={isDataLoading}
            >
              Refresh
            </button>
          </div>

          <form className="form-grid forecast-form" onSubmit={handleForecastSubmit}>
            <label>
              SKU
              <select
                value={forecastForm.skuId}
                onChange={(eventValue) =>
                  setForecastForm((previousValue) => ({
                    ...previousValue,
                    skuId: eventValue.target.value,
                  }))
                }
              >
                {summaryItems.length === 0 ? (
                  <option value={forecastForm.skuId}>{forecastForm.skuId}</option>
                ) : (
                  summaryItems.map((itemValue) => (
                    <option key={itemValue.skuId} value={itemValue.skuId}>
                      {itemValue.skuId}
                    </option>
                  ))
                )}
              </select>
            </label>
            <label>
              Model
              <select
                value={forecastForm.modelType}
                onChange={(eventValue) =>
                  setForecastForm((previousValue) => ({
                    ...previousValue,
                    modelType: eventValue.target.value as ForecastModelType,
                  }))
                }
              >
                <option value="xgboost">XGBoost</option>
                <option value="prophet">Prophet</option>
              </select>
            </label>
            <label>
              Horizon
              <input
                type="number"
                min="1"
                max="90"
                value={forecastForm.horizonDays}
                onChange={(eventValue) =>
                  setForecastForm((previousValue) => ({
                    ...previousValue,
                    horizonDays: eventValue.target.value,
                  }))
                }
                required
              />
            </label>
            <label>
              Stok saat ini
              <input
                type="number"
                min="0"
                step="0.1"
                value={forecastForm.currentStock}
                onChange={(eventValue) =>
                  setForecastForm((previousValue) => ({
                    ...previousValue,
                    currentStock: eventValue.target.value,
                  }))
                }
                required
              />
            </label>
            <label>
              Threshold
              <input
                type="number"
                min="0"
                step="0.1"
                value={forecastForm.stockThreshold}
                onChange={(eventValue) =>
                  setForecastForm((previousValue) => ({
                    ...previousValue,
                    stockThreshold: eventValue.target.value,
                  }))
                }
                required
              />
            </label>
            <button type="submit" className="primary-button" disabled={isForecasting}>
              {isForecasting ? 'Menghitung...' : 'Jalankan'}
            </button>
          </form>
        </div>
      </section>

      <section className="analytics-grid">
        <div className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Demand outlook</p>
              <h2>Kurva forecast</h2>
            </div>
            {forecastResult ? (
              <span className="cache-pill">{forecastResult.cacheHit ? 'cache hit' : 'fresh run'}</span>
            ) : null}
          </div>
          <ForecastChart forecastValue={forecastResult} />
        </div>

        <div className="panel restock-panel">
          <p className="eyebrow">Restock signal</p>
          <h2>{forecastResult ? forecastResult.skuId : 'Belum ada forecast'}</h2>
          <dl className="restock-list">
            <div>
              <dt>Projected demand</dt>
              <dd>{forecastResult ? formatNumber(forecastResult.projectedDemandTotal) : '-'}</dd>
            </div>
            <div>
              <dt>Recommended restock</dt>
              <dd>{forecastResult ? formatNumber(forecastResult.recommendedRestock) : '-'}</dd>
            </div>
            <div>
              <dt>Generated</dt>
              <dd>{forecastResult ? formatDate(forecastResult.generatedAt) : '-'}</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="data-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SKU summary</p>
              <h2>Ringkasan demand</h2>
            </div>
          </div>
          <div className="summary-list">
            {summaryItems.length === 0 ? (
              <p className="empty-state">Belum ada histori demand.</p>
            ) : (
              summaryItems.map((itemValue) => (
                <button
                  type="button"
                  className="summary-row"
                  key={itemValue.skuId}
                  onClick={() => {
                    setSelectedSku(itemValue.skuId)
                    setForecastForm((previousValue) => ({
                      ...previousValue,
                      skuId: itemValue.skuId,
                    }))
                  }}
                >
                  <span>
                    <strong>{itemValue.skuId}</strong>
                    <small>{formatDate(itemValue.lastTransactionDate)}</small>
                  </span>
                  <span>{formatNumber(itemValue.averageDemand)} avg</span>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Transactions</p>
              <h2>Histori demand</h2>
            </div>
            <select value={selectedSku} onChange={(eventValue) => setSelectedSku(eventValue.target.value)}>
              <option value="all">Semua SKU</option>
              {summaryItems.map((itemValue) => (
                <option key={itemValue.skuId} value={itemValue.skuId}>
                  {itemValue.skuId}
                </option>
              ))}
            </select>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Tanggal</th>
                  <th>Demand</th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {filteredTransactions.map((itemValue) => (
                  <tr key={itemValue.id}>
                    <td>{itemValue.skuId}</td>
                    <td>{formatDate(itemValue.transactionDate)}</td>
                    <td>{formatNumber(itemValue.demandQuantity)}</td>
                    <td>
                      <button
                        type="button"
                        className="text-button danger"
                        onClick={() => void handleDeleteTransaction(itemValue.id)}
                      >
                        Hapus
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredTransactions.length === 0 ? (
              <p className="empty-state">Tidak ada transaksi pada filter ini.</p>
            ) : null}
          </div>
        </div>
      </section>
    </main>
  )
}

function StatusStrip({
  healthState,
  notice,
  onRetry,
}: {
  healthState: 'checking' | 'online' | 'offline'
  notice: NoticeState | null
  onRetry: () => void
}) {
  return (
    <div className="status-strip" role="status">
      <span className={`health-dot ${healthState}`} />
      <span>Backend {healthState}</span>
      {notice ? <span className={`notice ${notice.tone}`}>{notice.message}</span> : null}
      {healthState === 'offline' ? (
        <button type="button" className="text-button" onClick={onRetry}>
          Cek ulang
        </button>
      ) : null}
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  )
}

function ForecastChart({ forecastValue }: { forecastValue: ForecastResponse | null }) {
  if (!forecastValue || forecastValue.points.length === 0) {
    return (
      <div className="empty-chart">
        <span>Forecast akan muncul setelah SKU memiliki histori demand.</span>
      </div>
    )
  }

  const widthValue = 720
  const heightValue = 260
  const paddingValue = 28
  const maxQuantity = Math.max(
    ...forecastValue.points.map((itemValue) => itemValue.forecastQuantity),
    1,
  )
  const coordinateItems = forecastValue.points.map((itemValue, indexValue) => {
    const xValue =
      forecastValue.points.length === 1
        ? widthValue / 2
        : paddingValue +
          (indexValue / (forecastValue.points.length - 1)) *
            (widthValue - paddingValue * 2)
    const yValue =
      heightValue -
      paddingValue -
      (itemValue.forecastQuantity / maxQuantity) * (heightValue - paddingValue * 2)
    return `${xValue},${yValue}`
  })
  const linePath = coordinateItems.join(' ')
  const areaPath = `${paddingValue},${heightValue - paddingValue} ${linePath} ${
    widthValue - paddingValue
  },${heightValue - paddingValue}`

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${widthValue} ${heightValue}`} role="img" aria-label="Forecast demand chart">
        <polyline className="chart-grid" points={`${paddingValue},42 ${widthValue - paddingValue},42`} />
        <polyline className="chart-grid" points={`${paddingValue},130 ${widthValue - paddingValue},130`} />
        <polyline className="chart-grid" points={`${paddingValue},218 ${widthValue - paddingValue},218`} />
        <polygon className="chart-area" points={areaPath} />
        <polyline className="chart-line" points={linePath} />
        {forecastValue.points.map((itemValue, indexValue) => {
          const [xValue, yValue] = coordinateItems[indexValue].split(',')
          return (
            <circle
              key={`${itemValue.transactionDate}-${itemValue.forecastQuantity}`}
              className="chart-point"
              cx={xValue}
              cy={yValue}
              r="4"
            />
          )
        })}
      </svg>
      <div className="chart-axis">
        <span>{formatDate(forecastValue.points[0].transactionDate)}</span>
        <span>{formatDate(forecastValue.points[forecastValue.points.length - 1].transactionDate)}</span>
      </div>
    </div>
  )
}

export default App
