from __future__ import annotations

import httpx

from app.services.ai.aiService import AiService


class ClaudeAiService(AiService):
    def __init__(self, apiKey: str) -> None:
        self.apiKey = apiKey

    # Dibantu AI: generateInsight
    async def generateInsight(self, promptValue: str) -> str:
        if self.apiKey == "":
            return "Claude key missing"

        requestBody = {
            "model": "claude-3-5-sonnet-latest",
            "max_tokens": 220,
            "messages": [{"role": "user", "content": promptValue}],
        }

        headersValue = {
            "x-api-key": self.apiKey,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15) as clientValue:
            responseValue = await clientValue.post(
                "https://api.anthropic.com/v1/messages",
                headers=headersValue,
                json=requestBody,
            )
            responseValue.raise_for_status()
            payloadValue = responseValue.json()
            contentItems = payloadValue.get("content", [])
            if not contentItems:
                return "Insight unavailable"
            firstItem = contentItems[0]
            return str(firstItem.get("text", "Insight unavailable"))
