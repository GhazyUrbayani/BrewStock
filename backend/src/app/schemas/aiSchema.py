from __future__ import annotations

from pydantic import Field

from app.schemas.baseSchema import SanitizedModel


class InsightRequest(SanitizedModel):
    message: str = Field(min_length=1, max_length=500)


class InsightResponse(SanitizedModel):
    insight: str
