from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    createAccessToken,
    createRefreshToken,
    hashSecret,
    readToken,
    verifySecret,
)
from app.core.settings import loadSettings
from app.models.userModel import UserAccount
from app.repositories.refreshTokenRepository import RefreshTokenRepository
from app.repositories.userRepository import UserRepository
from app.schemas.authSchema import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(
        self,
        userRepository: UserRepository,
        refreshTokenRepository: RefreshTokenRepository,
        sessionValue: AsyncSession,
    ) -> None:
        self.userRepository = userRepository
        self.refreshTokenRepository = refreshTokenRepository
        self.sessionValue = sessionValue
        self.settingsValue = loadSettings()

    # dibantu AI: registerUser
    async def registerUser(self, requestValue: RegisterRequest) -> TokenResponse:
        existingUser = await self.userRepository.findByEmail(requestValue.email)
        if existingUser is not None:
            raise ValueError("Email already exists")

        userValue = UserAccount(
            email=requestValue.email,
            passwordHash=hashSecret(requestValue.password),
        )
        await self.userRepository.saveUser(userValue)
        tokenValue = await self.issueTokens(userValue.id)
        await self.sessionValue.commit()
        return tokenValue

    # dibantu AI: loginUser
    async def loginUser(self, requestValue: LoginRequest) -> TokenResponse:
        userValue = await self.userRepository.findByEmail(requestValue.email)
        if userValue is None:
            raise ValueError("Invalid credentials")

        if not verifySecret(requestValue.password, userValue.passwordHash):
            raise ValueError("Invalid credentials")

        tokenValue = await self.issueTokens(userValue.id)
        await self.sessionValue.commit()
        return tokenValue

    # dibantu AI: refreshSession
    async def refreshSession(self, requestValue: RefreshRequest) -> TokenResponse:
        payloadValue = readToken(requestValue.refreshToken)
        if payloadValue.get("typ") != "refresh":
            raise ValueError("Invalid refresh token")

        tokenId = str(payloadValue.get("jti", ""))
        if tokenId == "":
            raise ValueError("Invalid refresh token")

        tokenHash = self.hashTokenValue(requestValue.refreshToken)
        tokenRecord = await self.refreshTokenRepository.findActiveByHash(tokenHash)
        if tokenRecord is None or tokenRecord.tokenId != tokenId:
            userIdValue = int(payloadValue.get("sub")) if payloadValue.get("sub") else None
            if userIdValue is not None:
                await self.refreshTokenRepository.revokeByUserId(userIdValue)
                await self.sessionValue.commit()
            raise ValueError("Refresh token revoked")

        await self.refreshTokenRepository.revokeByTokenId(tokenId)
        tokenValue = await self.issueTokens(tokenRecord.userId)
        await self.sessionValue.commit()
        return tokenValue

    # dibantu AI: issueTokens
    async def issueTokens(self, userId: int) -> TokenResponse:
        accessTokenValue = createAccessToken(str(userId))
        refreshTokenValue, tokenId = createRefreshToken(str(userId))
        tokenHash = self.hashTokenValue(refreshTokenValue)
        expiresAt = datetime.now(timezone.utc) + timedelta(days=self.settingsValue.refreshTokenDays)

        await self.refreshTokenRepository.createTokenRecord(
            tokenId=tokenId,
            tokenHash=tokenHash,
            userId=userId,
            expiresAt=expiresAt,
        )

        return TokenResponse(
            accessToken=accessTokenValue,
            refreshToken=refreshTokenValue,
            tokenType="bearer",
        )

    # dibantu AI: hashTokenValue
    def hashTokenValue(self, rawToken: str) -> str:
        return hashlib.sha256(rawToken.encode("utf-8")).hexdigest()
