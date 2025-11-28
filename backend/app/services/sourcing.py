from ..schemas import SourcingRequestItem, SourcingResponse, SourcingRecommendation, SupplierProduct
from ..data import suppliers


def _score(p: SupplierProduct) -> float:
    price = p.unit_price
    lead = p.lead_time_days
    sust = p.sustainability or 0.5
    return 0.5 * (1.0 / max(price, 0.01)) + 0.3 * (1.0 / max(lead, 1)) + 0.2 * sust


def _substitutions(name: str, dietary_tags: list[str]) -> list[SupplierProduct]:
    n = name.lower()
    tags = [t.lower() for t in (dietary_tags or [])]
    if any(t in tags for t in ["vegan", "vegetarian"]):
        if "beef" in n or "wagyu" in n:
            return suppliers.search("Parmigiano")
        if "chicken" in n:
            return suppliers.search("Matcha")
    return []


def recommend(items: list[SourcingRequestItem]) -> SourcingResponse:
    recs: list[SourcingRecommendation] = []
    for it in items:
        options = suppliers.search(it.name)
        if not options:
            # Fallback: fuzzy suggestions based on keywords
            key = it.name.lower()
            if "beef" in key:
                options = suppliers.search("Wagyu")
            elif "salmon" in key or "fish" in key:
                options = suppliers.search("Salmon")
            elif "matcha" in key or "tea" in key:
                options = suppliers.search("Matcha")
        options_sorted = sorted(options, key=lambda p: _score(p), reverse=True)[:3]
        note = None
        if any("Wagyu" in p.product_name for p in options_sorted):
            note = "Premium option available: Wagyu for elevated menu positioning"
        subs = _substitutions(it.name, it.dietary_tags or [])
        recs.append(SourcingRecommendation(request_name=it.name, top_options=options_sorted, note=note, substitutions=subs))
    return SourcingResponse(recommendations=recs)
