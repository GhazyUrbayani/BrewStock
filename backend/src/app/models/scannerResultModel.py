from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScannerBoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(slots=True)
class ScannerDetectionResult:
    className: str
    confidence: float
    count: int
    boundingBoxes: list[ScannerBoundingBox]


@dataclass(slots=True)
class SuggestedStockUpdate:
    skuId: str
    detectedCount: int


@dataclass(slots=True)
class ScannerResult:
    detections: list[ScannerDetectionResult]
    totalItemsDetected: int
    annotatedImageBase64: str
    inferenceTimeMs: int
    suggestedStockUpdate: list[SuggestedStockUpdate]
