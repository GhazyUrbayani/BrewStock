from __future__ import annotations

from datetime import timedelta

from app.models.forecastDataModel import DemandHistoryData, ForecastPointData


def buildBaselineForecast(
    historyData: list[DemandHistoryData],
    horizonDays: int,
) -> list[ForecastPointData]:
    if not historyData:
        raise ValueError("History data missing")

    sortedHistory = sorted(historyData, key=lambda itemValue: itemValue.transactionDate)
    recentHistory = sortedHistory[-7:]
    recentAverage = sum(itemValue.demandQuantity for itemValue in recentHistory) / len(recentHistory)
    trendValue = 0.0

    if len(sortedHistory) > 1:
        firstValue = sortedHistory[0].demandQuantity
        lastValue = sortedHistory[-1].demandQuantity
        trendValue = (lastValue - firstValue) / (len(sortedHistory) - 1)

    lastDate = sortedHistory[-1].transactionDate
    pointItems: list[ForecastPointData] = []
    for dayIndex in range(1, horizonDays + 1):
        forecastQuantity = recentAverage + trendValue * min(dayIndex, 7)
        pointItems.append(
            ForecastPointData(
                transactionDate=lastDate + timedelta(days=dayIndex),
                forecastQuantity=max(0.0, forecastQuantity),
            )
        )

    return pointItems
