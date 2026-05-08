from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.forecastSchema import ForecastRequest, ForecastResponse
from app.services.forecastService import ForecastService


class ForecastController:
    def __init__(self, forecastService: ForecastService) -> None:
        self.forecastService = forecastService

    # dibantu AI: createForecast
    async def createForecast(self, requestValue: ForecastRequest) -> ForecastResponse:
        try:
            return await self.forecastService.generateForecast(requestValue)
        except (RuntimeError, ValueError) as errorValue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(errorValue),
            ) from errorValue
