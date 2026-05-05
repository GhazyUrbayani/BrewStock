from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from app.core.settings import loadSettings
from app.models.forecastDataModel import DemandHistoryData, ForecastPointData
from app.models.stockAlertModel import StockAlertEvent
from app.observers.stockAlertPublisher import StockAlertPublisher
from app.repositories.transactionRepository import TransactionRepository
from app.schemas.forecastSchema import (
    ForecastPointOutput,
    ForecastRequest,
    ForecastResponse,
)
from app.strategies.forecastStrategy import ForecastStrategy


class ForecastService:
    def __init__(
        self,
        transactionRepository: TransactionRepository,
        strategyMap: dict[str, ForecastStrategy],
        cacheValue: Any,
        alertPublisher: StockAlertPublisher,
    ) -> None:
        self.transactionRepository = transactionRepository
        self.strategyMap = strategyMap
        self.cacheValue = cacheValue
        self.alertPublisher = alertPublisher
        self.cacheTtlSeconds = loadSettings().forecastCacheTtlSeconds

    # Dibantu AI: generateForecast
    async def generateForecast(self, requestValue: ForecastRequest) -> ForecastResponse:
        cacheKey = self.buildCacheKey(requestValue)
        cachedPayload = await self.cacheValue.get(cacheKey)
        if cachedPayload:
            return self.readCachedResponse(requestValue, cachedPayload)

        strategyValue = self.strategyMap.get(requestValue.modelType)
        if strategyValue is None:
            raise ValueError("Unsupported model type")

        historyData = await self.resolveHistoryData(requestValue)
        forecastPoints = await strategyValue.runForecast(
            historyData=historyData,
            horizonDays=requestValue.horizonDays,
        )

        responseValue = await self.buildResponseValue(requestValue, forecastPoints, cacheHit=False)
        await self.cacheValue.set(
            cacheKey,
            self.serializeResponse(responseValue),
            ex=self.cacheTtlSeconds,
        )
        return responseValue

    # Dibantu AI: resolveHistoryData
    async def resolveHistoryData(self, requestValue: ForecastRequest) -> list[DemandHistoryData]:
        if requestValue.historyData:
            return [
                DemandHistoryData(
                    transactionDate=itemValue.transactionDate,
                    demandQuantity=itemValue.demandQuantity,
                )
                for itemValue in requestValue.historyData
            ]

        repositoryHistory = await self.transactionRepository.fetchHistoryBySku(requestValue.skuId)
        if not repositoryHistory:
            raise ValueError("History data missing")
        return repositoryHistory

    # Dibantu AI: buildResponseValue
    async def buildResponseValue(
        self,
        requestValue: ForecastRequest,
        forecastPoints: list[ForecastPointData],
        cacheHit: bool,
    ) -> ForecastResponse:
        projectedDemandTotal = sum(pointValue.forecastQuantity for pointValue in forecastPoints)
        recommendedRestock = max(0.0, projectedDemandTotal - requestValue.currentStock)

        if recommendedRestock > requestValue.stockThreshold:
            alertValue = StockAlertEvent(
                skuId=requestValue.skuId,
                currentStock=requestValue.currentStock,
                projectedDemand=projectedDemandTotal,
                recommendedRestock=recommendedRestock,
            )
            await self.alertPublisher.notifyObservers(alertValue)

        return ForecastResponse(
            skuId=requestValue.skuId,
            modelType=requestValue.modelType,
            generatedAt=datetime.now(timezone.utc),
            cacheHit=cacheHit,
            points=[
                ForecastPointOutput(
                    transactionDate=pointValue.transactionDate,
                    forecastQuantity=round(pointValue.forecastQuantity, 2),
                )
                for pointValue in forecastPoints
            ],
            projectedDemandTotal=round(projectedDemandTotal, 2),
            recommendedRestock=round(recommendedRestock, 2),
        )

    # Dibantu AI: buildCacheKey
    def buildCacheKey(self, requestValue: ForecastRequest) -> str:
        historyString = "|".join(
            f"{itemValue.transactionDate.isoformat()}:{itemValue.demandQuantity}"
            for itemValue in requestValue.historyData
        )
        digestValue = hashlib.sha256(historyString.encode("utf-8")).hexdigest()
        return (
            f"forecast:{requestValue.skuId}:{requestValue.modelType}:"
            f"{requestValue.horizonDays}:{digestValue}"
        )

    # Dibantu AI: serializeResponse
    def serializeResponse(self, responseValue: ForecastResponse) -> str:
        payloadValue = {
            "skuId": responseValue.skuId,
            "modelType": responseValue.modelType,
            "generatedAt": responseValue.generatedAt.isoformat(),
            "cacheHit": responseValue.cacheHit,
            "projectedDemandTotal": responseValue.projectedDemandTotal,
            "recommendedRestock": responseValue.recommendedRestock,
            "points": [
                {
                    "transactionDate": pointValue.transactionDate.isoformat(),
                    "forecastQuantity": pointValue.forecastQuantity,
                }
                for pointValue in responseValue.points
            ],
        }
        return json.dumps(payloadValue)

    # Dibantu AI: readCachedResponse
    def readCachedResponse(self, requestValue: ForecastRequest, cachedPayload: str) -> ForecastResponse:
        payloadValue = json.loads(cachedPayload)
        return ForecastResponse(
            skuId=requestValue.skuId,
            modelType=requestValue.modelType,
            generatedAt=datetime.fromisoformat(payloadValue["generatedAt"]),
            cacheHit=True,
            projectedDemandTotal=float(payloadValue["projectedDemandTotal"]),
            recommendedRestock=float(payloadValue["recommendedRestock"]),
            points=[
                ForecastPointOutput(
                    transactionDate=datetime.fromisoformat(pointValue["transactionDate"]).date(),
                    forecastQuantity=float(pointValue["forecastQuantity"]),
                )
                for pointValue in payloadValue["points"]
            ],
        )
