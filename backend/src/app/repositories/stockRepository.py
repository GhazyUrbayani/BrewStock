from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stockItemModel import StockItem


class StockRepository:
    def __init__(self, sessionValue: AsyncSession) -> None:
        self.sessionValue = sessionValue

    # Dibantu AI: upsertStock
    async def upsertStock(self, skuId: str, currentStock: float) -> StockItem:
        stockValue = await self.sessionValue.get(StockItem, skuId)
        if stockValue is None:
            stockValue = StockItem(skuId=skuId, currentStock=currentStock)
            self.sessionValue.add(stockValue)
            await self.sessionValue.flush()
            await self.sessionValue.refresh(stockValue)
            return stockValue

        stockValue.currentStock = currentStock
        await self.sessionValue.flush()
        await self.sessionValue.refresh(stockValue)
        return stockValue
