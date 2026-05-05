from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column as mappedColumn

from app.core.database import baseModel


class TransactionRecord(baseModel):
    __tablename__ = "transactionRecord"
    __table_args__ = (Index("idxTransactionDateSkuId", "transactionDate", "skuId"),)

    id: Mapped[int] = mappedColumn(Integer, primary_key=True, autoincrement=True)
    skuId: Mapped[str] = mappedColumn(String(64), nullable=False, index=True)
    transactionDate: Mapped[date] = mappedColumn(Date, nullable=False)
    demandQuantity: Mapped[float] = mappedColumn(Float, nullable=False)
    createdAt: Mapped[datetime] = mappedColumn(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
