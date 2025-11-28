from ..schemas import SupplierProduct


CATALOG: list[SupplierProduct] = [
    SupplierProduct(supplier_id="SUP1", supplier_name="Nordic Seafoods", product_name="Atlantic Salmon Fillet", grade="AAA", unit="kg", unit_price=22.0, lead_time_days=2),
    SupplierProduct(supplier_id="SUP2", supplier_name="Kyoto Wagyu Co.", product_name="Wagyu A5 Striploin", grade="A5", unit="kg", unit_price=180.0, lead_time_days=5),
    SupplierProduct(supplier_id="SUP3", supplier_name="Green Valley Farms", product_name="Free-Range Chicken Breast", grade="Prime", unit="kg", unit_price=14.5, lead_time_days=3),
    SupplierProduct(supplier_id="SUP4", supplier_name="Matcha Masters", product_name="Ceremonial Grade Matcha", grade="Ceremonial", unit="100g", unit_price=28.0, lead_time_days=7),
    SupplierProduct(supplier_id="SUP5", supplier_name="Italian Pantry", product_name="Parmigiano Reggiano 24m", grade="DOP", unit="kg", unit_price=32.0, lead_time_days=4),
]


def search(term: str) -> list[SupplierProduct]:
    t = term.lower()
    return [p for p in CATALOG if t in p.product_name.lower()]
