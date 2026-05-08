from __future__ import annotations

from app.services.ai.aiService import AiService


class NoopAiService(AiService):
    # dibantu AI: generateInsight
    async def generateInsight(self, promptValue: str) -> str:
        return "AI provider unavailable"
