from .. import schemas
from urllib.parse import quote_plus


def generate_fiche(prompt: str, servings: int, excluded_allergens: list[str] | None = None) -> schemas.FicheTechnique:
    title = prompt.title()[:80]
    base_ing = [
        schemas.FicheIngredient(name="Main Protein", quantity_g=180.0),
        schemas.FicheIngredient(name="Sauce", quantity_g=60.0),
        schemas.FicheIngredient(name="Garnish", quantity_g=80.0),
    ]
    steps = [
        "Prep ingredients",
        "Cook protein",
        "Prepare sauce",
        "Plate with garnish",
    ]
    allergens = [] if not excluded_allergens else excluded_allergens
    return schemas.FicheTechnique(
        title=title,
        yield_servings=servings,
        ingredients=base_ing,
        steps=steps,
        plating_notes="Fine dining plating with vertical elements",
        allergens=allergens,
    )


def suggest_videos(prompt: str) -> schemas.VideoResponse:
    q = quote_plus(prompt)
    urls = [
        f"https://www.youtube.com/results?search_query={q}+fine+dining",
        f"https://www.youtube.com/results?search_query={q}+plating",
        f"https://www.youtube.com/results?search_query={q}+culinary+techniques",
    ]
    return schemas.VideoResponse(prompt=prompt, video_urls=urls)
