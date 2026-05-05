from __future__ import annotations

import logging

from app.models.stockAlertModel import StockAlertEvent
from app.observers.stockAlertObserver import StockAlertObserver

loggerValue = logging.getLogger("brewStock")


class LogStockObserver(StockAlertObserver):
    # Dibantu AI: handleStockAlert
    async def handleStockAlert(self, eventValue: StockAlertEvent) -> None:
        loggerValue.warning(
            "Stock alert sku=%s current=%.2f demand=%.2f restock=%.2f",
            eventValue.skuId,
            eventValue.currentStock,
            eventValue.projectedDemand,
            eventValue.recommendedRestock,
        )
