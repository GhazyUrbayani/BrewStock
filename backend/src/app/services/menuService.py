from __future__ import annotations

from dataclasses import dataclass
import math

from app.schemas.menuSchema import (
    MenuAvailabilityRequest,
    MenuAvailabilityResponse,
    MenuIngredientStatus,
    MenuItemAvailability,
)


@dataclass(slots=True)
class MenuRecipe:
    menuId: str
    menuName: str
    recipeItems: dict[str, float]


class MenuService:
    def __init__(self, recipeItems: list[MenuRecipe] | None = None) -> None:
        self.recipeItems = recipeItems or self.buildDefaultRecipes()

    # dibantu AI: buildDefaultRecipes
    def buildDefaultRecipes(self) -> list[MenuRecipe]:
        return [
            MenuRecipe(
                menuId="caffe-latte",
                menuName="Caffe Latte",
                recipeItems={
                    "arabica-beans": 1,
                    "fresh-milk": 2,
                },
            ),
            MenuRecipe(
                menuId="espresso",
                menuName="Espresso",
                recipeItems={
                    "arabica-beans": 1,
                },
            ),
            MenuRecipe(
                menuId="caffe-mocha",
                menuName="Caffe Mocha",
                recipeItems={
                    "arabica-beans": 1,
                    "fresh-milk": 1,
                    "chocolate-sauce": 1,
                },
            ),
            MenuRecipe(
                menuId="americano",
                menuName="Americano",
                recipeItems={
                    "arabica-beans": 1,
                    "filtered-water": 2,
                },
            ),
        ]

    # dibantu AI: buildMenuAvailability
    async def buildMenuAvailability(
        self,
        requestValue: MenuAvailabilityRequest,
    ) -> MenuAvailabilityResponse:
        stockMap = {
            itemValue.skuId: float(itemValue.availableQuantity)
            for itemValue in requestValue.stockItems
        }

        menuItems: list[MenuItemAvailability] = []
        for recipeValue in self.recipeItems:
            ingredientStatuses: list[MenuIngredientStatus] = []
            servingCandidates: list[float] = []

            for skuId, requiredQuantity in recipeValue.recipeItems.items():
                if requiredQuantity <= 0:
                    raise ValueError("Recipe quantity invalid")

                availableQuantity = float(stockMap.get(skuId, 0))
                isEnough = availableQuantity >= requiredQuantity
                ingredientStatuses.append(
                    MenuIngredientStatus(
                        skuId=skuId,
                        requiredQuantity=requiredQuantity,
                        availableQuantity=availableQuantity,
                        isEnough=isEnough,
                    )
                )
                servingCandidates.append(availableQuantity / requiredQuantity)

            maxServings = 0
            if servingCandidates:
                maxServings = int(math.floor(min(servingCandidates)))

            isAvailable = all(itemValue.isEnough for itemValue in ingredientStatuses)
            menuItems.append(
                MenuItemAvailability(
                    menuId=recipeValue.menuId,
                    menuName=recipeValue.menuName,
                    isAvailable=isAvailable,
                    maxServings=max(0, maxServings),
                    ingredientStatuses=ingredientStatuses,
                )
            )

        totalAvailable = len([itemValue for itemValue in menuItems if itemValue.isAvailable])
        return MenuAvailabilityResponse(menuItems=menuItems, totalAvailable=totalAvailable)
