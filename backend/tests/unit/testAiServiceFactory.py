from __future__ import annotations

from app.core.settings import AppSettings
from app.factories.aiServiceFactory import AiServiceFactory
from app.services.ai.claudeAiService import ClaudeAiService
from app.services.ai.gptAiService import GptAiService
from app.services.ai.noopAiService import NoopAiService


# dibantu AI: testCreateServiceTypes
def testCreateServiceTypes() -> None:
    settingsValue = AppSettings(
        appName="BrewStock API",
        appVersion="0.1.0",
        databaseUrl="postgresql+asyncpg://postgres:postgres@localhost:5432/brewstock",
        redisUrl="redis://localhost:6379/0",
        jwtSecret="secret",
        jwtAlgorithm="HS256",
        accessTokenMinutes=30,
        refreshTokenDays=7,
        allowedOrigins=["http://localhost:5173"],
        claudeApiKey="claudeKey",
        gptApiKey="gptKey",
        rateLimitCount=100,
        rateLimitWindowSeconds=60,
        forecastCacheTtlSeconds=3600,
    )
    factoryValue = AiServiceFactory(settingsValue)

    assert isinstance(factoryValue.createService("claude"), ClaudeAiService)
    assert isinstance(factoryValue.createService("gpt"), GptAiService)
    assert isinstance(factoryValue.createService("other"), NoopAiService)
