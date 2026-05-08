from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.controllers.scannerController import ScannerController
from app.core.dependencies import getScannerController, readCurrentUserId
from app.core.rateLimit import enforceRateLimit, enforceScannerRateLimit
from app.schemas.scannerSchema import ScannerResponse

scannerRouter = APIRouter(prefix="/api/v1/scanner", tags=["scanner"])


# dibantu AI: enforceScannerLimit
async def enforceScannerLimit(
    userId: int = Depends(readCurrentUserId),
) -> None:
    await enforceScannerRateLimit(userId)


@scannerRouter.post(
    "/detect",
    response_model=ScannerResponse,
    dependencies=[Depends(enforceRateLimit), Depends(enforceScannerLimit)],
)
# dibantu AI: detectStock
async def detectStock(
    image: UploadFile = File(...),
    controllerValue: ScannerController = Depends(getScannerController),
) -> ScannerResponse:
    imageBytes = await image.read()
    return await controllerValue.detectStock(
        imageBytes=imageBytes,
        contentType=image.content_type,
    )
