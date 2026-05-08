from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refreshTokenModel import RefreshTokenRecord


class RefreshTokenRepository:
    def __init__(self, sessionValue: AsyncSession) -> None:
        self.sessionValue = sessionValue

    # dibantu AI: createTokenRecord
    async def createTokenRecord(
        self,
        tokenId: str,
        tokenHash: str,
        userId: int,
        expiresAt: datetime,
    ) -> RefreshTokenRecord:
        tokenValue = RefreshTokenRecord(
            tokenId=tokenId,
            tokenHash=tokenHash,
            userId=userId,
            expiresAt=expiresAt,
        )
        self.sessionValue.add(tokenValue)
        await self.sessionValue.flush()
        await self.sessionValue.refresh(tokenValue)
        return tokenValue

    # dibantu AI: findActiveByHash
    async def findActiveByHash(self, tokenHash: str) -> RefreshTokenRecord | None:
        nowValue = datetime.now(timezone.utc)
        queryValue = select(RefreshTokenRecord).where(
            RefreshTokenRecord.tokenHash == tokenHash,
            RefreshTokenRecord.revokedAt.is_(None),
            RefreshTokenRecord.expiresAt > nowValue,
        )
        resultValue = await self.sessionValue.execute(queryValue)
        return resultValue.scalar_one_or_none()

    # dibantu AI: revokeByTokenId
    async def revokeByTokenId(self, tokenId: str) -> None:
        queryValue = select(RefreshTokenRecord).where(RefreshTokenRecord.tokenId == tokenId)
        resultValue = await self.sessionValue.execute(queryValue)
        tokenValue = resultValue.scalar_one_or_none()
        if tokenValue is not None and tokenValue.revokedAt is None:
            tokenValue.revokedAt = datetime.now(timezone.utc)

    # dibantu AI: revokeByUserId
    async def revokeByUserId(self, userId: int) -> None:
        queryValue = select(RefreshTokenRecord).where(
            RefreshTokenRecord.userId == userId,
            RefreshTokenRecord.revokedAt.is_(None),
        )
        resultValue = await self.sessionValue.execute(queryValue)
        tokenItems = resultValue.scalars().all()
        nowValue = datetime.now(timezone.utc)
        for tokenValue in tokenItems:
            tokenValue.revokedAt = nowValue
