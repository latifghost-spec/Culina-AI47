from .. import schemas


def food_cost(ingredients: list[schemas.IngredientInput]) -> float:
    total = 0.0
    for ing in ingredients:
        unit = ing.unit_price_per_kg or 0.0
        waste = ing.waste_pct or 0.0
        effective_g = ing.quantity_g * (1.0 + waste)
        total += (effective_g / 1000.0) * unit
    return round(total, 2)


def food_cost_per_serving(ingredients: list[schemas.IngredientInput], servings: int) -> float:
    total = food_cost(ingredients)
    s = max(servings, 1)
    return round(total / s, 2)


def suggest_price(food_cost_per_serving_value: float, target_cost_pct: float) -> float:
    pct = max(min(target_cost_pct, 0.95), 0.01)
    return round(food_cost_per_serving_value / pct, 2)
