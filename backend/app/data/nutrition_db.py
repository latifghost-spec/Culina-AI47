from ..schemas import MacroProfile


NUTRITION: dict[str, MacroProfile] = {
    "salmon": MacroProfile(calories_per_100g=208.0, protein_g_per_100g=20.4, fat_g_per_100g=13.4, carbs_g_per_100g=0.0),
    "chicken breast": MacroProfile(calories_per_100g=165.0, protein_g_per_100g=31.0, fat_g_per_100g=3.6, carbs_g_per_100g=0.0),
    "wagyu": MacroProfile(calories_per_100g=350.0, protein_g_per_100g=23.0, fat_g_per_100g=28.0, carbs_g_per_100g=0.0),
    "matcha": MacroProfile(calories_per_100g=324.0, protein_g_per_100g=29.0, fat_g_per_100g=5.0, carbs_g_per_100g=38.0),
    "parmigiano": MacroProfile(calories_per_100g=431.0, protein_g_per_100g=38.0, fat_g_per_100g=29.0, carbs_g_per_100g=4.1),
}


def lookup(name: str) -> MacroProfile | None:
    key = name.lower()
    for k, v in NUTRITION.items():
        if k in key:
            return v
    return None
