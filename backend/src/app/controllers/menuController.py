from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.menuSchema import MenuAvailabilityRequest, MenuAvailabilityResponse
from app.services.menuService import MenuService


class MenuController:
    def __init__(self, menuService: MenuService) -> None:
        self.menuService = menuService

    # dibantu AI: listAvailability
    async def listAvailability(
        self,
        requestValue: MenuAvailabilityRequest,
    ) -> MenuAvailabilityResponse:
        try:
            return await self.menuService.buildMenuAvailability(requestValue)
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(errorValue),
            ) from errorValue
