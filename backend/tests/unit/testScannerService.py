from __future__ import annotations

import base64
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.controllers.scannerController import ScannerController
from app.models.scannerResultModel import (
    ScannerBoundingBox,
    ScannerDetectionResult,
    ScannerResult,
    SuggestedStockUpdate,
)
from app.schemas.inventorySchema import StockUpdateResponse
from app.services.scannerService import ScannerService


class FakeBoxes:
    def __init__(self, clsItems: list[int], confItems: list[float], xyxyItems: list[list[float]]) -> None:
        self.cls = clsItems
        self.conf = confItems
        self.xyxy = xyxyItems


class FakeResult:
    def __init__(self) -> None:
        self.names = {0: "milk_bottle", 1: "coffee_bag"}
        self.boxes = FakeBoxes(
            clsItems=[0, 0, 1],
            confItems=[0.91, 0.82, 0.74],
            xyxyItems=[
                [10, 12, 40, 48],
                [60, 70, 90, 100],
                [110, 120, 150, 160],
            ],
        )

    def plot(self) -> bytes:
        return b"fake-image"


class FakeModel:
    def __init__(self, resultValue: FakeResult) -> None:
        self.resultValue = resultValue

    def predict(self, imageBytes: bytes, verbose: bool = False):
        return [self.resultValue]


class FakeScannerService:
    async def runDetection(self, imageBytes: bytes) -> ScannerResult:
        return ScannerResult(
            detections=[
                ScannerDetectionResult(
                    className="milk_bottle",
                    confidence=0.91,
                    count=2,
                    boundingBoxes=[ScannerBoundingBox(x1=10, y1=12, x2=40, y2=48)],
                )
            ],
            totalItemsDetected=2,
            annotatedImageBase64="data:image/jpeg;base64,ZmFrZQ==",
            inferenceTimeMs=28,
            suggestedStockUpdate=[SuggestedStockUpdate(skuId="milk-full-cream", detectedCount=2)],
        )


class FakeInventoryService:
    def __init__(self) -> None:
        self.updateItems: list[tuple[str, float]] = []

    async def updateCurrentStock(self, skuId: str, requestValue):
        self.updateItems.append((skuId, float(requestValue.currentStock)))
        return StockUpdateResponse(
            skuId=skuId,
            currentStock=float(requestValue.currentStock),
            updatedAt=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
# Dibantu AI: testRunDetectionBuildsSummary
async def testRunDetectionBuildsSummary() -> None:
    serviceValue = ScannerService(
        modelPath="unused",
        modelValue=FakeModel(FakeResult()),
    )

    resultValue = await serviceValue.runDetection(b"\x89PNG\r\n\x1a\n")

    assert resultValue.totalItemsDetected == 3
    assert resultValue.detections[0].className == "milk_bottle"
    assert resultValue.detections[0].count == 2
    assert resultValue.suggestedStockUpdate[0].skuId == "milk-full-cream"

    encodedValue = base64.b64encode(b"fake-image").decode("ascii")
    assert encodedValue in resultValue.annotatedImageBase64


@pytest.mark.asyncio
# Dibantu AI: testDetectStockRejectsInvalidType
async def testDetectStockRejectsInvalidType() -> None:
    controllerValue = ScannerController(FakeScannerService())

    with pytest.raises(HTTPException) as errorInfo:
        await controllerValue.detectStock(imageBytes=b"not-image", contentType="text/plain")

    assert errorInfo.value.status_code == 415


@pytest.mark.asyncio
# Dibantu AI: testDetectStockReturnsResponse
async def testDetectStockReturnsResponse() -> None:
    controllerValue = ScannerController(FakeScannerService())
    imageBytes = b"\x89PNG\r\n\x1a\n" + b"0" * 40

    resultValue = await controllerValue.detectStock(imageBytes=imageBytes, contentType="image/png")

    assert resultValue.totalItemsDetected == 2
    assert resultValue.suggestedStockUpdate[0].detectedCount == 2


@pytest.mark.asyncio
# Dibantu AI: testDetectStockAppliesStockUpdate
async def testDetectStockAppliesStockUpdate() -> None:
    inventoryService = FakeInventoryService()
    controllerValue = ScannerController(
        scannerService=FakeScannerService(),
        inventoryService=inventoryService,
    )
    imageBytes = b"\x89PNG\r\n\x1a\n" + b"0" * 40

    await controllerValue.detectStock(
        imageBytes=imageBytes,
        contentType="image/png",
        applyStockUpdate=True,
    )

    assert inventoryService.updateItems == [("milk-full-cream", 2.0)]


@pytest.mark.asyncio
# Dibantu AI: testDetectStockApplyRequiresInventoryService
async def testDetectStockApplyRequiresInventoryService() -> None:
    controllerValue = ScannerController(FakeScannerService())
    imageBytes = b"\x89PNG\r\n\x1a\n" + b"0" * 40

    with pytest.raises(HTTPException) as errorInfo:
        await controllerValue.detectStock(
            imageBytes=imageBytes,
            contentType="image/png",
            applyStockUpdate=True,
        )

    assert errorInfo.value.status_code == 503
