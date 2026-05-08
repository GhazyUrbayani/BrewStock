from __future__ import annotations

from pydantic import Field

from app.schemas.baseSchema import SanitizedModel


class ScannerBoundingBoxOutput(SanitizedModel):
    x1: float
    y1: float
    x2: float
    y2: float


class ScannerDetectionOutput(SanitizedModel):
    className: str
    confidence: float = Field(ge=0, le=1)
    count: int = Field(ge=0)
    boundingBoxes: list[ScannerBoundingBoxOutput]


class ScannerSuggestedStockUpdate(SanitizedModel):
    skuId: str
    detectedCount: int = Field(ge=0)


class ScannerResponse(SanitizedModel):
    detections: list[ScannerDetectionOutput]
    totalItemsDetected: int = Field(ge=0)
    annotatedImageBase64: str
    inferenceTimeMs: int = Field(ge=0)
    suggestedStockUpdate: list[ScannerSuggestedStockUpdate]
