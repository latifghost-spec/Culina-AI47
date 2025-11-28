from pydantic import BaseModel, Field
from typing import List, Optional


class MacroProfile(BaseModel):
    calories_per_100g: Optional[float] = None
    protein_g_per_100g: Optional[float] = None
    fat_g_per_100g: Optional[float] = None
    carbs_g_per_100g: Optional[float] = None


class IngredientInput(BaseModel):
    name: str
    quantity_g: float
    unit_price_per_kg: Optional[float] = None
    waste_pct: Optional[float] = 0.0
    macro_profile: Optional[MacroProfile] = None
    allergens: Optional[List[str]] = []


class NutritionSummary(BaseModel):
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float


class NutritionResponse(BaseModel):
    total: NutritionSummary
    per_serving: NutritionSummary


class CostingResponse(BaseModel):
    food_cost_total: float
    food_cost_per_serving: float
    suggested_price: Optional[float] = None


class RecipeIdeaRequest(BaseModel):
    prompt: str
    servings: int = 2
    target_cost_pct: float = 0.3
    dietary_tags: Optional[List[str]] = []
    excluded_allergens: Optional[List[str]] = []
    use_llm: bool = True


class FicheIngredient(BaseModel):
    name: str
    quantity_g: float


class FicheTechnique(BaseModel):
    title: str
    yield_servings: int
    ingredients: List[FicheIngredient]
    steps: List[str]
    plating_notes: Optional[str] = None
    allergens: Optional[List[str]] = []
    nutrition_per_serving: Optional[NutritionSummary] = None
    food_cost_per_serving: Optional[float] = None
    suggested_price: Optional[float] = None


class InventoryItem(BaseModel):
    sku: str
    name: str
    stock_qty: float
    reorder_point: float
    reserve_qty: float
    unit_price_per_kg: Optional[float] = None
    supplier_id: Optional[str] = None


class Supplier(BaseModel):
    id: str
    name: str
    lead_time_days: int


class InventoryAdvice(BaseModel):
    sku: str
    action: str
    reason: str
    recommended_qty: Optional[float] = None


class InventoryResponse(BaseModel):
    notices: List[InventoryAdvice]
    recommendations: List[str]


class SupplierProduct(BaseModel):
    supplier_id: str
    supplier_name: str
    product_name: str
    grade: Optional[str] = None
    unit: str
    unit_price: float
    lead_time_days: int
    sustainability: Optional[float] = 0.5


class SourcingRequestItem(BaseModel):
    name: str
    quantity_g: Optional[float] = None
    dietary_tags: Optional[List[str]] = []


class SourcingRecommendation(BaseModel):
    request_name: str
    top_options: List[SupplierProduct]
    note: Optional[str] = None
    substitutions: Optional[List[SupplierProduct]] = []


class SourcingResponse(BaseModel):
    recommendations: List[SourcingRecommendation]


class NutritionLookupResponse(BaseModel):
    name: str
    macro_profile: Optional[MacroProfile] = None


class SupplierLLMSuggestion(BaseModel):
    name: str
    note: Optional[str] = None
    confidence: Optional[float] = 0.5


class SupplierLLMSuggestionsResponse(BaseModel):
    suggestions: List[SupplierLLMSuggestion]


class MockTokenRequest(BaseModel):
    email: str
    role: str


class MockTokenResponse(BaseModel):
    token: str


class VideoResponse(BaseModel):
    prompt: str
    video_urls: List[str]


class BusinessPlanInput(BaseModel):
    seats: int
    average_check: float
    open_days_per_month: int
    fixed_monthly_costs: float
    variable_cost_rate: float
    initial_capex: float


class BusinessPlanOutput(BaseModel):
    projected_monthly_revenue: float
    projected_monthly_opex: float
    gross_margin_rate: float
    break_even_months: float
