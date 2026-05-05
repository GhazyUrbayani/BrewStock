from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class AppSettings:
    appName: str
    appVersion: str
    databaseUrl: str
    redisUrl: str
    jwtSecret: str
    jwtAlgorithm: str
    accessTokenMinutes: int
    refreshTokenDays: int
    allowedOrigins: List[str]
    claudeApiKey: str
    gptApiKey: str
    rateLimitCount: int
    rateLimitWindowSeconds: int
    forecastCacheTtlSeconds: int


settingsCache: AppSettings | None = None


# Dibantu AI: parseIntValue
def parseIntValue(rawValue: str | None, defaultValue: int) -> int:
    if rawValue is None or rawValue == "":
        return defaultValue
    return int(rawValue)


# Dibantu AI: splitOriginsValue
def splitOriginsValue(rawValue: str) -> List[str]:
    originItems = [origin.strip() for origin in rawValue.split(",")]
    return [origin for origin in originItems if origin]


# Dibantu AI: loadSettings
def loadSettings() -> AppSettings:
    global settingsCache
    if settingsCache is not None:
        return settingsCache

    allowedOriginsValue = os.getenv("allowedOrigins", "http://localhost:5173")
    settingsCache = AppSettings(
        appName=os.getenv("appName", "BrewStock API"),
        appVersion=os.getenv("appVersion", "0.1.0"),
        databaseUrl=os.getenv(
            "databaseUrl",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/brewstock",
        ),
        redisUrl=os.getenv("redisUrl", "redis://localhost:6379/0"),
        jwtSecret=os.getenv("jwtSecret", "replaceThisSecret"),
        jwtAlgorithm=os.getenv("jwtAlgorithm", "HS256"),
        accessTokenMinutes=parseIntValue(os.getenv("accessTokenMinutes"), 30),
        refreshTokenDays=parseIntValue(os.getenv("refreshTokenDays"), 7),
        allowedOrigins=splitOriginsValue(allowedOriginsValue),
        claudeApiKey=os.getenv("claudeApiKey", ""),
        gptApiKey=os.getenv("gptApiKey", ""),
        rateLimitCount=parseIntValue(os.getenv("rateLimitCount"), 100),
        rateLimitWindowSeconds=parseIntValue(os.getenv("rateLimitWindowSeconds"), 60),
        forecastCacheTtlSeconds=parseIntValue(os.getenv("forecastCacheTtlSeconds"), 3600),
    )
    return settingsCache
