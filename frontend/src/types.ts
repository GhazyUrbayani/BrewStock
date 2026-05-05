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
