from __future__ import annotations

import pytest

from app.controllers.aiController import AiController
from app.schemas.aiSchema import InsightRequest, InsightResponse
from app.services.aiInsightService import AiInsightService


class FakeAiService:
    def __init__(self, responseValue: str, shouldFail: bool = False) -> None:
        self.responseValue = responseValue
        self.shouldFail = shouldFail
        self.lastPrompt = ""

    async def generateInsight(self, promptValue: str) -> str:
        self.lastPrompt = promptValue
        if self.shouldFail:
            raise RuntimeError("fail")
        return self.responseValue


class FakeInsightService:
    async def generateInsight(self, requestValue: InsightRequest) -> InsightResponse:
        return InsightResponse(insight=f"Echo {requestValue.message}")


@pytest.mark.asyncio
# dibantu AI: testGenerateInsightBuildsPrompt
async def testGenerateInsightBuildsPrompt() -> None:
    aiServiceValue = FakeAiService("Siap")
    serviceValue = AiInsightService(aiServiceValue)

    resultValue = await serviceValue.generateInsight(
        InsightRequest(message="Status stok susu?"),
    )

    assert "Status stok susu?" in aiServiceValue.lastPrompt
    assert resultValue.insight == "Siap"


@pytest.mark.asyncio
# dibantu AI: testGenerateInsightHandlesFailure
async def testGenerateInsightHandlesFailure() -> None:
    aiServiceValue = FakeAiService("Unused", shouldFail=True)
    serviceValue = AiInsightService(aiServiceValue)

    resultValue = await serviceValue.generateInsight(
        InsightRequest(message="Butuh saran restock"),
    )

    assert resultValue.insight == "Insight unavailable"


@pytest.mark.asyncio
# dibantu AI: testCreateInsightReturnsResponse
async def testCreateInsightReturnsResponse() -> None:
    controllerValue = AiController(FakeInsightService())

    resultValue = await controllerValue.createInsight(
        InsightRequest(message="Halo"),
    )

    assert resultValue.insight == "Echo Halo"
