from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.authController import AuthController
from app.controllers.forecastController import ForecastController
from app.controllers.inventoryController import InventoryController
from app.core.cacheClient import getRedisClient
from app.core.database import getSession
from app.core.security import readToken
from app.factories.aiServiceFactory import AiServiceFactory
from app.observers.aiStockObserver import AiStockObserver
from app.observers.logStockObserver import LogStockObserver
from app.observers.stockAlertPublisher import StockAlertPublisher
from app.repositories.refreshTokenRepository import RefreshTokenRepository
from app.repositories.transactionRepository import TransactionRepository
from app.repositories.userRepository import UserRepository
from app.services.authService import AuthService
from app.services.forecastService import ForecastService
from app.services.inventoryService import InventoryService
from app.strategies.prophetStrategy import ProphetStrategy
from app.strategies.xgboostStrategy import XgboostStrategy

httpBearer = HTTPBearer()


# dibantu AI: getForecastController
async def getForecastController(
    sessionValue: AsyncSession = Depends(getSession),
) -> ForecastController:
    cacheValue = await getRedisClient()
    transactionRepository = TransactionRepository(sessionValue)
    strategyMap = {
        "prophet": ProphetStrategy(),
        "xgboost": XgboostStrategy(),
    }

    aiServiceFactory = AiServiceFactory()
    alertPublisher = StockAlertPublisher()
    alertPublisher.registerObserver(LogStockObserver())
    alertPublisher.registerObserver(AiStockObserver(aiServiceFactory.createService("claude")))

    forecastService = ForecastService(
        transactionRepository=transactionRepository,
        strategyMap=strategyMap,
        cacheValue=cacheValue,
        alertPublisher=alertPublisher,
    )
    return ForecastController(forecastService)


async def getInventoryController(
    sessionValue: AsyncSession = Depends(getSession),
) -> InventoryController:
    transactionRepository = TransactionRepository(sessionValue)
    inventoryService = InventoryService(
        transactionRepository=transactionRepository,
        sessionValue=sessionValue,
    )
    return InventoryController(inventoryService)


# dibantu AI: getAuthController
async def getAuthController(
    sessionValue: AsyncSession = Depends(getSession),
) -> AuthController:
    userRepository = UserRepository(sessionValue)
    refreshTokenRepository = RefreshTokenRepository(sessionValue)
    authService = AuthService(
        userRepository=userRepository,
        refreshTokenRepository=refreshTokenRepository,
        sessionValue=sessionValue,
    )
    return AuthController(authService)


# dibantu AI: readCurrentUserId
async def readCurrentUserId(
    authValue: HTTPAuthorizationCredentials = Depends(httpBearer),
) -> int:
    try:
        payloadValue = readToken(authValue.credentials)
        if payloadValue.get("typ") != "access":
            raise ValueError("Invalid access type")

        userIdRaw = payloadValue.get("sub")
        if userIdRaw is None:
            raise ValueError("User id missing")

        return int(userIdRaw)
    except Exception as errorValue:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from errorValue
