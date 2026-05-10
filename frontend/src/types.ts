export type AuthMode = 'login' | 'register'

export type TokenResponse = {
  accessToken: string
  refreshToken: string
  tokenType: string
}

export type TransactionRecord = {
  id: number
  skuId: string
  transactionDate: string
  demandQuantity: number
  createdAt: string
}

export type InventorySummary = {
  skuId: string
  transactionCount: number
  totalDemand: number
  averageDemand: number
  lastTransactionDate: string
}

export type ForecastPoint = {
  transactionDate: string
  forecastQuantity: number
}

export type ForecastResponse = {
  skuId: string
  modelType: 'prophet' | 'xgboost'
  generatedAt: string
  cacheHit: boolean
  points: ForecastPoint[]
  projectedDemandTotal: number
  recommendedRestock: number
}

export type ForecastModelType = ForecastResponse['modelType']

export type InventoryAlert = {
  alertId?: string
  skuId: string
  currentStock: number
  projectedDemand: number
  recommendedRestock: number
  createdAt?: string
}

export type ForecastChartPoint = {
  transactionDate: string
  actualValue: number | null
  predictedValue: number | null
  lowerBound: number | null
  upperBound: number | null
}

export type ForecastChartSeries = {
  skuId: string
  horizonDays: number
  unitLabel: string
  points: ForecastChartPoint[]
}

export type ScannerBoundingBox = {
  x1: number
  y1: number
  x2: number
  y2: number
}

export type ScannerDetection = {
  className: string
  confidence: number
  count: number
  boundingBoxes: ScannerBoundingBox[]
}

export type ScannerSuggestedStockUpdate = {
  skuId: string
  detectedCount: number
}

export type ScannerResponse = {
  detections: ScannerDetection[]
  totalItemsDetected: number
  annotatedImageBase64: string
  inferenceTimeMs: number
  suggestedStockUpdate: ScannerSuggestedStockUpdate[]
}

export type StockUpdateResponse = {
  skuId: string
  currentStock: number
  updatedAt: string
}

export type KpiCardType = {
  label: string
  value: string
  trend: string
  trendDirection: 'up' | 'down' | 'neutral'
  targetText: string
  statusBadge: string
  statusCondition: 'good' | 'warning' | 'critical'
}

export type DashboardKpiResponse = {
  kpiCards: KpiCardType[]
}
