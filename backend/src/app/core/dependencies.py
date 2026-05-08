from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.aiController import AiController
from app.controllers.authController import AuthController
from app.controllers.menuController import MenuController
from app.controllers.forecastController import ForecastController
from app.controllers.inventoryController import InventoryController
from app.controllers.scannerController import ScannerController
from app.core.cacheClient import getRedisClient
from app.core.database import getSession
from app.core.settings import loadSettings
from app.core.security import readToken
from app.factories.aiServiceFactory import AiServiceFactory
from app.observers.aiStockObserver import AiStockObserver
from app.observers.logStockObserver import LogStockObserver
from app.observers.stockAlertPublisher import StockAlertPublisher
from app.repositories.refreshTokenRepository import RefreshTokenRepository
from app.repositories.stockRepository import StockRepository
from app.repositories.transactionRepository import TransactionRepository
from app.repositories.userRepository import UserRepository
from app.services.authService import AuthService
from app.services.aiInsightService import AiInsightService
from app.services.forecastService import ForecastService
from app.services.inventoryService import InventoryService
from app.services.menuService import MenuService
from app.services.scannerService import ScannerService
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


# dibantu AI: getAiController
async def getAiController() -> AiController:
    settingsValue = loadSettings()
    providerName = "claude" if settingsValue.claudeApiKey != "" else "noop"
    aiServiceFactory = AiServiceFactory(settingsValue)
    aiService = aiServiceFactory.createService(providerName)
    insightService = AiInsightService(aiService)
    return AiController(insightService)


# dibantu AI: buildInventoryService
def buildInventoryService(sessionValue: AsyncSession) -> InventoryService:
    transactionRepository = TransactionRepository(sessionValue)
    stockRepository = StockRepository(sessionValue)
    return InventoryService(
        transactionRepository=transactionRepository,
        stockRepository=stockRepository,
        sessionValue=sessionValue,
    )


# dibantu AI: getInventoryController
async def getInventoryController(
    sessionValue: AsyncSession = Depends(getSession),
) -> InventoryController:
    inventoryService = buildInventoryService(sessionValue)
    return InventoryController(inventoryService)


# dibantu AI: getScannerController
async def getScannerController(
    sessionValue: AsyncSession = Depends(getSession),
) -> ScannerController:
    settingsValue = loadSettings()
    scannerService = ScannerService.getInstance(settingsValue.yoloModelPath)
    inventoryService = buildInventoryService(sessionValue)
    return ScannerController(
        scannerService=scannerService,
        inventoryService=inventoryService,
    )


# dibantu AI: getMenuController
async def getMenuController() -> MenuController:
    menuService = MenuService()
    return MenuController(menuService)


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
