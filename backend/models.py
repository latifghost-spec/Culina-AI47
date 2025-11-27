from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Numeric
from pydantic import BaseModel, ConfigDict
from db import Base
from datetime import datetime, date
from typing import Optional, List, Dict

# --- Database Tables ---
class MenuDB(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    menu_type = Column(String)
    covers = Column(Integer)
    target_price = Column(Float)
    content = Column(Text)

class InventoryDB(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Float)
    unit = Column(String)
    category = Column(String)

class SalesDataDB(Base):
    __tablename__ = "sales_data"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    revenue = Column(Float)
    orders = Column(Integer)
    avg_order_value = Column(Float)
    customer_satisfaction = Column(Float)

class CustomerDB(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_visit = Column(DateTime)
    loyalty_points = Column(Integer, default=0)

class StaffDB(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    hourly_rate = Column(Float)
    hours_worked = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    hire_date = Column(DateTime, default=datetime.utcnow)

# --- Pydantic Schemas ---
class MenuRequest(BaseModel):
    menu_type: str
    covers: int
    target_price: float
    theme: str | None = None

class ConceptRequest(BaseModel):
    idea: str
    location: str
    budget_level: str

class PnLRequest(BaseModel):
    total_revenue: float
    total_food_cost: float
    labor_percent: float 
    rent_monthly: float

class PnLResponse(BaseModel):
    net_profit: float
    total_labor_cost: float
    gross_profit: float
    net_profit_margin: float

class InventoryItemReq(BaseModel):
    item_name: str
    quantity: float
    unit: str
    category: str

class MenuResponse(BaseModel):
    id: int
    name: str
    menu_type: str | None = None
    covers: int
    target_price: float
    content: str
    
    model_config = ConfigDict(from_attributes=True)

class DashboardMetrics(BaseModel):
    daily_revenue: float
    avg_order_value: float
    table_turnover: float
    customer_satisfaction: float
    food_cost_percentage: float
    labor_cost_percentage: float
    overhead_percentage: float
    net_margin_percentage: float
    low_stock_items: int
    waste_percentage: float
    pending_orders: int

class CreativeBriefRequest(BaseModel):
    theme: str | None = None
    season: str | None = None
    target_audience: str | None = None
    concept: str | None = None

class PitchDeckData(BaseModel):
    company: str
    tagline: str
    problem: str
    solution: str
    market: str
    traction: str
    revenue: str
    team: str
    ask: str

# Authentication Schemas
class ChefRegister(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    restaurant_name: str | None = None
    restaurant_location: str | None = None
    cuisine_specialty: str | None = None
    experience_years: int = 0
    phone: str | None = None

class ChefLogin(BaseModel):
    email: str
    password: str

class ChefResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    restaurant_name: str | None = None
    restaurant_location: str | None = None
    cuisine_specialty: str | None = None
    experience_years: int
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# Supplier Management Schemas
class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = "Tunisia"
    city: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_time: Optional[str] = None
    minimum_order: Optional[float] = 0.0
    specialties: Optional[List[str]] = None
    brands_carried: Optional[List[str]] = None

class SupplierResponse(BaseModel):
    id: int
    chef_id: int
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    country: str
    city: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_time: Optional[str] = None
    minimum_order: float
    rating: float
    specialties: Optional[List[str]] = None
    brands_carried: Optional[List[str]] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_order_date: Optional[datetime] = None
    total_orders: int
    total_spent: float
    
    model_config = ConfigDict(from_attributes=True)

class SupplierProductCreate(BaseModel):
    supplier_id: int
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    unit: str
    price: float
    currency: Optional[str] = "TND"
    availability: Optional[str] = "in_stock"
    minimum_quantity: Optional[float] = 1.0
    maximum_quantity: Optional[float] = None
    lead_time: Optional[str] = None
    quality_rating: Optional[float] = 0.0
    origin_country: Optional[str] = None
    certifications: Optional[List[str]] = None

class SupplierProductResponse(BaseModel):
    id: int
    supplier_id: int
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    unit: str
    price: float
    currency: str
    availability: str
    minimum_quantity: float
    maximum_quantity: Optional[float] = None
    lead_time: Optional[str] = None
    quality_rating: float
    origin_country: Optional[str] = None
    certifications: Optional[List[str]] = None
    last_price_update: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    requested_delivery_date: Optional[datetime] = None
    priority: Optional[str] = "normal"
    notes: Optional[str] = None

class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float
    notes: Optional[str] = None

class PurchaseOrderResponse(BaseModel):
    id: int
    chef_id: int
    supplier_id: int
    order_number: str
    order_date: datetime
    requested_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str
    priority: str
    total_amount: float
    currency: str
    payment_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Inventory Management Schemas
class InventoryItemCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    current_stock: Optional[float] = 0.0
    unit: str
    unit_cost: Optional[float] = 0.0
    currency: Optional[str] = "TND"
    minimum_stock: Optional[float] = 0.0
    maximum_stock: Optional[float] = None
    critical_stock: Optional[float] = 0.0
    preferred_supplier_id: Optional[int] = None
    alternative_suppliers: Optional[List[int]] = None
    storage_location: Optional[str] = None
    shelf_life_days: Optional[int] = None
    expiry_date: Optional[datetime] = None

class InventoryItemResponse(BaseModel):
    id: int
    chef_id: int
    item_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    current_stock: float
    unit: str
    unit_cost: float
    currency: str
    average_monthly_consumption: float
    consumption_pattern: Optional[Dict] = None
    seasonal_variations: Optional[Dict] = None
    minimum_stock: float
    maximum_stock: Optional[float] = None
    critical_stock: float
    preferred_supplier_id: Optional[int] = None
    alternative_suppliers: Optional[List[int]] = None
    storage_location: Optional[str] = None
    shelf_life_days: Optional[int] = None
    expiry_date: Optional[datetime] = None
    quality_check_frequency: str
    ai_recommendations: Optional[Dict] = None
    status: str
    last_updated: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class InventoryAlertResponse(BaseModel):
    id: int
    chef_id: int
    inventory_item_id: int
    alert_type: str
    alert_message: str
    suggested_action: Optional[str] = None
    priority: str
    is_read: bool
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# AI Consultant Schemas
class AIConsultantRequest(BaseModel):
    query_type: str  # supplier_comparison, inventory_optimization, cost_optimization
    item_name: Optional[str] = None  # For inventory optimization
    category: Optional[str] = None  # For supplier comparison
    budget_range: Optional[Dict[str, float]] = None  # min and max budget
    quality_requirements: Optional[List[str]] = None
    delivery_requirements: Optional[str] = None

class AIConsultantResponse(BaseModel):
    id: int
    chef_id: int
    recommendation_type: str
    title: str
    description: str
    comparison_data: Optional[Dict] = None
    recommended_suppliers: Optional[List[Dict]] = None
    cost_savings_potential: float
    brand_recommendations: Optional[List[Dict]] = None
    quality_score: float
    reliability_score: float
    value_score: float
    action_items: Optional[List[Dict]] = None
    implementation_priority: str
    estimated_implementation_time: Optional[str] = None
    is_implemented: bool
    implementation_notes: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Excel Export Schema
class ExportRequest(BaseModel):
    export_type: str  # suppliers, inventory, orders, recommendations
    format: str = "excel"  # excel, csv
    date_range: Optional[Dict[str, datetime]] = None
    filters: Optional[Dict] = None

class FinancialReport(BaseModel):
    period: str
    restaurant: str
    daily_revenue: float
    monthly_revenue: float
    yearly_revenue: float
    food_cost_percentage: float
    labor_cost_percentage: float
    overhead_percentage: float
    net_margin_percentage: float
    roi: float
    break_even_covers: int
    labor_efficiency: float
    inventory_turnover: float
    customer_retention: float
    average_ticket: float
    peak_hour_efficiency: float

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer)
    order_date = Column(DateTime, default=datetime.utcnow)
    delivery_date = Column(DateTime)
    total_amount = Column(Float)
    status = Column(String, default="pending")  # pending, delivered, cancelled
    notes = Column(Text)

class ChefDB(Base):
    __tablename__ = "chefs"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    restaurant_name = Column(String)
    restaurant_location = Column(String)
    cuisine_specialty = Column(String)
    experience_years = Column(Integer, default=0)
    phone = Column(String)
    profile_image = Column(String)

# Enhanced Supplier Management
class SupplierDB(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    website = Column(String)
    country = Column(String, default="Tunisia")
    city = Column(String)
    payment_terms = Column(String)  # e.g., "Net 30", "COD", "15 days"
    delivery_time = Column(String)  # e.g., "2-3 days", "Same day"
    minimum_order = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    specialties = Column(JSON)  # List of product categories they specialize in
    brands_carried = Column(JSON)  # List of brands they carry (e.g., "Josper", "Houna")
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_order_date = Column(DateTime)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)

class SupplierProductDB(Base):
    __tablename__ = "supplier_products"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    product_name = Column(String, nullable=False)
    brand = Column(String)  # Brand name (e.g., "Josper", "Houna")
    category = Column(String)  # Product category
    description = Column(Text)
    unit = Column(String)  # kg, liter, piece, etc.
    price = Column(Numeric(10, 3), nullable=False)  # Price per unit
    currency = Column(String, default="TND")
    availability = Column(String, default="in_stock")  # in_stock, out_of_stock, limited
    minimum_quantity = Column(Float, default=1.0)
    maximum_quantity = Column(Float)
    lead_time = Column(String)  # Time to deliver
    quality_rating = Column(Float, default=0.0)
    origin_country = Column(String)
    certifications = Column(JSON)  # Organic, Halal, etc.
    last_price_update = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class PurchaseOrderDB(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_number = Column(String, unique=True, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    requested_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)
    status = Column(String, default="pending")  # pending, approved, delivered, cancelled, delayed
    priority = Column(String, default="normal")  # low, normal, high, urgent
    total_amount = Column(Numeric(10, 3), default=0.0)
    currency = Column(String, default="TND")
    payment_status = Column(String, default="pending")  # pending, paid, partial
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrderItemDB(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("supplier_products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Numeric(10, 3), nullable=False)
    total_price = Column(Numeric(10, 3), nullable=False)
    received_quantity = Column(Float, default=0.0)
    notes = Column(Text)

# Enhanced Inventory Management with AI Alerts
class InventoryItemDB(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    item_name = Column(String, nullable=False)
    category = Column(String)  # Meat, Seafood, Vegetables, Spices, etc.
    brand = Column(String)  # Preferred brand
    current_stock = Column(Float, default=0.0)
    unit = Column(String, nullable=False)  # kg, liter, piece, etc.
    unit_cost = Column(Numeric(10, 3), default=0.0)
    currency = Column(String, default="TND")
    
    # AI-powered consumption tracking
    average_monthly_consumption = Column(Float, default=0.0)  # AI calculated
    consumption_pattern = Column(JSON)  # Weekly/monthly consumption data
    seasonal_variations = Column(JSON)  # Seasonal consumption patterns
    
    # Alert thresholds
    minimum_stock = Column(Float, default=0.0)  # Reorder point
    maximum_stock = Column(Float)  # Maximum storage capacity
    critical_stock = Column(Float, default=0.0)  # Critical alert level
    
    # Supplier preferences
    preferred_supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    alternative_suppliers = Column(JSON)  # List of backup supplier IDs
    
    # Storage and quality
    storage_location = Column(String)
    shelf_life_days = Column(Integer)
    expiry_date = Column(DateTime)
    quality_check_frequency = Column(String, default="weekly")
    
    # AI recommendations
    last_ai_analysis = Column(DateTime)
    ai_recommendations = Column(JSON)  # AI suggestions for this item
    
    # Status and tracking
    status = Column(String, default="active")  # active, low_stock, critical, expired
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryAlertDB(Base):
    __tablename__ = "inventory_alerts"
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # low_stock, critical_stock, expiry_warning, over_stock
    alert_message = Column(Text, nullable=False)
    suggested_action = Column(Text)  # AI suggestion for action
    priority = Column(String, default="medium")  # low, medium, high, critical
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# AI Consultant Recommendations
class AIConsultantRecommendationDB(Base):
    __tablename__ = "ai_consultant_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)  # supplier_comparison, cost_optimization, inventory_optimization
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Comparison data for suppliers
    comparison_data = Column(JSON)  # Detailed comparison of suppliers/products
    recommended_suppliers = Column(JSON)  # Top recommended suppliers with reasons
    cost_savings_potential = Column(Numeric(10, 2), default=0.0)
    
    # Brand recommendations (like Josper, Houna)
    brand_recommendations = Column(JSON)  # Recommended brands with justifications
    quality_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    value_score = Column(Float, default=0.0)  # Overall value proposition
    
    # Action items
    action_items = Column(JSON)  # List of recommended actions
    implementation_priority = Column(String, default="medium")  # low, medium, high
    estimated_implementation_time = Column(String)  # e.g., "1-2 weeks", "1 month"
    
    # Tracking
    is_implemented = Column(Boolean, default=False)
    implementation_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Recommendation expiry date