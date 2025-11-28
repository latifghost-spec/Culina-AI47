import json
import re
import time
from typing import List, Iterable
import google.generativeai as genai
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from .. import schemas


def _extract_json(text: str) -> dict:
    s = text.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"^```\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    return json.loads(s)


def _validate_fiche_dict(data: dict, prompt: str, servings: int, excluded_allergens: List[str]) -> schemas.FicheTechnique:
    ingredients = [schemas.FicheIngredient(**ing) for ing in data.get("ingredients", [])]
    return schemas.FicheTechnique(
        title=data.get("title", prompt.title()[:80]),
        yield_servings=data.get("yield_servings", servings),
        ingredients=ingredients,
        steps=data.get("steps", []),
        plating_notes=data.get("plating_notes", ""),
        allergens=data.get("allergens", excluded_allergens),
    )


def generate_fiche_llm(prompt: str, servings: int, excluded_allergens: List[str], dietary_tags: List[str]) -> schemas.FicheTechnique:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    sys = (
        "You are a Michelin-level chef assistant. Return ONLY JSON with keys: "
        "title, yield_servings, ingredients, steps, plating_notes, allergens. "
        "ingredients is a list of {name, quantity_g}."
    )
    user = (
        f"Prompt: {prompt}. Servings: {servings}. Dietary tags: {', '.join(dietary_tags)}. "
        f"Exclude allergens: {', '.join(excluded_allergens)}."
    )
    last_err = None
    for attempt in range(3):
        try:
            resp = model.generate_content([sys, user])
            data = _extract_json(resp.text)
            return _validate_fiche_dict(data, prompt, servings, excluded_allergens)
        except Exception as e:
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    # Fallback template
    return schemas.FicheTechnique(
        title=prompt.title()[:80],
        yield_servings=servings,
        ingredients=[schemas.FicheIngredient(name="Chef selection", quantity_g=150.0)],
        steps=["Prep", "Cook", "Plate"],
        plating_notes="",
        allergens=excluded_allergens,
    )


def stream_generate_fiche_llm(prompt: str, servings: int, excluded_allergens: List[str], dietary_tags: List[str]) -> Iterable[str]:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    sys = (
        "Return ONLY JSON with keys: title, yield_servings, ingredients[{name,quantity_g}], steps, plating_notes, allergens."
    )
    user = (
        f"Prompt: {prompt}. Servings: {servings}. Dietary tags: {', '.join(dietary_tags)}. "
        f"Exclude allergens: {', '.join(excluded_allergens)}."
    )
    for attempt in range(3):
        try:
            stream = model.generate_content([sys, user], stream=True)
            buffer = ""
            for chunk in stream:
                text = getattr(chunk, "text", "")
                if not text:
                    continue
                buffer += text
                yield f"data: {text}\n\n"
            # At end, yield validated summary block
            try:
                data = _extract_json(buffer)
                _validate_fiche_dict(data, prompt, servings, excluded_allergens)
                yield "event: end\n" + "data: VALID\n\n"
            except Exception:
                yield "event: end\n" + "data: INVALID_JSON\n\n"
            return
        except Exception:
            time.sleep(0.8 * (attempt + 1))
    yield "event: error\n" + "data: RETRY_FAILED\n\n"
