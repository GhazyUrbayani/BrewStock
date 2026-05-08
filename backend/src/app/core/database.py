from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine as createAsyncEngine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.settings import loadSettings

settings = loadSettings()
baseModel = declarative_base()
asyncEngine: AsyncEngine = createAsyncEngine(settings.databaseUrl, pool_pre_ping=True)
sessionFactory = sessionmaker(bind=asyncEngine, class_=AsyncSession, expire_on_commit=False)


# dibantu AI: getSession
async def getSession() -> AsyncGenerator[AsyncSession, None]:
    sessionValue: AsyncSession = sessionFactory()
    try:
        yield sessionValue
    finally:
        await sessionValue.close()
