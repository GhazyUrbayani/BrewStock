from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.authSchema import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.services.authService import AuthService


class AuthController:
    def __init__(self, authService: AuthService) -> None:
        self.authService = authService

    # dibantu AI: registerUser
    async def registerUser(self, requestValue: RegisterRequest) -> TokenResponse:
        try:
            return await self.authService.registerUser(requestValue)
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(errorValue),
            ) from errorValue

    # dibantu AI: loginUser
    async def loginUser(self, requestValue: LoginRequest) -> TokenResponse:
        try:
            return await self.authService.loginUser(requestValue)
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(errorValue),
            ) from errorValue

    # dibantu AI: refreshSession
    async def refreshSession(self, requestValue: RefreshRequest) -> TokenResponse:
        try:
            return await self.authService.refreshSession(requestValue)
        except ValueError as errorValue:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(errorValue),
            ) from errorValue
