from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from app.schemas.baseSchema import SanitizedModel


class DemandPointInput(SanitizedModel):
    transactionDate: date
    demandQuantity: float = Field(gt=0)


class ForecastRequest(SanitizedModel):
    skuId: str = Field(min_length=1, max_length=64)
    horizonDays: int = Field(default=14, ge=1, le=90)
    modelType: str = Field(default="prophet", pattern="^(prophet|xgboost)$")
    historyData: list[DemandPointInput] = Field(default_factory=list)
    currentStock: float = Field(default=0, ge=0)
    stockThreshold: float = Field(default=0, ge=0)


class ForecastPointOutput(SanitizedModel):
    transactionDate: date
    forecastQuantity: float


class ForecastResponse(SanitizedModel):
    skuId: str
    modelType: str
    generatedAt: datetime
    cacheHit: bool
    points: list[ForecastPointOutput]
    projectedDemandTotal: float
    recommendedRestock: float
