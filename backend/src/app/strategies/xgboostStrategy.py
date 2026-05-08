from __future__ import annotations

import asyncio
from datetime import timedelta

from app.models.forecastDataModel import DemandHistoryData, ForecastPointData
from app.strategies.baselineStrategy import buildBaselineForecast
from app.strategies.forecastStrategy import ForecastStrategy

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None


class XgboostStrategy(ForecastStrategy):
    # dibantu AI: runForecast
    async def runForecast(
        self,
        historyData: list[DemandHistoryData],
        horizonDays: int,
    ) -> list[ForecastPointData]:
        if XGBRegressor is None or len(historyData) < 2:
            return buildBaselineForecast(historyData, horizonDays)

        sortedHistory = sorted(historyData, key=lambda itemValue: itemValue.transactionDate)
        return await asyncio.to_thread(self.predictValues, sortedHistory, horizonDays)

    # dibantu AI: predictValues
    def predictValues(
        self,
        historyData: list[DemandHistoryData],
        horizonDays: int,
    ) -> list[ForecastPointData]:
        trainX = [[indexValue] for indexValue in range(len(historyData))]
        trainY = [itemValue.demandQuantity for itemValue in historyData]

        modelValue = XGBRegressor(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            objective="reg:squarederror",
        )
        modelValue.fit(trainX, trainY)

        startIndex = len(historyData)
        futureX = [[startIndex + indexValue] for indexValue in range(horizonDays)]
        predictionValues = modelValue.predict(futureX)
        lastDate = historyData[-1].transactionDate

        pointItems: list[ForecastPointData] = []
        for indexValue, predictionValue in enumerate(predictionValues, start=1):
            pointItems.append(
                ForecastPointData(
                    transactionDate=lastDate + timedelta(days=indexValue),
                    forecastQuantity=max(0.0, float(predictionValue)),
                )
            )

        return pointItems
