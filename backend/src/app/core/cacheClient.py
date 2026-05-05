from __future__ import annotations

from redis.asyncio import Redis

from app.core.settings import loadSettings

redisClientCache: Redis | None = None


# Dibantu AI: getRedisClient
async def getRedisClient() -> Redis:
    global redisClientCache
    if redisClientCache is None:
        settings = loadSettings()
        redisClientCache = Redis.from_url(settings.redisUrl, decode_responses=True)
    return redisClientCache
