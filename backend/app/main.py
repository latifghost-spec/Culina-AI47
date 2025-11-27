from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import schemas
from .services import nutrition, costing, inventory, ideation, business
from .services import sourcing
from .services.llm import generate_fiche_llm, stream_generate_fiche_llm
from .services.llm_sourcing import suggest_suppliers
from fastapi.responses import StreamingResponse
from .db import Base, engine, SessionLocal
from . import models
from fastapi import Depends, UploadFile, File
from .auth import require_jwt_role, issue_mock_token, require_jwt_role_dep


app = FastAPI(title="CulinaAI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/calc/nutrition", response_model=schemas.NutritionResponse)
def calc_nutrition(ingredients: list[schemas.IngredientInput], servings: int = 1):
    total = nutrition.calculate_totals(ingredients)
    per = nutrition.per_serving(total, servings)
    return schemas.NutritionResponse(total=total, per_serving=per)


@app.post("/calc/costing", response_model=schemas.CostingResponse)
def calc_costing(ingredients: list[schemas.IngredientInput], servings: int = 1, target_cost_pct: float = 0.3):
    total = costing.food_cost(ingredients)
    per = costing.food_cost_per_serving(ingredients, servings)
    price = costing.suggest_price(per, target_cost_pct)
    return schemas.CostingResponse(food_cost_total=total, food_cost_per_serving=per, suggested_price=price)


@app.post("/inventory/evaluate", response_model=schemas.InventoryResponse)
def inventory_evaluate(items: list[schemas.InventoryItem]):
    return inventory.evaluate(items)


@app.get("/inspiration/videos", response_model=schemas.VideoResponse)
def inspiration_videos(prompt: str):
    return ideation.suggest_videos(prompt)


@app.post("/chef/ideate", response_model=schemas.FicheTechnique)
def chef_ideate(req: schemas.RecipeIdeaRequest):
    fiche = (
        generate_fiche_llm(req.prompt, req.servings, req.excluded_allergens or [], req.dietary_tags or [])
        if req.use_llm
        else ideation.generate_fiche(req.prompt, req.servings, req.excluded_allergens or [])
    )
    ing_inputs = [
        schemas.IngredientInput(name=i.name, quantity_g=i.quantity_g) for i in fiche.ingredients
    ]
    total = nutrition.calculate_totals(ing_inputs)
    per = nutrition.per_serving(total, req.servings)
    fiche.nutrition_per_serving = per
    cost_per = costing.food_cost_per_serving(ing_inputs, req.servings)
    fiche.food_cost_per_serving = cost_per
    fiche.suggested_price = costing.suggest_price(cost_per, req.target_cost_pct)
    return fiche


@app.get("/chef/ideate/stream")
def chef_ideate_stream(prompt: str, servings: int = 2, excluded_allergens: str = "", dietary_tags: str = ""):
    excl = [a.strip() for a in excluded_allergens.split(",") if a.strip()]
    tags = [t.strip() for t in dietary_tags.split(",") if t.strip()]
    gen = stream_generate_fiche_llm(prompt, servings, excl, tags)
    return StreamingResponse(gen, media_type="text/event-stream")


@app.post("/business/plan", response_model=schemas.BusinessPlanOutput)
def business_plan(input: schemas.BusinessPlanInput):
    return business.plan(input)
@app.get("/suppliers/catalog", response_model=list[schemas.SupplierProduct])
def suppliers_catalog():
    db = SessionLocal()
    rows = db.query(models.SupplierProduct).all()
    if not rows:
        from .data.suppliers import CATALOG as seed
        for p in seed:
            db.add(models.SupplierProduct(supplier_id=0, supplier_name=p.supplier_name, product_name=p.product_name, grade=p.grade, unit=p.unit, unit_price=p.unit_price, lead_time_days=p.lead_time_days))
        db.commit()
        rows = db.query(models.SupplierProduct).all()
    return [schemas.SupplierProduct(supplier_id=str(r.supplier_id), supplier_name=r.supplier_name, product_name=r.product_name, grade=r.grade, unit=r.unit, unit_price=r.unit_price, lead_time_days=r.lead_time_days) for r in rows]


