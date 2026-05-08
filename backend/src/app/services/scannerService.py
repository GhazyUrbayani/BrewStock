from __future__ import annotations

import asyncio
import base64
import time
from typing import Any

from app.models.scannerResultModel import (
    ScannerBoundingBox,
    ScannerDetectionResult,
    ScannerResult,
    SuggestedStockUpdate,
)


class ScannerService:
    modelInstance: ScannerService | None = None

    def __init__(
        self,
        modelPath: str,
        modelValue: Any | None = None,
        classToSkuMap: dict[str, str] | None = None,
    ) -> None:
        if modelValue is None:
            if modelPath == "":
                raise ValueError("Model path missing")
            from ultralytics import YOLO

            self.model = YOLO(modelPath)
        else:
            self.model = modelValue

        self.classToSkuMap = classToSkuMap or {
            "milk_bottle": "milk-full-cream",
            "syrup_bottle": "syrup-hazelnut",
            "coffee_bag": "coffee-arabica",
            "whipped_cream": "whipped-cream-can",
            "cup_stack": "cup-medium",
        }

    # Dibantu AI: getInstance
    @classmethod
    def getInstance(cls, modelPath: str) -> "ScannerService":
        if cls.modelInstance is None:
            cls.modelInstance = cls(modelPath)
        return cls.modelInstance

    # Dibantu AI: runDetection
    async def runDetection(self, imageBytes: bytes) -> ScannerResult:
        startTime = time.perf_counter()
        resultItems = await self.runModel(imageBytes)
        inferenceTimeMs = int((time.perf_counter() - startTime) * 1000)

        resultValue = resultItems[0] if resultItems else None
        detectionItems = self.readDetections(resultValue)
        totalItemsDetected = sum(itemValue.count for itemValue in detectionItems)
        annotatedImageBase64 = self.encodeAnnotatedImage(resultValue, imageBytes)
        suggestedStockUpdate = self.buildSuggestedStockUpdate(detectionItems)

        return ScannerResult(
            detections=detectionItems,
            totalItemsDetected=totalItemsDetected,
            annotatedImageBase64=annotatedImageBase64,
            inferenceTimeMs=inferenceTimeMs,
            suggestedStockUpdate=suggestedStockUpdate,
        )

    # Dibantu AI: runModel
    async def runModel(self, imageBytes: bytes) -> list[Any]:
        if hasattr(self.model, "predict"):
            return await asyncio.to_thread(self.model.predict, imageBytes, verbose=False)
        return await asyncio.to_thread(self.model, imageBytes)

    # Dibantu AI: readDetections
    def readDetections(self, resultValue: Any | None) -> list[ScannerDetectionResult]:
        if resultValue is None:
            return []

        namesValue = getattr(resultValue, "names", {})
        boxesValue = getattr(resultValue, "boxes", None)
        if boxesValue is None:
            return []

        xyxyItems = self.readList(boxesValue.xyxy)
        confItems = self.readList(boxesValue.conf)
        classItems = self.readList(boxesValue.cls)

        detectionMap: dict[str, ScannerDetectionResult] = {}
        for indexValue, boxValue in enumerate(xyxyItems):
            classIndex = int(classItems[indexValue]) if indexValue < len(classItems) else 0
            className = self.readClassName(namesValue, classIndex)
            confidenceValue = float(confItems[indexValue]) if indexValue < len(confItems) else 0.0
            x1, y1, x2, y2 = self.normalizeBox(boxValue)

            detectionValue = detectionMap.get(className)
            if detectionValue is None:
                detectionValue = ScannerDetectionResult(
                    className=className,
                    confidence=confidenceValue,
                    count=0,
                    boundingBoxes=[],
                )
                detectionMap[className] = detectionValue

            detectionValue.boundingBoxes.append(
                ScannerBoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
            )
            detectionValue.count += 1
            detectionValue.confidence = max(detectionValue.confidence, confidenceValue)

        return list(detectionMap.values())

    # Dibantu AI: buildSuggestedStockUpdate
    def buildSuggestedStockUpdate(
        self,
        detectionItems: list[ScannerDetectionResult],
    ) -> list[SuggestedStockUpdate]:
        suggestedItems: list[SuggestedStockUpdate] = []
        for itemValue in detectionItems:
            skuId = self.classToSkuMap.get(itemValue.className)
            if skuId:
                suggestedItems.append(
                    SuggestedStockUpdate(
                        skuId=skuId,
                        detectedCount=itemValue.count,
                    )
                )
        return suggestedItems

    # Dibantu AI: encodeAnnotatedImage
    def encodeAnnotatedImage(self, resultValue: Any | None, fallbackBytes: bytes) -> str:
        if resultValue is not None and hasattr(resultValue, "plot"):
            try:
                annotatedValue = resultValue.plot()
                encodedValue = self.encodeImageValue(annotatedValue)
                if encodedValue:
                    return encodedValue
            except Exception:
                pass

        return self.encodeImageValue(fallbackBytes)

    # Dibantu AI: encodeImageValue
    def encodeImageValue(self, imageValue: Any) -> str:
        if isinstance(imageValue, (bytes, bytearray)):
            rawBytes = bytes(imageValue)
        else:
            try:
                from PIL import Image
                import io

                imageObject = Image.fromarray(imageValue)
                bufferValue = io.BytesIO()
                imageObject.save(bufferValue, format="JPEG")
                rawBytes = bufferValue.getvalue()
            except Exception:
                return ""

        encodedValue = base64.b64encode(rawBytes).decode("ascii")
        return f"data:image/jpeg;base64,{encodedValue}"

    # Dibantu AI: readList
    def readList(self, inputValue: Any) -> list[Any]:
        if hasattr(inputValue, "tolist"):
            return list(inputValue.tolist())
        return list(inputValue)

    # Dibantu AI: normalizeBox
    def normalizeBox(self, boxValue: Any) -> tuple[float, float, float, float]:
        boxItems = self.readList(boxValue)
        if len(boxItems) < 4:
            return 0.0, 0.0, 0.0, 0.0
        return (
            float(boxItems[0]),
            float(boxItems[1]),
            float(boxItems[2]),
            float(boxItems[3]),
        )

    # Dibantu AI: readClassName
    def readClassName(self, namesValue: Any, classIndex: int) -> str:
        if isinstance(namesValue, dict):
            return str(namesValue.get(classIndex, classIndex))
        if isinstance(namesValue, list) and classIndex < len(namesValue):
            return str(namesValue[classIndex])
        return str(classIndex)
