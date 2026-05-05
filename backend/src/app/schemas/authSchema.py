from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.baseSchema import SanitizedModel


class LoginRequest(SanitizedModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterRequest(SanitizedModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(SanitizedModel):
    refreshToken: str = Field(min_length=10)


class TokenResponse(SanitizedModel):
    accessToken: str
    refreshToken: str
    tokenType: str
