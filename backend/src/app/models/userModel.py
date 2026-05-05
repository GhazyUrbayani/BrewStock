from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column as mappedColumn

from app.core.database import baseModel


class UserAccount(baseModel):
    __tablename__ = "userAccount"

    id: Mapped[int] = mappedColumn(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mappedColumn(String(255), unique=True, nullable=False, index=True)
    passwordHash: Mapped[str] = mappedColumn(String(255), nullable=False)
    isActive: Mapped[bool] = mappedColumn(Boolean, nullable=False, default=True)
    createdAt: Mapped[datetime] = mappedColumn(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
