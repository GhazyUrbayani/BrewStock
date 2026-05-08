from __future__ import annotations

import time
import uuid

from fastapi import HTTPException, Request, status

from app.core.cacheClient import getRedisClient
from app.core.settings import loadSettings


class SlidingWindowLimiter:
    def __init__(self, requestLimit: int, windowSeconds: int) -> None:
        self.requestLimit = requestLimit
        self.windowSeconds = windowSeconds
        self.windowMillis = windowSeconds * 1000

    # dibantu AI: allowRequest
    async def allowRequest(self, ipAddress: str) -> bool:
        redisClient = await getRedisClient()
        nowMillis = int(time.time() * 1000)
        floorMillis = nowMillis - self.windowMillis
        keyValue = f"rateLimit:{ipAddress}"
        memberValue = f"{nowMillis}:{uuid.uuid4()}"

        pipelineValue = redisClient.pipeline(transaction=True)
        pipelineValue.zremrangebyscore(keyValue, 0, floorMillis)
        pipelineValue.zcard(keyValue)
        pipelineValue.zadd(keyValue, {memberValue: nowMillis})
        pipelineValue.expire(keyValue, self.windowSeconds + 1)

        _, requestCount, _, _ = await pipelineValue.execute()
        return int(requestCount) < self.requestLimit

    # dibantu AI: applyLimit
    async def applyLimit(self, request: Request) -> None:
        ipAddress = request.client.host if request.client else "unknown"
        isAllowed = await self.allowRequest(ipAddress)
        if not isAllowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.windowSeconds)},
            )


rateLimiterCache: SlidingWindowLimiter | None = None


# dibantu AI: getRateLimiter
async def getRateLimiter() -> SlidingWindowLimiter:
    global rateLimiterCache
    if rateLimiterCache is None:
        settings = loadSettings()
        rateLimiterCache = SlidingWindowLimiter(
            requestLimit=settings.rateLimitCount,
            windowSeconds=settings.rateLimitWindowSeconds,
        )
    return rateLimiterCache


# dibantu AI: enforceRateLimit
async def enforceRateLimit(request: Request) -> None:
    rateLimiter = await getRateLimiter()
    await rateLimiter.applyLimit(request)
