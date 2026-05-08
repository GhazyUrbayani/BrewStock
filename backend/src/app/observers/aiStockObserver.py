from __future__ import annotations

import logging

from app.models.stockAlertModel import StockAlertEvent
from app.observers.stockAlertObserver import StockAlertObserver
from app.services.ai.aiService import AiService

loggerValue = logging.getLogger("brewStock")


class AiStockObserver(StockAlertObserver):
    def __init__(self, aiService: AiService) -> None:
        self.aiService = aiService

    # dibantu AI: handleStockAlert
    async def handleStockAlert(self, eventValue: StockAlertEvent) -> None:
        promptValue = (
            "Buat insight restock singkat untuk coffee shop. "
            f"SKU {eventValue.skuId}, stock saat ini {eventValue.currentStock:.2f}, "
            f"prediksi demand {eventValue.projectedDemand:.2f}, "
            f"restock disarankan {eventValue.recommendedRestock:.2f}."
        )

        try:
            insightValue = await self.aiService.generateInsight(promptValue)
            loggerValue.info("AI insight sku=%s detail=%s", eventValue.skuId, insightValue)
        except Exception as errorValue:
            loggerValue.error("AI insight failed %s", str(errorValue))
