from __future__ import annotations

from app.schemas.aiSchema import InsightRequest, InsightResponse
from app.services.aiInsightService import AiInsightService


class AiController:
    def __init__(self, insightService: AiInsightService) -> None:
        self.insightService = insightService

    # dibantu AI: createInsight
    async def createInsight(self, requestValue: InsightRequest) -> InsightResponse:
        return await self.insightService.generateInsight(requestValue)
