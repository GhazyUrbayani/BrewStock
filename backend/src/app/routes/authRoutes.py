from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.authController import AuthController
from app.core.dependencies import getAuthController
from app.core.rateLimit import enforceRateLimit
from app.schemas.authSchema import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

authRouter = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@authRouter.post(
    "/register",
    response_model=TokenResponse,
    dependencies=[Depends(enforceRateLimit)],
)
# Dibantu AI: registerUser
async def registerUser(
    requestValue: RegisterRequest,
    controllerValue: AuthController = Depends(getAuthController),
) -> TokenResponse:
    return await controllerValue.registerUser(requestValue)


@authRouter.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(enforceRateLimit)],
)
# Dibantu AI: loginUser
async def loginUser(
    requestValue: LoginRequest,
    controllerValue: AuthController = Depends(getAuthController),
) -> TokenResponse:
    return await controllerValue.loginUser(requestValue)


@authRouter.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(enforceRateLimit)],
)
# Dibantu AI: refreshSession
async def refreshSession(
    requestValue: RefreshRequest,
    controllerValue: AuthController = Depends(getAuthController),
) -> TokenResponse:
    return await controllerValue.refreshSession(requestValue)
