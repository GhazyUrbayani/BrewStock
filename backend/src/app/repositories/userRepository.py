from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.userModel import UserAccount


class UserRepository:
    def __init__(self, sessionValue: AsyncSession) -> None:
        self.sessionValue = sessionValue

    # dibantu AI: findByEmail
    async def findByEmail(self, email: str) -> UserAccount | None:
        queryValue = select(UserAccount).where(UserAccount.email == email)
        resultValue = await self.sessionValue.execute(queryValue)
        return resultValue.scalar_one_or_none()

    # dibantu AI: findById
    async def findById(self, userId: int) -> UserAccount | None:
        queryValue = select(UserAccount).where(UserAccount.id == userId)
        resultValue = await self.sessionValue.execute(queryValue)
        return resultValue.scalar_one_or_none()

    # dibantu AI: saveUser
    async def saveUser(self, userValue: UserAccount) -> UserAccount:
        self.sessionValue.add(userValue)
        await self.sessionValue.flush()
        await self.sessionValue.refresh(userValue)
        return userValue
