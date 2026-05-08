from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

import pytest

from app.schemas.inventorySchema import StockUpdateRequest, TransactionCreateRequest
from app.services.inventoryService import InventoryService


class FakeSession:
    def __init__(self) -> None:
        self.commitCount = 0

    async def commit(self) -> None:
        self.commitCount += 1


@dataclass
class FakeTransaction:
    id: int
    skuId: str
    transactionDate: date
    demandQuantity: float
    createdAt: datetime


class FakeTransactionRepository:
    def __init__(self) -> None:
        self.nextId = 1
        self.items: list[FakeTransaction] = []

    async def createTransaction(
        self,
        skuId: str,
        transactionDate: date,
        demandQuantity: float,
    ) -> FakeTransaction:
        itemValue = FakeTransaction(
            id=self.nextId,
            skuId=skuId,
            transactionDate=transactionDate,
            demandQuantity=demandQuantity,
            createdAt=datetime.now(timezone.utc),
        )
        self.nextId += 1
        self.items.append(itemValue)
        return itemValue

    async def listTransactions(self, skuId: str | None = None, limit: int = 100):
        filteredItems = self.items
        if skuId:
            filteredItems = [itemValue for itemValue in self.items if itemValue.skuId == skuId]
        return filteredItems[:limit]

    async def deleteTransaction(self, transactionId: int) -> bool:
        indexValue = next(
            (indexValue for indexValue, itemValue in enumerate(self.items) if itemValue.id == transactionId),
            None,
        )
        if indexValue is None:
            return False
        del self.items[indexValue]
        return True

    async def summarizeBySku(self):
        summaryMap: dict[str, dict[str, object]] = {}
        for itemValue in self.items:
            current = summaryMap.setdefault(
                itemValue.skuId,
                {
                    "skuId": itemValue.skuId,
                    "transactionCount": 0,
                    "totalDemand": 0.0,
                    "averageDemand": 0.0,
                    "lastTransactionDate": itemValue.transactionDate,
                },
            )
            current["transactionCount"] = int(current["transactionCount"]) + 1
            current["totalDemand"] = float(current["totalDemand"]) + itemValue.demandQuantity
            current["lastTransactionDate"] = max(
                current["lastTransactionDate"],
                itemValue.transactionDate,
            )

        resultItems = []
        for itemValue in summaryMap.values():
            countValue = int(itemValue["transactionCount"])
            totalValue = float(itemValue["totalDemand"])
            resultItems.append(
                {
                    **itemValue,
                    "averageDemand": totalValue / countValue if countValue > 0 else 0.0,
                }
            )
        return resultItems


@dataclass
class FakeStockItem:
    skuId: str
    currentStock: float
    updatedAt: datetime


class FakeStockRepository:
    def __init__(self) -> None:
        self.items: dict[str, FakeStockItem] = {}

    async def upsertStock(self, skuId: str, currentStock: float) -> FakeStockItem:
        stockValue = self.items.get(skuId)
        if stockValue is None:
            stockValue = FakeStockItem(
                skuId=skuId,
                currentStock=currentStock,
                updatedAt=datetime.now(timezone.utc),
            )
            self.items[skuId] = stockValue
            return stockValue

        stockValue.currentStock = currentStock
        stockValue.updatedAt = datetime.now(timezone.utc)
        return stockValue


@pytest.mark.asyncio
async def testInventoryServiceCrudAndSummary() -> None:
    sessionValue = FakeSession()
    repositoryValue = FakeTransactionRepository()
    stockRepository = FakeStockRepository()
    serviceValue = InventoryService(repositoryValue, stockRepository, sessionValue)

    await serviceValue.createTransaction(
        TransactionCreateRequest(
            skuId="arabica-beans",
            transactionDate=date(2026, 5, 1),
            demandQuantity=12.0,
        )
    )
    await serviceValue.createTransaction(
        TransactionCreateRequest(
            skuId="arabica-beans",
            transactionDate=date(2026, 5, 2),
            demandQuantity=14.0,
        )
    )
    await serviceValue.createTransaction(
        TransactionCreateRequest(
            skuId="fresh-milk",
            transactionDate=date(2026, 5, 2),
            demandQuantity=22.0,
        )
    )

    summaryItems = await serviceValue.listSummaries()
    assert len(summaryItems) == 2
    assert summaryItems[0].skuId in {"arabica-beans", "fresh-milk"}

    arabicaItems = await serviceValue.listTransactions("arabica-beans", 100)
    assert len(arabicaItems) == 2

    await serviceValue.deleteTransaction(arabicaItems[0].id)
    updatedArabicaItems = await serviceValue.listTransactions("arabica-beans", 100)
    assert len(updatedArabicaItems) == 1
    assert sessionValue.commitCount == 4


@pytest.mark.asyncio
async def testInventoryDeleteNotFoundRaises() -> None:
    sessionValue = FakeSession()
    repositoryValue = FakeTransactionRepository()
    stockRepository = FakeStockRepository()
    serviceValue = InventoryService(repositoryValue, stockRepository, sessionValue)

    with pytest.raises(ValueError):
        await serviceValue.deleteTransaction(999)


@pytest.mark.asyncio
# Dibantu AI: testUpdateCurrentStock
async def testUpdateCurrentStock() -> None:
    sessionValue = FakeSession()
    repositoryValue = FakeTransactionRepository()
    stockRepository = FakeStockRepository()
    serviceValue = InventoryService(repositoryValue, stockRepository, sessionValue)

    resultValue = await serviceValue.updateCurrentStock(
        skuId="arabica-beans",
        requestValue=StockUpdateRequest(currentStock=14),
    )

    assert resultValue.skuId == "arabica-beans"
    assert resultValue.currentStock == 14
    assert sessionValue.commitCount == 1
