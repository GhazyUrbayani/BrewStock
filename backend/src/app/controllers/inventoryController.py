from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.inventorySchema import (
    InventorySummaryResponse,
    StockUpdateRequest,
    StockUpdateResponse,
    TransactionCreateRequest,
    TransactionResponse,
)
from app.services.inventoryService import InventoryService


class InventoryController:
    def __init__(self, inventoryService: InventoryService) -> None:
        self.inventoryService = inventoryService

    async def createTransaction(
        self,
        requestValue: TransactionCreateRequest,
    ) -> TransactionResponse:
        return await self.inventoryService.createTransaction(requestValue)

    async def listTransactions(
        self,
        skuId: str | None,
        limit: int,
    ) -> list[TransactionResponse]:
        return await self.inventoryService.listTransactions(skuId=skuId, limit=limit)

    async def deleteTransaction(self, transactionId: int) -> dict[str, str]:
        try:
            await self.inventoryService.deleteTransaction(transactionId)
            return {"status": "deleted"}
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(errorValue),
            ) from errorValue

    async def listSummaries(self) -> list[InventorySummaryResponse]:
        return await self.inventoryService.listSummaries()

    # Dibantu AI: updateStock
    async def updateStock(
        self,
        skuId: str,
        requestValue: StockUpdateRequest,
    ) -> StockUpdateResponse:
        try:
            return await self.inventoryService.updateCurrentStock(skuId, requestValue)
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(errorValue),
            ) from errorValue
