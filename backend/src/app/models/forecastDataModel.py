from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class DemandHistoryData:
    transactionDate: date
    demandQuantity: float


@dataclass(slots=True)
class ForecastPointData:
    transactionDate: date
    forecastQuantity: float
