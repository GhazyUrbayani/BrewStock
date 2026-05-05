from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column as mappedColumn

from app.core.database import baseModel


class RefreshTokenRecord(baseModel):
    __tablename__ = "refreshTokenRecord"

    id: Mapped[int] = mappedColumn(Integer, primary_key=True, autoincrement=True)
    tokenId: Mapped[str] = mappedColumn(String(128), unique=True, nullable=False, index=True)
    tokenHash: Mapped[str] = mappedColumn(String(255), nullable=False, unique=True, index=True)
    userId: Mapped[int] = mappedColumn(ForeignKey("userAccount.id"), nullable=False, index=True)
    revokedAt: Mapped[datetime | None] = mappedColumn(DateTime(timezone=True), nullable=True)
    expiresAt: Mapped[datetime] = mappedColumn(DateTime(timezone=True), nullable=False)
    createdAt: Mapped[datetime] = mappedColumn(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
