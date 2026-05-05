from __future__ import annotations

import time
from typing import Any

from redis.asyncio import Redis

from app.core.settings import loadSettings


class InMemoryPipeline:
    def __init__(self, cacheValue: "InMemoryCacheClient") -> None:
        self.cacheValue = cacheValue
        self.operationItems: list[tuple[str, tuple[Any, ...]]] = []

    def zremrangebyscore(self, keyValue: str, minValue: float, maxValue: float) -> "InMemoryPipeline":
        self.operationItems.append(("zremrangebyscore", (keyValue, minValue, maxValue)))
        return self

    def zcard(self, keyValue: str) -> "InMemoryPipeline":
        self.operationItems.append(("zcard", (keyValue,)))
        return self

    def zadd(self, keyValue: str, scoreMap: dict[str, float]) -> "InMemoryPipeline":
        self.operationItems.append(("zadd", (keyValue, scoreMap)))
        return self

    def expire(self, keyValue: str, secondsValue: int) -> "InMemoryPipeline":
        self.operationItems.append(("expire", (keyValue, secondsValue)))
        return self

    async def execute(self) -> list[int]:
        resultItems: list[int] = []
        for operationName, argumentItems in self.operationItems:
            if operationName == "zremrangebyscore":
                resultItems.append(self.cacheValue.zremrangebyscore(*argumentItems))
            elif operationName == "zcard":
                resultItems.append(self.cacheValue.zcard(*argumentItems))
            elif operationName == "zadd":
                resultItems.append(self.cacheValue.zadd(*argumentItems))
            elif operationName == "expire":
                resultItems.append(self.cacheValue.expire(*argumentItems))
        return resultItems


class InMemoryCacheClient:
    def __init__(self) -> None:
        self.valueStore: dict[str, tuple[str, float | None]] = {}
        self.sortedSetStore: dict[str, dict[str, float]] = {}
        self.expiryStore: dict[str, float] = {}

    async def get(self, keyValue: str) -> str | None:
        self.purgeExpired(keyValue)
        storedValue = self.valueStore.get(keyValue)
        if storedValue is None:
            return None
        return storedValue[0]

    async def set(self, keyValue: str, payloadValue: str, ex: int | None = None) -> None:
        expiresAt = time.time() + ex if ex is not None else None
        self.valueStore[keyValue] = (payloadValue, expiresAt)

    async def close(self) -> None:
        self.valueStore.clear()
        self.sortedSetStore.clear()
        self.expiryStore.clear()

    def pipeline(self, transaction: bool = True) -> InMemoryPipeline:
        return InMemoryPipeline(self)

    def zremrangebyscore(self, keyValue: str, minValue: float, maxValue: float) -> int:
        self.purgeExpired(keyValue)
        scoreMap = self.sortedSetStore.setdefault(keyValue, {})
        removeItems = [
            memberValue
            for memberValue, scoreValue in scoreMap.items()
            if minValue <= scoreValue <= maxValue
        ]
        for memberValue in removeItems:
            del scoreMap[memberValue]
        return len(removeItems)

    def zcard(self, keyValue: str) -> int:
        self.purgeExpired(keyValue)
        return len(self.sortedSetStore.get(keyValue, {}))

    def zadd(self, keyValue: str, scoreMap: dict[str, float]) -> int:
        self.purgeExpired(keyValue)
        targetMap = self.sortedSetStore.setdefault(keyValue, {})
        addedCount = 0
        for memberValue, scoreValue in scoreMap.items():
            if memberValue not in targetMap:
                addedCount += 1
            targetMap[memberValue] = scoreValue
        return addedCount

    def expire(self, keyValue: str, secondsValue: int) -> int:
        self.expiryStore[keyValue] = time.time() + secondsValue
        return 1

    def purgeExpired(self, keyValue: str) -> None:
        valueItem = self.valueStore.get(keyValue)
        if valueItem is not None and valueItem[1] is not None and valueItem[1] <= time.time():
            del self.valueStore[keyValue]

        expiresAt = self.expiryStore.get(keyValue)
        if expiresAt is not None and expiresAt <= time.time():
            self.expiryStore.pop(keyValue, None)
            self.sortedSetStore.pop(keyValue, None)


CacheClient = Redis | InMemoryCacheClient
redisClientCache: CacheClient | None = None


# Dibantu AI: getRedisClient
async def getRedisClient() -> CacheClient:
    global redisClientCache
    if redisClientCache is None:
        settings = loadSettings()
        candidateClient = Redis.from_url(settings.redisUrl, decode_responses=True)
        try:
            await candidateClient.ping()
            redisClientCache = candidateClient
        except Exception:
            await candidateClient.close()
            redisClientCache = InMemoryCacheClient()
    return redisClientCache
