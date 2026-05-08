from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.menuController import MenuController
from app.core.dependencies import getMenuController, readCurrentUserId
from app.core.rateLimit import enforceRateLimit
from app.schemas.menuSchema import MenuAvailabilityRequest, MenuAvailabilityResponse

menuRouter = APIRouter(prefix="/api/v1/menu", tags=["menu"])


@menuRouter.post(
    "/availability",
    response_model=MenuAvailabilityResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
# dibantu AI: listMenuAvailability
async def listMenuAvailability(
    requestValue: MenuAvailabilityRequest,
    controllerValue: MenuController = Depends(getMenuController),
) -> MenuAvailabilityResponse:
    return await controllerValue.listAvailability(requestValue)
