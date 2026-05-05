from __future__ import annotations

import asyncio

import pandas as pd

from app.models.forecastDataModel import DemandHistoryData, ForecastPointData
from app.strategies.baselineStrategy import buildBaselineForecast
from app.strategies.forecastStrategy import ForecastStrategy

try:
    from prophet import Prophet
except Exception:
    Prophet = None


class ProphetStrategy(ForecastStrategy):
    # Dibantu AI: runForecast
    async def runForecast(
        self,
        historyData: list[DemandHistoryData],
        horizonDays: int,
    ) -> list[ForecastPointData]:
        if Prophet is None or len(historyData) < 2:
            return buildBaselineForecast(historyData, horizonDays)

        sortedHistory = sorted(historyData, key=lambda itemValue: itemValue.transactionDate)
        frameValue = pd.DataFrame(
            {
                "ds": [itemValue.transactionDate for itemValue in sortedHistory],
                "y": [itemValue.demandQuantity for itemValue in sortedHistory],
            }
        )

        resultFrame = await asyncio.to_thread(self.predictFrame, frameValue, horizonDays)
        lastDate = sortedHistory[-1].transactionDate
        pointItems: list[ForecastPointData] = []

        for rowValue in resultFrame.itertuples(index=False):
            resultDate = rowValue.ds.date()
            if resultDate <= lastDate:
                continue

            pointItems.append(
                ForecastPointData(
                    transactionDate=resultDate,
                    forecastQuantity=max(0.0, float(rowValue.yhat)),
                )
            )

        return pointItems[:horizonDays]

    # Dibantu AI: predictFrame
    def predictFrame(self, frameValue: pd.DataFrame, horizonDays: int) -> pd.DataFrame:
        modelValue = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        modelValue.fit(frameValue)
        futureFrame = modelValue.make_future_dataframe(periods=horizonDays, freq="D")
        resultFrame = modelValue.predict(futureFrame)
        return resultFrame[["ds", "yhat"]]
