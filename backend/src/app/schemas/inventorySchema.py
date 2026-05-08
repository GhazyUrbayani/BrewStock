from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from app.schemas.baseSchema import SanitizedModel


class TransactionCreateRequest(SanitizedModel):
    skuId: str = Field(min_length=1, max_length=64)
    transactionDate: date
    demandQuantity: float = Field(gt=0)


class TransactionResponse(SanitizedModel):
    id: int
    skuId: str
    transactionDate: date
    demandQuantity: float
    createdAt: datetime


class InventorySummaryResponse(SanitizedModel):
    skuId: str
    transactionCount: int
    totalDemand: float
    averageDemand: float
    lastTransactionDate: date


class StockUpdateRequest(SanitizedModel):
    currentStock: float = Field(ge=0)


class StockUpdateResponse(SanitizedModel):
    skuId: str
    currentStock: float
    updatedAt: datetime
