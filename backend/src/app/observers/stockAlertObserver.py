from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.stockAlertModel import StockAlertEvent


class StockAlertObserver(ABC):
    @abstractmethod
    async def handleStockAlert(self, eventValue: StockAlertEvent) -> None:
        raise NotImplementedError
