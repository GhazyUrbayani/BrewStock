from __future__ import annotations

from datetime import date

import pytest

from app.models.forecastDataModel import DemandHistoryData, ForecastPointData
from app.observers.stockAlertObserver import StockAlertObserver
from app.observers.stockAlertPublisher import StockAlertPublisher
from app.schemas.forecastSchema import DemandPointInput, ForecastRequest
from app.services.forecastService import ForecastService


class FakeTransactionRepository:
    async def fetchHistoryBySku(self, skuId: str) -> list[DemandHistoryData]:
        return [
            DemandHistoryData(transactionDate=date(2026, 5, 1), demandQuantity=10),
            DemandHistoryData(transactionDate=date(2026, 5, 2), demandQuantity=12),
        ]


class FakeStrategy:
    def __init__(self) -> None:
        self.callCount = 0

    async def runForecast(
        self,
        historyData: list[DemandHistoryData],
        horizonDays: int,
    ) -> list[ForecastPointData]:
        self.callCount += 1
        return [
            ForecastPointData(transactionDate=date(2026, 5, 3), forecastQuantity=13.0),
            ForecastPointData(transactionDate=date(2026, 5, 4), forecastQuantity=14.0),
        ]


class FakeCache:
    def __init__(self) -> None:
        self.storeValue: dict[str, str] = {}
        self.ttlValue: dict[str, int] = {}

    async def get(self, keyValue: str) -> str | None:
        return self.storeValue.get(keyValue)

    async def set(self, keyValue: str, payloadValue: str, ex: int) -> None:
        self.storeValue[keyValue] = payloadValue
        self.ttlValue[keyValue] = ex


class CollectingObserver(StockAlertObserver):
    def __init__(self) -> None:
        self.eventItems: list = []

    async def handleStockAlert(self, eventValue) -> None:
        self.eventItems.append(eventValue)


@pytest.mark.asyncio
# Dibantu AI: testGenerateForecastCachesResult
async def testGenerateForecastCachesResult() -> None:
    strategyValue = FakeStrategy()
    cacheValue = FakeCache()
    observerValue = CollectingObserver()

    publisherValue = StockAlertPublisher()
    publisherValue.registerObserver(observerValue)

    serviceValue = ForecastService(
        transactionRepository=FakeTransactionRepository(),
        strategyMap={"prophet": strategyValue},
        cacheValue=cacheValue,
        alertPublisher=publisherValue,
    )

    requestValue = ForecastRequest(
        skuId="beansArabica",
        horizonDays=2,
        modelType="prophet",
        currentStock=10,
        stockThreshold=1,
        historyData=[
            DemandPointInput(transactionDate=date(2026, 5, 1), demandQuantity=10),
            DemandPointInput(transactionDate=date(2026, 5, 2), demandQuantity=12),
        ],
    )

    firstResult = await serviceValue.generateForecast(requestValue)
    secondResult = await serviceValue.generateForecast(requestValue)

    assert firstResult.cacheHit is False
    assert secondResult.cacheHit is True
    assert strategyValue.callCount == 1
    assert len(observerValue.eventItems) == 1


@pytest.mark.asyncio
# Dibantu AI: testGenerateForecastUsesRepository
async def testGenerateForecastUsesRepositoryWhenHistoryEmpty() -> None:
    strategyValue = FakeStrategy()
    cacheValue = FakeCache()
    publisherValue = StockAlertPublisher()

    serviceValue = ForecastService(
        transactionRepository=FakeTransactionRepository(),
        strategyMap={"prophet": strategyValue},
        cacheValue=cacheValue,
        alertPublisher=publisherValue,
    )

    requestValue = ForecastRequest(
        skuId="milkFresh",
        horizonDays=2,
        modelType="prophet",
        historyData=[],
        currentStock=40,
        stockThreshold=100,
    )

    resultValue = await serviceValue.generateForecast(requestValue)

    assert resultValue.projectedDemandTotal == 27.0
    assert resultValue.recommendedRestock == 0.0
    assert strategyValue.callCount == 1
