from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecastDataModel import DemandHistoryData
from app.models.transactionModel import TransactionRecord


class TransactionRepository:
    def __init__(self, sessionValue: AsyncSession) -> None:
        self.sessionValue = sessionValue

    async def createTransaction(
        self,
        skuId: str,
        transactionDate: date,
        demandQuantity: float,
    ) -> TransactionRecord:
        transactionValue = TransactionRecord(
            skuId=skuId,
            transactionDate=transactionDate,
            demandQuantity=demandQuantity,
        )
        self.sessionValue.add(transactionValue)
        await self.sessionValue.flush()
        await self.sessionValue.refresh(transactionValue)
        return transactionValue

    async def listTransactions(
        self,
        skuId: str | None = None,
        limit: int = 100,
    ) -> list[TransactionRecord]:
        queryValue = select(TransactionRecord)
        if skuId:
            queryValue = queryValue.where(TransactionRecord.skuId == skuId)

        queryValue = queryValue.order_by(
            TransactionRecord.transactionDate.desc(),
            TransactionRecord.id.desc(),
        ).limit(limit)
        resultValue = await self.sessionValue.execute(queryValue)
        return list(resultValue.scalars().all())

    async def deleteTransaction(self, transactionId: int) -> bool:
        transactionValue = await self.sessionValue.get(TransactionRecord, transactionId)
        if transactionValue is None:
            return False

        await self.sessionValue.delete(transactionValue)
        return True

    async def summarizeBySku(self) -> list[dict[str, object]]:
        queryValue = (
            select(
                TransactionRecord.skuId.label("skuId"),
                func.count(TransactionRecord.id).label("transactionCount"),
                func.sum(TransactionRecord.demandQuantity).label("totalDemand"),
                func.avg(TransactionRecord.demandQuantity).label("averageDemand"),
                func.max(TransactionRecord.transactionDate).label("lastTransactionDate"),
            )
            .group_by(TransactionRecord.skuId)
            .order_by(func.max(TransactionRecord.transactionDate).desc())
        )
        resultValue = await self.sessionValue.execute(queryValue)
        return [dict(rowValue._mapping) for rowValue in resultValue.all()]

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
