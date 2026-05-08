from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.core import dependencies
from app.controllers.inventoryController import InventoryController
from app.controllers.scannerController import ScannerController


@dataclass(slots=True)
class FakeSettings:
    yoloModelPath: str


@pytest.mark.asyncio
# Dibantu AI: testGetInventoryControllerBuildsStockRepository
async def testGetInventoryControllerBuildsStockRepository() -> None:
    sessionValue = object()

    controllerValue = await dependencies.getInventoryController(sessionValue=sessionValue)

    assert isinstance(controllerValue, InventoryController)
    assert controllerValue.inventoryService.stockRepository is not None


@pytest.mark.asyncio
# Dibantu AI: testGetScannerControllerUsesModelPath
async def testGetScannerControllerUsesModelPath(monkeypatch) -> None:
    expectedService = object()
    captureMap: dict[str, str] = {}

    def fakeLoadSettings() -> FakeSettings:
        return FakeSettings(yoloModelPath="/tmp/custom.pt")

    @classmethod
    def fakeGetInstance(cls, modelPath: str):
        captureMap["modelPath"] = modelPath
        return expectedService

    monkeypatch.setattr(dependencies, "loadSettings", fakeLoadSettings)
    monkeypatch.setattr(dependencies.ScannerService, "getInstance", fakeGetInstance)

    controllerValue = await dependencies.getScannerController(sessionValue=object())

    assert isinstance(controllerValue, ScannerController)
    assert controllerValue.scannerService is expectedService
    assert controllerValue.inventoryService is not None
    assert captureMap["modelPath"] == "/tmp/custom.pt"
