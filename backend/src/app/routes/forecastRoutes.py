from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.forecastController import ForecastController
from app.core.dependencies import getForecastController, readCurrentUserId
from app.core.rateLimit import enforceRateLimit
from app.schemas.forecastSchema import ForecastRequest, ForecastResponse

forecastRouter = APIRouter(prefix="/api/v1/forecast", tags=["forecast"])


@forecastRouter.post(
    "/demand",
    response_model=ForecastResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
# dibantu AI: createDemandForecast
async def createDemandForecast(
    requestValue: ForecastRequest,
    controllerValue: ForecastController = Depends(getForecastController),
) -> ForecastResponse:
    return await controllerValue.createForecast(requestValue)
