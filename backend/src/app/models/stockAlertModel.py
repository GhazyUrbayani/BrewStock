from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StockAlertEvent:
    skuId: str
    currentStock: float
    projectedDemand: float
    recommendedRestock: float
