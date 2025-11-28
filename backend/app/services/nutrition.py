from .. import schemas
from ..data import nutrition_db


def _calories_from_macros(profile: schemas.MacroProfile) -> float:
    p = profile.protein_g_per_100g or 0.0
    f = profile.fat_g_per_100g or 0.0
    c = profile.carbs_g_per_100g or 0.0
    return 4.0 * p + 9.0 * f + 4.0 * c


def calculate_totals(ingredients: list[schemas.IngredientInput]) -> schemas.NutritionSummary:
    calories = 0.0
    protein = 0.0
    fat = 0.0
    carbs = 0.0
    for ing in ingredients:
        qty = ing.quantity_g
        profile = ing.macro_profile or nutrition_db.lookup(ing.name)
        if profile:
            cal100 = profile.calories_per_100g if profile.calories_per_100g is not None else _calories_from_macros(profile)
            p100 = profile.protein_g_per_100g or 0.0
            f100 = profile.fat_g_per_100g or 0.0
            c100 = profile.carbs_g_per_100g or 0.0
            calories += cal100 * qty / 100.0
            protein += p100 * qty / 100.0
            fat += f100 * qty / 100.0
            carbs += c100 * qty / 100.0
    return schemas.NutritionSummary(calories=round(calories, 2), protein_g=round(protein, 2), fat_g=round(fat, 2), carbs_g=round(carbs, 2))


def per_serving(total: schemas.NutritionSummary, servings: int) -> schemas.NutritionSummary:
    s = max(servings, 1)
    return schemas.NutritionSummary(
        calories=round(total.calories / s, 2),
        protein_g=round(total.protein_g / s, 2),
        fat_g=round(total.fat_g / s, 2),
        carbs_g=round(total.carbs_g / s, 2),
    )
