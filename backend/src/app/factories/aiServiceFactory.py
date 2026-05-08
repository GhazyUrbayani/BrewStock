from __future__ import annotations

from app.core.settings import AppSettings, loadSettings
from app.services.ai.aiService import AiService
from app.services.ai.claudeAiService import ClaudeAiService
from app.services.ai.gptAiService import GptAiService
from app.services.ai.noopAiService import NoopAiService


class AiServiceFactory:
    def __init__(self, settingsValue: AppSettings | None = None) -> None:
        self.settingsValue = settingsValue or loadSettings()

    # dibantu AI: createService
    def createService(self, providerName: str) -> AiService:
        normalizedProvider = providerName.lower()

        if normalizedProvider == "claude":
            return ClaudeAiService(self.settingsValue.claudeApiKey)

        if normalizedProvider == "gpt":
            return GptAiService(self.settingsValue.gptApiKey)

        return NoopAiService()
