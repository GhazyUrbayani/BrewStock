from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column as mappedColumn

from app.core.database import baseModel


class StockItem(baseModel):
    __tablename__ = "stockItem"

    skuId: Mapped[str] = mappedColumn(String(64), primary_key=True)
    currentStock: Mapped[float] = mappedColumn(Float, nullable=False, default=0)
    updatedAt: Mapped[datetime] = mappedColumn(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
