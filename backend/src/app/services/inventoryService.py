from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transactionModel import TransactionRecord
from app.repositories.stockRepository import StockRepository
from app.repositories.transactionRepository import TransactionRepository
from app.schemas.inventorySchema import (
    InventorySummaryResponse,
    StockUpdateRequest,
    StockUpdateResponse,
    TransactionCreateRequest,
    TransactionResponse,
)


class InventoryService:
    def __init__(
        self,
        transactionRepository: TransactionRepository,
        stockRepository: StockRepository,
        sessionValue: AsyncSession,
    ) -> None:
        self.transactionRepository = transactionRepository
        self.stockRepository = stockRepository
        self.sessionValue = sessionValue

    async def createTransaction(
        self,
        requestValue: TransactionCreateRequest,
    ) -> TransactionResponse:
        transactionValue = await self.transactionRepository.createTransaction(
            skuId=requestValue.skuId,
            transactionDate=requestValue.transactionDate,
            demandQuantity=requestValue.demandQuantity,
        )
        await self.sessionValue.commit()
        return self.toTransactionResponse(transactionValue)

    async def listTransactions(
        self,
        skuId: str | None,
        limit: int,
    ) -> list[TransactionResponse]:
        transactionItems = await self.transactionRepository.listTransactions(
            skuId=skuId,
            limit=limit,
        )
        return [self.toTransactionResponse(itemValue) for itemValue in transactionItems]

    async def deleteTransaction(self, transactionId: int) -> None:
        isDeleted = await self.transactionRepository.deleteTransaction(transactionId)
        if not isDeleted:
            raise ValueError("Transaction not found")

        await self.sessionValue.commit()

    async def listSummaries(self) -> list[InventorySummaryResponse]:
        summaryItems = await self.transactionRepository.summarizeBySku()
        return [
            InventorySummaryResponse(
                skuId=str(itemValue["skuId"]),
                transactionCount=int(itemValue["transactionCount"] or 0),
                totalDemand=round(float(itemValue["totalDemand"] or 0), 2),
                averageDemand=round(float(itemValue["averageDemand"] or 0), 2),
                lastTransactionDate=itemValue["lastTransactionDate"],
            )
            for itemValue in summaryItems
        ]

    # Dibantu AI: updateCurrentStock
    async def updateCurrentStock(
        self,
        skuId: str,
        requestValue: StockUpdateRequest,
    ) -> StockUpdateResponse:
        stockValue = await self.stockRepository.upsertStock(
            skuId=skuId,
            currentStock=requestValue.currentStock,
        )
        await self.sessionValue.commit()
        return StockUpdateResponse(
            skuId=stockValue.skuId,
            currentStock=stockValue.currentStock,
            updatedAt=stockValue.updatedAt,
        )

    def toTransactionResponse(self, transactionValue: TransactionRecord) -> TransactionResponse:
        return TransactionResponse(
            id=transactionValue.id,
            skuId=transactionValue.skuId,
            transactionDate=transactionValue.transactionDate,
            demandQuantity=transactionValue.demandQuantity,
            createdAt=transactionValue.createdAt,
        )
