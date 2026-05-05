from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core.rateLimit import SlidingWindowLimiter


class AllowLimiter(SlidingWindowLimiter):
    async def allowRequest(self, ipAddress: str) -> bool:
        return True


class DenyLimiter(SlidingWindowLimiter):
    async def allowRequest(self, ipAddress: str) -> bool:
        return False


# Dibantu AI: buildRequest
def buildRequest() -> Request:
    scopeValue = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 5010),
        "server": ("test", 80),
        "scheme": "http",
        "http_version": "1.1",
    }
    return Request(scopeValue)


@pytest.mark.asyncio
# Dibantu AI: testApplyLimitAllows
async def testApplyLimitAllows() -> None:
    limiterValue = AllowLimiter(requestLimit=100, windowSeconds=60)
    requestValue = buildRequest()

    await limiterValue.applyLimit(requestValue)


@pytest.mark.asyncio
# Dibantu AI: testApplyLimitBlocks
async def testApplyLimitBlocks() -> None:
    limiterValue = DenyLimiter(requestLimit=100, windowSeconds=60)
    requestValue = buildRequest()

    with pytest.raises(HTTPException) as errorInfo:
        await limiterValue.applyLimit(requestValue)

    assert errorInfo.value.status_code == 429
