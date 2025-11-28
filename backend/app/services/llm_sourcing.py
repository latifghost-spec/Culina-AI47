import json
import re
import google.generativeai as genai
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from .. import schemas


def _extract_json(text: str) -> dict:
    s = text.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"^```\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    return json.loads(s)


def suggest_suppliers(prompt: str) -> schemas.SupplierLLMSuggestionsResponse:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    sys = "Return ONLY JSON { suggestions: [{ name, note, confidence }] }"
    resp = model.generate_content([sys, prompt])
    data = _extract_json(resp.text)
    items = []
    for s in data.get("suggestions", []):
        items.append(schemas.SupplierLLMSuggestion(name=s.get("name", ""), note=s.get("note", ""), confidence=float(s.get("confidence", 0.5))))
    return schemas.SupplierLLMSuggestionsResponse(suggestions=items)
