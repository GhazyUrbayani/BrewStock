from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cacheClient import getRedisClient
from app.core.database import asyncEngine, baseModel
from app.core.settings import loadSettings
from app.routes.authRoutes import authRouter
from app.routes.forecastRoutes import forecastRouter
from app.routes.inventoryRoutes import inventoryRouter

settingsValue = loadSettings()


# dibantu AI: lifespan
@asynccontextmanager
async def lifespan(appValue: FastAPI):
    async with asyncEngine.begin() as connectionValue:
        await connectionValue.run_sync(baseModel.metadata.create_all)

    yield

    redisClient = await getRedisClient()
    await redisClient.close()


app = FastAPI(
    title=settingsValue.appName,
    version=settingsValue.appVersion,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settingsValue.allowedOrigins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(authRouter)
app.include_router(inventoryRouter)
app.include_router(forecastRouter)


@app.get("/health")
# dibantu AI: readHealth
async def readHealth() -> dict[str, str]:
    return {"status": "ok"}
