import sys
import types

# Provide lightweight mocks for google.generativeai to avoid heavy protobuf imports during tests
google_mod = types.ModuleType("google")
genai_mod = types.ModuleType("google.generativeai")

class _DummyModel:
    def __init__(self, model_name=None):
        self.model_name = model_name

    def generate_content(self, prompts, stream=False):
        if stream:
            return []
        class R:
            text = '{"title":"Unit Test Fiche","yield_servings":2,"ingredients":[],"steps":[],"plating_notes":"","allergens":[]}'
        return R()

def _dummy_configure(api_key=None):
    return None

genai_mod.configure = _dummy_configure
genai_mod.GenerativeModel = _DummyModel
sys.modules['google'] = google_mod
sys.modules['google.generativeai'] = genai_mod

from fastapi.testclient import TestClient
import importlib

import backend.app.main as m
importlib.reload(m)

client = TestClient(m.app)


def get_token(role: str = "manager"):
    r = client.post('/auth/mock-token', json={'email': 'test@culina.ai', 'role': role})
    assert r.status_code == 200
    return r.json()['token']


def test_suppliers_import_and_catalog():
    token = get_token('manager')
    headers = {'Authorization': f'Bearer {token}'}
    payload: list[dict[str, str | float | int]] = [
        {'supplier_id': '1', 'supplier_name': 'UnitTest Supplier', 'product_name': 'UT Olive Oil', 'grade': 'A', 'unit': 'litre', 'unit_price': 9.99, 'lead_time_days': 2}
    ]
    r = client.post('/suppliers/import', json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json().get('ok') is True

    r2 = client.get('/suppliers/catalog')
    assert r2.status_code == 200
    names = [p.get('product_name') for p in r2.json()]
    assert 'UT Olive Oil' in names


def test_inventory_import_and_reorder():
    token = get_token('manager')
    headers = {'Authorization': f'Bearer {token}'}
    payload: list[dict[str, str | float | int]] = [
        {'sku': 'UT-OLIVE-1', 'name': 'UT Olive Oil', 'stock_qty': 5, 'reorder_point': 2, 'reserve_qty': 0, 'unit_price_per_kg': 9.99, 'supplier_id': '1'}
    ]
    r = client.post('/inventory/import', json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json().get('ok') is True

    r2 = client.post('/inventory/reorder', json=payload, headers=headers)
    assert r2.status_code == 200
    body = r2.json()
    assert 'order' in body and 'recommendations' in body