@app.post("/suppliers/import")
def suppliers_import(items: list[schemas.SupplierProduct], role: str = Depends(require_jwt_role_dep("manager"))):
    db = SessionLocal()
    for it in items:
        row = models.SupplierProduct(supplier_id=int(it.supplier_id or 0), supplier_name=it.supplier_name, product_name=it.product_name, grade=it.grade, unit=it.unit, unit_price=it.unit_price, lead_time_days=it.lead_time_days)
        db.add(row)
    db.commit()
    return {"ok": True}


@app.post("/suppliers/upload_csv")
async def suppliers_upload_csv(file: UploadFile = File(...), role: str = Depends(require_jwt_role_dep("manager"))):
    import csv
    db = SessionLocal()
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        db.add(models.SupplierProduct(
            supplier_id=int(row.get("supplier_id") or 0),
            supplier_name=row.get("supplier_name") or "",
            product_name=row.get("product_name") or "",
            grade=row.get("grade") or None,
            unit=row.get("unit") or "kg",
            unit_price=float(row.get("unit_price") or 0.0),
            lead_time_days=int(row.get("lead_time_days") or 0),
            sustainability=float(row.get("sustainability") or 0.5),
        ))
    db.commit()
    return {"ok": True}


@app.post("/sourcing/recommend", response_model=schemas.SourcingResponse)
def sourcing_recommend(items: list[schemas.SourcingRequestItem]):
    return sourcing.recommend(items)


@app.get("/nutrition/lookup", response_model=schemas.NutritionLookupResponse)
def nutrition_lookup(name: str):
    from .data.nutrition_db import lookup
    return schemas.NutritionLookupResponse(name=name, macro_profile=lookup(name))


@app.post("/inventory/import")
def inventory_import(items: list[schemas.InventoryItem], role: str = Depends(require_jwt_role_dep("manager"))):
    db = SessionLocal()
    for it in items:
        row = models.InventoryItem(sku=it.sku, name=it.name, stock_qty=it.stock_qty, reorder_point=it.reorder_point, reserve_qty=it.reserve_qty, unit_price_per_kg=it.unit_price_per_kg or 0.0, supplier_id=int(it.supplier_id or 0) if it.supplier_id else None)
        db.add(row)
    db.commit()
    return {"ok": True}


@app.post("/inventory/reorder")
def inventory_reorder(items: list[schemas.InventoryItem], role: str = Depends(require_jwt_role_dep("manager"))):
    adv = inventory.evaluate(items)
    return {"order": adv.notices, "recommendations": adv.recommendations}


@app.post("/calc/live")
def calc_live(ingredients: list[schemas.IngredientInput], servings: int = 1):
    def gen():
        acc = schemas.NutritionSummary(calories=0.0, protein_g=0.0, fat_g=0.0, carbs_g=0.0)
        cost_acc = 0.0
        for ing in ingredients:
            part = nutrition.calculate_totals([ing])
            acc = schemas.NutritionSummary(
                calories=round(acc.calories + part.calories, 2),
                protein_g=round(acc.protein_g + part.protein_g, 2),
                fat_g=round(acc.fat_g + part.fat_g, 2),
                carbs_g=round(acc.carbs_g + part.carbs_g, 2),
            )
            cost_acc = round(cost_acc + costing.food_cost([ing]), 2)
            per = nutrition.per_serving(acc, servings)
            yield "data: " + json.dumps({"total": acc.model_dump(), "per_serving": per.model_dump(), "food_cost_total": cost_acc, "food_cost_per_serving": round(cost_acc / max(servings,1),2)}) + "\n\n"
        yield "event: end\n" + "data: DONE\n\n"
    import json
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/sourcing/llm_suggest", response_model=schemas.SupplierLLMSuggestionsResponse)
def sourcing_llm_suggest(prompt: str):
    return suggest_suppliers(prompt)


@app.post("/auth/mock-token", response_model=schemas.MockTokenResponse)
def auth_mock_token(req: schemas.MockTokenRequest):
    return schemas.MockTokenResponse(token=issue_mock_token(req.email, req.role))
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/api/dashboard/metrics")
def dashboard_metrics():
    db = SessionLocal()
    sp_count = db.query(models.SupplierProduct).count()
    inv_count = db.query(models.InventoryItem).count()
    spend = 0.0
    for r in db.query(models.SupplierProduct).all():
        spend += float(r.unit_price or 0.0)
    return {
        "totalMenus": max(inv_count, 12),
        "activeUsers": max(sp_count, 23),
        "totalRevenue": round(spend * 100, 2),
        "monthlyGrowth": 7,
    }
