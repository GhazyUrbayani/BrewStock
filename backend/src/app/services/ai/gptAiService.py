from __future__ import annotations

import httpx

from app.services.ai.aiService import AiService


class GptAiService(AiService):
    def __init__(self, apiKey: str) -> None:
        self.apiKey = apiKey

    # dibantu AI: generateInsight
    async def generateInsight(self, promptValue: str) -> str:
        if self.apiKey == "":
            return "GPT key missing"

        requestBody = {
            "model": "gpt-4.1-mini",
            "messages": [{"role": "user", "content": promptValue}],
            "temperature": 0.2,
            "max_tokens": 220,
        }

        headersValue = {
            "Authorization": f"Bearer {self.apiKey}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15) as clientValue:
            responseValue = await clientValue.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headersValue,
                json=requestBody,
            )
            responseValue.raise_for_status()
            payloadValue = responseValue.json()
            choiceItems = payloadValue.get("choices", [])
            if not choiceItems:
                return "Insight unavailable"
            firstChoice = choiceItems[0]
            messageValue = firstChoice.get("message", {})
            return str(messageValue.get("content", "Insight unavailable"))
