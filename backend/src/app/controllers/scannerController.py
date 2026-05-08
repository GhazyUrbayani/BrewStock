from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.scannerSchema import (
    ScannerBoundingBoxOutput,
    ScannerDetectionOutput,
    ScannerResponse,
    ScannerSuggestedStockUpdate,
)
from app.services.scannerService import ScannerService


class ScannerController:
    def __init__(
        self,
        scannerService: ScannerService,
    ) -> None:
        self.scannerService = scannerService

    # dibantu AI: detectStock
    async def detectStock(
        self,
        imageBytes: bytes,
        contentType: str | None,
    ) -> ScannerResponse:
        if imageBytes == b"":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image missing",
            )

        maxSizeBytes = 10 * 1024 * 1024
        if len(imageBytes) > maxSizeBytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image too large",
            )

        allowedMimeItems = {"image/jpeg", "image/png", "image/webp"}
        if contentType is not None and contentType not in allowedMimeItems:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )

        allowedTypes = {"jpeg", "png", "webp"}
        detectedType = self.readImageType(imageBytes)
        if detectedType not in allowedTypes:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )

        resultValue = await self.scannerService.runDetection(imageBytes)

        return ScannerResponse(
            detections=[
                ScannerDetectionOutput(
                    className=itemValue.className,
                    confidence=itemValue.confidence,
                    count=itemValue.count,
                    boundingBoxes=[
                        ScannerBoundingBoxOutput(
                            x1=boxValue.x1,
                            y1=boxValue.y1,
                            x2=boxValue.x2,
                            y2=boxValue.y2,
                        )
                        for boxValue in itemValue.boundingBoxes
                    ],
                )
                for itemValue in resultValue.detections
            ],
            totalItemsDetected=resultValue.totalItemsDetected,
            annotatedImageBase64=resultValue.annotatedImageBase64,
            inferenceTimeMs=resultValue.inferenceTimeMs,
            suggestedStockUpdate=[
                ScannerSuggestedStockUpdate(
                    skuId=itemValue.skuId,
                    detectedCount=itemValue.detectedCount,
                )
                for itemValue in resultValue.suggestedStockUpdate
            ],
        )

    # dibantu AI: readImageType
    def readImageType(self, imageBytes: bytes) -> str | None:
        if imageBytes.startswith(b"\xff\xd8\xff"):
            return "jpeg"
        if imageBytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "png"
        if imageBytes.startswith(b"RIFF") and imageBytes[8:12] == b"WEBP":
            return "webp"
        return None
