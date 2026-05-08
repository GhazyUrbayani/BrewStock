from __future__ import annotations

from pydantic import Field

from app.schemas.baseSchema import SanitizedModel


class StockItemInput(SanitizedModel):
    skuId: str = Field(min_length=1, max_length=64)
    availableQuantity: float = Field(ge=0)


class MenuAvailabilityRequest(SanitizedModel):
    stockItems: list[StockItemInput] = Field(default_factory=list)


class MenuIngredientStatus(SanitizedModel):
    skuId: str
    requiredQuantity: float
    availableQuantity: float
    isEnough: bool


class MenuItemAvailability(SanitizedModel):
    menuId: str
    menuName: str
    isAvailable: bool
    maxServings: int = Field(ge=0)
    ingredientStatuses: list[MenuIngredientStatus]


class MenuAvailabilityResponse(SanitizedModel):
    menuItems: list[MenuItemAvailability]
    totalAvailable: int = Field(ge=0)
