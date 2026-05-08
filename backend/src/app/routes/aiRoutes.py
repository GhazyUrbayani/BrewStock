from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.aiController import AiController
from app.core.dependencies import getAiController, readCurrentUserId
from app.core.rateLimit import enforceRateLimit
from app.schemas.aiSchema import InsightRequest, InsightResponse

aiRouter = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@aiRouter.post(
    "/insight",
    response_model=InsightResponse,
    dependencies=[Depends(enforceRateLimit), Depends(readCurrentUserId)],
)
# dibantu AI: createInsight
async def createInsight(
    requestValue: InsightRequest,
    controllerValue: AiController = Depends(getAiController),
) -> InsightResponse:
    return await controllerValue.createInsight(requestValue)
