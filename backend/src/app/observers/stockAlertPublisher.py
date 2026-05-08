from __future__ import annotations

from app.models.stockAlertModel import StockAlertEvent
from app.observers.stockAlertObserver import StockAlertObserver


class StockAlertPublisher:
    def __init__(self) -> None:
        self.observerItems: list[StockAlertObserver] = []

    # dibantu AI: registerObserver
    def registerObserver(self, observerValue: StockAlertObserver) -> None:
        self.observerItems.append(observerValue)

    # dibantu AI: removeObserver
    def removeObserver(self, observerValue: StockAlertObserver) -> None:
        self.observerItems = [
            itemValue for itemValue in self.observerItems if itemValue is not observerValue
        ]

    # dibantu AI: notifyObservers
    async def notifyObservers(self, eventValue: StockAlertEvent) -> None:
        for observerValue in self.observerItems:
            await observerValue.handleStockAlert(eventValue)
