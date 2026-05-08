from __future__ import annotations

from app.schemas.aiSchema import InsightRequest, InsightResponse
from app.services.ai.aiService import AiService


class AiInsightService:
    def __init__(self, aiService: AiService) -> None:
        self.aiService = aiService

    # dibantu AI: generateInsight
    async def generateInsight(self, requestValue: InsightRequest) -> InsightResponse:
        promptValue = (
            "Kamu adalah asisten manajer kedai kopi. "
            "Jawab ringkas, praktis, tanpa jargon. "
            f"Pertanyaan: {requestValue.message}"
        )

        try:
            insightValue = await self.aiService.generateInsight(promptValue)
        except Exception:
            insightValue = "Insight unavailable"

        return InsightResponse(insight=insightValue)
