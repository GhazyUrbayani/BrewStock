from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.forecastDataModel import DemandHistoryData, ForecastPointData


class ForecastStrategy(ABC):
    @abstractmethod
    async def runForecast(
        self,
        historyData: list[DemandHistoryData],
        horizonDays: int,
    ) -> list[ForecastPointData]:
        raise NotImplementedError
