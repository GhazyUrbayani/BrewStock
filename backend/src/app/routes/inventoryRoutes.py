from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.controllers.inventoryController import InventoryController
from app.core.dependencies import getInventoryController, readCurrentUserId
from app.core.rateLimit import enforceRateLimit
from app.schemas.inventorySchema import (
    DashboardKpiResponse,
    InventoryAlertResponse,
    InventorySummaryResponse,
    StockUpdateRequest,
    StockUpdateResponse,
    TransactionCreateRequest,
    TransactionResponse,
)

inventoryRouter = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@inventoryRouter.get(
    "/transactions",
    response_model=list[TransactionResponse],
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
async def listTransactions(
    skuId: str | None = Query(default=None, min_length=1, max_length=64),
    limit: int = Query(default=100, ge=1, le=500),
    controllerValue: InventoryController = Depends(getInventoryController),
) -> list[TransactionResponse]:
    return await controllerValue.listTransactions(skuId=skuId, limit=limit)


@inventoryRouter.post(
    "/transactions",
    response_model=TransactionResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
async def createTransaction(
    requestValue: TransactionCreateRequest,
    controllerValue: InventoryController = Depends(getInventoryController),
) -> TransactionResponse:
    return await controllerValue.createTransaction(requestValue)


@inventoryRouter.delete(
    "/transactions/{transactionId}",
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
async def deleteTransaction(
    transactionId: int,
    controllerValue: InventoryController = Depends(getInventoryController),
) -> dict[str, str]:
    return await controllerValue.deleteTransaction(transactionId)


@inventoryRouter.get(
    "/summary",
    response_model=list[InventorySummaryResponse],
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
async def listSummaries(
    controllerValue: InventoryController = Depends(getInventoryController),
) -> list[InventorySummaryResponse]:
    return await controllerValue.listSummaries()


@inventoryRouter.get(
    "/kpi",
    response_model=DashboardKpiResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
async def getDashboardKpi(
    controllerValue: InventoryController = Depends(getInventoryController),
) -> DashboardKpiResponse:
    return await controllerValue.getDashboardKpi()


@inventoryRouter.get(
    "/alerts",
    response_model=list[InventoryAlertResponse],
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
# dibantu AI: listAlerts
async def listAlerts(
    controllerValue: InventoryController = Depends(getInventoryController),
) -> list[InventoryAlertResponse]:
    return await controllerValue.listAlerts()


@inventoryRouter.patch(
    "/{skuId}/stock",
    response_model=StockUpdateResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
# Dibantu AI: updateStock
async def updateStock(
    skuId: str,
    requestValue: StockUpdateRequest,
    controllerValue: InventoryController = Depends(getInventoryController),
) -> StockUpdateResponse:
    return await controllerValue.updateStock(skuId, requestValue)
