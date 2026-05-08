from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from app.core.security import hashSecret
from app.repositories.refreshTokenRepository import RefreshTokenRepository
from app.repositories.userRepository import UserRepository
from app.schemas.authSchema import LoginRequest, RefreshRequest, RegisterRequest
from app.services.authService import AuthService


class FakeSession:
    def __init__(self) -> None:
        self.commitCount = 0

    async def commit(self) -> None:
        self.commitCount += 1


class FakeUser:
    def __init__(self, userId: int, email: str, passwordHash: str) -> None:
        self.id = userId
        self.email = email
        self.passwordHash = passwordHash


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.userByEmail: dict[str, FakeUser] = {}
        self.nextId = 1

    async def findByEmail(self, email: str):
        return self.userByEmail.get(email)

    async def findById(self, userId: int):
        for userValue in self.userByEmail.values():
            if userValue.id == userId:
                return userValue
        return None

    async def saveUser(self, userValue):
        userValue.id = self.nextId
        self.nextId += 1
        fakeUser = FakeUser(
            userId=userValue.id,
            email=userValue.email,
            passwordHash=userValue.passwordHash,
        )
        self.userByEmail[userValue.email] = fakeUser
        return fakeUser


@dataclass
class FakeTokenRecord:
    tokenId: str
    tokenHash: str
    userId: int
    expiresAt: datetime
    revokedAt: datetime | None = None


class FakeRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self) -> None:
        self.tokenItems: list[FakeTokenRecord] = []

    async def createTokenRecord(self, tokenId: str, tokenHash: str, userId: int, expiresAt: datetime):
        tokenValue = FakeTokenRecord(
            tokenId=tokenId,
            tokenHash=tokenHash,
            userId=userId,
            expiresAt=expiresAt,
        )
        self.tokenItems.append(tokenValue)
        return tokenValue

    async def findActiveByHash(self, tokenHash: str):
        nowValue = datetime.now(timezone.utc)
        for tokenValue in self.tokenItems:
            if tokenValue.tokenHash == tokenHash and tokenValue.revokedAt is None and tokenValue.expiresAt > nowValue:
                return tokenValue
        return None

    async def revokeByTokenId(self, tokenId: str):
        for tokenValue in self.tokenItems:
            if tokenValue.tokenId == tokenId and tokenValue.revokedAt is None:
                tokenValue.revokedAt = datetime.now(timezone.utc)

    async def revokeByUserId(self, userId: int):
        for tokenValue in self.tokenItems:
            if tokenValue.userId == userId and tokenValue.revokedAt is None:
                tokenValue.revokedAt = datetime.now(timezone.utc)


@pytest.mark.asyncio
# dibantu AI: testRegisterAndLogin
async def testRegisterAndLogin() -> None:
    sessionValue = FakeSession()
    userRepository = FakeUserRepository()
    refreshRepository = FakeRefreshTokenRepository()
    serviceValue = AuthService(userRepository, refreshRepository, sessionValue)

    registerResult = await serviceValue.registerUser(
        RegisterRequest(email="owner@brewstock.id", password="securePass123"),
    )

    assert registerResult.accessToken != ""
    assert registerResult.refreshToken != ""
    assert sessionValue.commitCount == 1

    loginResult = await serviceValue.loginUser(
        LoginRequest(email="owner@brewstock.id", password="securePass123"),
    )

    assert loginResult.accessToken != ""
    assert loginResult.refreshToken != ""
    assert sessionValue.commitCount == 2


@pytest.mark.asyncio
# dibantu AI: testRefreshRotation
async def testRefreshRotation() -> None:
    sessionValue = FakeSession()
    userRepository = FakeUserRepository()
    refreshRepository = FakeRefreshTokenRepository()
    serviceValue = AuthService(userRepository, refreshRepository, sessionValue)

    userRepository.userByEmail["bar@brewstock.id"] = FakeUser(
        userId=1,
        email="bar@brewstock.id",
        passwordHash=hashSecret("securePass123"),
    )

    tokenValue = await serviceValue.loginUser(
        LoginRequest(email="bar@brewstock.id", password="securePass123"),
    )

    refreshResult = await serviceValue.refreshSession(
        RefreshRequest(refreshToken=tokenValue.refreshToken),
    )

    assert refreshResult.refreshToken != tokenValue.refreshToken
    revokedCount = len([itemValue for itemValue in refreshRepository.tokenItems if itemValue.revokedAt is not None])
    assert revokedCount >= 1
