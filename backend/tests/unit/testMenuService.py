from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.controllers.menuController import MenuController
from app.schemas.menuSchema import MenuAvailabilityRequest, StockItemInput
from app.services.menuService import MenuRecipe, MenuService


@pytest.mark.asyncio
# dibantu AI: testBuildMenuAvailabilityAllAvailable
async def testBuildMenuAvailabilityAllAvailable() -> None:
    recipeItems = [
        MenuRecipe(
            menuId="latte",
            menuName="Latte",
            recipeItems={
                "espresso-shot": 1,
                "fresh-milk": 2,
            },
        ),
        MenuRecipe(
            menuId="americano",
            menuName="Americano",
            recipeItems={
                "espresso-shot": 1,
                "filtered-water": 3,
            },
        ),
    ]
    serviceValue = MenuService(recipeItems=recipeItems)

    requestValue = MenuAvailabilityRequest(
        stockItems=[
            StockItemInput(skuId="espresso-shot", availableQuantity=3),
            StockItemInput(skuId="fresh-milk", availableQuantity=4),
            StockItemInput(skuId="filtered-water", availableQuantity=10),
        ]
    )

    resultValue = await serviceValue.buildMenuAvailability(requestValue)
    assert resultValue.totalAvailable == 2

    latteValue = next(itemValue for itemValue in resultValue.menuItems if itemValue.menuId == "latte")
    assert latteValue.isAvailable is True
    assert latteValue.maxServings == 2

    americanoValue = next(itemValue for itemValue in resultValue.menuItems if itemValue.menuId == "americano")
    assert americanoValue.isAvailable is True
    assert americanoValue.maxServings == 3


@pytest.mark.asyncio
# dibantu AI: testBuildMenuAvailabilityMissingIngredient
async def testBuildMenuAvailabilityMissingIngredient() -> None:
    recipeItems = [
        MenuRecipe(
            menuId="mocha",
            menuName="Mocha",
            recipeItems={
                "espresso-shot": 1,
                "chocolate-sauce": 1,
            },
        )
    ]
    serviceValue = MenuService(recipeItems=recipeItems)

    requestValue = MenuAvailabilityRequest(
        stockItems=[
            StockItemInput(skuId="espresso-shot", availableQuantity=1),
        ]
    )

    resultValue = await serviceValue.buildMenuAvailability(requestValue)
    mochaValue = resultValue.menuItems[0]

    assert mochaValue.isAvailable is False
    assert mochaValue.maxServings == 0
    chocolateValue = next(
        itemValue for itemValue in mochaValue.ingredientStatuses if itemValue.skuId == "chocolate-sauce"
    )
    assert chocolateValue.availableQuantity == 0
    assert chocolateValue.isEnough is False


class FakeMenuService:
    async def buildMenuAvailability(self, requestValue: MenuAvailabilityRequest):
        raise ValueError("Invalid")


@pytest.mark.asyncio
# dibantu AI: testMenuControllerHandlesError
async def testMenuControllerHandlesError() -> None:
    controllerValue = MenuController(FakeMenuService())

    with pytest.raises(HTTPException) as errorInfo:
        await controllerValue.listAvailability(MenuAvailabilityRequest(stockItems=[]))

    assert errorInfo.value.status_code == 400
