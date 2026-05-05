from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import loadSettings

passwordContext = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# Dibantu AI: hashSecret
def hashSecret(rawSecret: str) -> str:
    return passwordContext.hash(rawSecret)


# Dibantu AI: verifySecret
def verifySecret(rawSecret: str, hashedSecret: str) -> bool:
    return passwordContext.verify(rawSecret, hashedSecret)


# Dibantu AI: buildToken
def buildToken(userId: str, tokenType: str, expireMinutes: int, tokenId: str | None = None) -> str:
    settings = loadSettings()
    expireAt = datetime.now(timezone.utc) + timedelta(minutes=expireMinutes)
    payload: Dict[str, Any] = {"sub": userId, "typ": tokenType, "exp": expireAt}
    if tokenId is not None:
        payload["jti"] = tokenId
    return jwt.encode(payload, settings.jwtSecret, algorithm=settings.jwtAlgorithm)


# Dibantu AI: readToken
def readToken(rawToken: str) -> Dict[str, Any]:
    settings = loadSettings()
    try:
        return jwt.decode(rawToken, settings.jwtSecret, algorithms=[settings.jwtAlgorithm])
    except JWTError as errorValue:
        raise ValueError("Invalid token") from errorValue


# Dibantu AI: createAccessToken
def createAccessToken(userId: str) -> str:
    settings = loadSettings()
    return buildToken(userId=userId, tokenType="access", expireMinutes=settings.accessTokenMinutes)


# Dibantu AI: createRefreshToken
def createRefreshToken(userId: str) -> tuple[str, str]:
    settings = loadSettings()
    tokenId = secrets.token_urlsafe(24)
    expireMinutes = settings.refreshTokenDays * 24 * 60
    tokenValue = buildToken(
        userId=userId,
        tokenType="refresh",
        expireMinutes=expireMinutes,
        tokenId=tokenId,
    )
    return tokenValue, tokenId
