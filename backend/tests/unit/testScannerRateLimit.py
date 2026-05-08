from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core import rateLimit
from app.core.rateLimit import SlidingWindowLimiter


class AllowLimiter(SlidingWindowLimiter):
    async def allowRequest(self, ipAddress: str) -> bool:
        return True


class DenyLimiter(SlidingWindowLimiter):
    async def allowRequest(self, ipAddress: str) -> bool:
        return False


@pytest.mark.asyncio
# Dibantu AI: testScannerRateLimitAllows
async def testScannerRateLimitAllows(monkeypatch) -> None:
    async def fakeGetScannerRateLimiter() -> SlidingWindowLimiter:
        return AllowLimiter(requestLimit=10, windowSeconds=60)

    monkeypatch.setattr(rateLimit, "getScannerRateLimiter", fakeGetScannerRateLimiter)

    await rateLimit.enforceScannerRateLimit(userId=12)


@pytest.mark.asyncio
# Dibantu AI: testScannerRateLimitBlocks
async def testScannerRateLimitBlocks(monkeypatch) -> None:
    async def fakeGetScannerRateLimiter() -> SlidingWindowLimiter:
        return DenyLimiter(requestLimit=10, windowSeconds=60)

    monkeypatch.setattr(rateLimit, "getScannerRateLimiter", fakeGetScannerRateLimiter)

    with pytest.raises(HTTPException) as errorInfo:
        await rateLimit.enforceScannerRateLimit(userId=12)

    assert errorInfo.value.status_code == 429
