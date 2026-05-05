from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecastDataModel import DemandHistoryData
from app.models.transactionModel import TransactionRecord


class TransactionRepository:
    def __init__(self, sessionValue: AsyncSession) -> None:
        self.sessionValue = sessionValue

    # Dibantu AI: fetchHistoryBySku
    async def fetchHistoryBySku(self, skuId: str) -> list[DemandHistoryData]:
        queryValue = (
            select(TransactionRecord)
            .where(TransactionRecord.skuId == skuId)
            .order_by(TransactionRecord.transactionDate.asc())
        )
        resultValue = await self.sessionValue.execute(queryValue)
        recordItems = resultValue.scalars().all()
        return [
            DemandHistoryData(
                transactionDate=recordValue.transactionDate,
                demandQuantity=recordValue.demandQuantity,
            )
            for recordValue in recordItems
        ]
