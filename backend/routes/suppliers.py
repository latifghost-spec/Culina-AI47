from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from db import get_db
from models import (
    SupplierDB, SupplierProductDB, PurchaseOrderDB, PurchaseOrderItemDB,
    InventoryItemDB, InventoryAlertDB, AIConsultantRecommendationDB,
    SupplierCreate, SupplierResponse, SupplierProductCreate, SupplierProductResponse,
    PurchaseOrderCreate, PurchaseOrderItemCreate, PurchaseOrderResponse,
    InventoryItemCreate, InventoryItemResponse, InventoryAlertResponse,
    AIConsultantRequest, AIConsultantResponse, ExportRequest
)
from services.supplier_service import SupplierService
from services.export_service import ExportService
from auth import get_current_user as get_current_chef
import os
from typing import Dict

router = APIRouter()

# Initialize services
def get_supplier_service(db: Session = Depends(get_db)):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API key not configured"
        )
    return SupplierService(db, gemini_api_key)

def get_export_service():
    return ExportService()

# Supplier Management Routes
@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Create a new supplier for the chef"""
    db_supplier = SupplierDB(
        chef_id=current_chef["id"],
        **supplier.model_dump()
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get all suppliers for the current chef"""
    query = db.query(SupplierDB).filter(SupplierDB.chef_id == current_chef["id"])
    
    if is_active is not None:
        query = query.filter(SupplierDB.is_active == is_active)
    
    if category:
        query = query.filter(SupplierDB.specialties.contains([category]))
    
    suppliers = query.offset(skip).limit(limit).all()
    return suppliers

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get a specific supplier"""
    supplier = db.query(SupplierDB).filter(
        SupplierDB.id == supplier_id,
        SupplierDB.chef_id == current_chef["id"]
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_update: SupplierCreate,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Update a supplier"""
    supplier = db.query(SupplierDB).filter(
        SupplierDB.id == supplier_id,
        SupplierDB.chef_id == current_chef["id"]
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    for key, value in supplier_update.model_dump().items():
        setattr(supplier, key, value)
    
    db.commit()
    db.refresh(supplier)
    return supplier

@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Delete (deactivate) a supplier"""
    supplier = db.query(SupplierDB).filter(
        SupplierDB.id == supplier_id,
        SupplierDB.chef_id == current_chef["id"]
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    supplier.is_active = False
    db.commit()
    
    return {"message": "Supplier deactivated successfully"}

# Supplier Product Routes
@router.post("/suppliers/{supplier_id}/products", response_model=SupplierProductResponse)
async def create_supplier_product(
    supplier_id: int,
    product: SupplierProductCreate,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Add a product to a supplier's catalog"""
    # Verify supplier belongs to chef
    supplier = db.query(SupplierDB).filter(
        SupplierDB.id == supplier_id,
        SupplierDB.chef_id == current_chef["id"]
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    db_product = SupplierProductDB(
        supplier_id=supplier_id,
        **product.model_dump()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/suppliers/{supplier_id}/products", response_model=List[SupplierProductResponse])
async def get_supplier_products(
    supplier_id: int,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get all products for a supplier"""
    # Verify supplier belongs to chef
    supplier = db.query(SupplierDB).filter(
        SupplierDB.id == supplier_id,
        SupplierDB.chef_id == current_chef["id"]
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    query = db.query(SupplierProductDB).filter(
        SupplierProductDB.supplier_id == supplier_id
    )
    
    if category:
        query = query.filter(SupplierProductDB.category.ilike(f"%{category}%"))
    
    if brand:
        query = query.filter(SupplierProductDB.brand.ilike(f"%{brand}%"))
    
    if is_active is not None:
        query = query.filter(SupplierProductDB.is_active == is_active)
    
    products = query.all()
    return products

# AI-Powered Supplier Recommendations
@router.post("/suppliers/recommendations")
async def get_supplier_recommendations(
    item_name: str,
    quantity_needed: float,
    urgency: str = "normal",
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Get AI-powered supplier recommendations for a specific item"""
    try:
        recommendations = await supplier_service.get_supplier_recommendations(
            current_chef["id"], item_name, quantity_needed, urgency
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

# Inventory Management Routes
@router.post("/inventory", response_model=InventoryItemResponse)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Create a new inventory item"""
    db_item = InventoryItemDB(
        chef_id=current_chef["id"],
        **item.model_dump()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/inventory", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    low_stock_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get all inventory items for the chef"""
    query = db.query(InventoryItemDB).filter(InventoryItemDB.chef_id == current_chef["id"])
    
    if category:
        query = query.filter(InventoryItemDB.category.ilike(f"%{category}%"))
    
    if status:
        query = query.filter(InventoryItemDB.status == status)
    
    if low_stock_only:
        query = query.filter(InventoryItemDB.current_stock <= InventoryItemDB.minimum_stock)
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/inventory/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get a specific inventory item"""
    item = db.query(InventoryItemDB).filter(
        InventoryItemDB.id == item_id,
        InventoryItemDB.chef_id == current_chef["id"]
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item

@router.put("/inventory/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_update: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Update an inventory item"""
    item = db.query(InventoryItemDB).filter(
        InventoryItemDB.id == item_id,
        InventoryItemDB.chef_id == current_chef["id"]
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    for key, value in item_update.model_dump().items():
        setattr(item, key, value)
    
    item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item

# Inventory Alerts
@router.get("/inventory/alerts", response_model=List[InventoryAlertResponse])
async def get_inventory_alerts(
    unread_only: Optional[bool] = None,
    priority: Optional[str] = None,
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Get inventory alerts for the chef"""
    # First, check for new alerts
    alerts = supplier_service.check_inventory_alerts(current_chef["id"])
    
    # Get alerts from database
    db = supplier_service.db
    query = db.query(InventoryAlertDB).filter(
        InventoryAlertDB.chef_id == current_chef["id"]
    )
    
    if unread_only:
        query = query.filter(InventoryAlertDB.is_read == False)
    
    if priority:
        query = query.filter(InventoryAlertDB.priority == priority)
    
    query = query.order_by(InventoryAlertDB.created_at.desc())
    
    db_alerts = query.all()
    return db_alerts

@router.post("/inventory/check-alerts")
async def check_inventory_alerts(
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Manually trigger inventory alert check"""
    alerts = supplier_service.check_inventory_alerts(current_chef["id"])
    return {"alerts_generated": len(alerts), "alerts": alerts}

# AI Consultant Routes
@router.post("/consultant/recommendations")
async def get_ai_consultant_recommendations(
    request: AIConsultantRequest,
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Get AI consultant recommendations"""
    try:
        if request.query_type == "supplier_comparison":
            # Use supplier service for supplier recommendations
            recommendations = await supplier_service.get_supplier_recommendations(
                current_chef["id"], 
                request.item_name or request.category or "general",
                1.0,  # Default quantity
                "normal"
            )
            return recommendations
        
        elif request.query_type == "inventory_optimization":
            # Check inventory alerts and provide optimization recommendations
            alerts = supplier_service.check_inventory_alerts(current_chef["id"])
            return {"alerts": alerts, "recommendations": "Inventory optimization recommendations generated"}
        
        elif request.query_type == "cost_optimization":
            # Generate cost optimization recommendations
            analytics = supplier_service.get_supplier_performance_analytics(current_chef["id"])
            return {"analytics": analytics, "recommendations": "Cost optimization analysis completed"}
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid query type"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.get("/consultant/recommendations/history", response_model=List[AIConsultantResponse])
async def get_consultant_recommendation_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get AI consultant recommendation history"""
    recommendations = db.query(AIConsultantRecommendationDB).filter(
        AIConsultantRecommendationDB.chef_id == current_chef["id"]
    ).order_by(AIConsultantRecommendationDB.created_at.desc()).offset(skip).limit(limit).all()
    
    return recommendations

# Brand Comparison Route
@router.post("/consultant/brand-comparison")
async def get_brand_comparison(
    category: str,
    brands: List[str],
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Get detailed brand comparison for equipment"""
    try:
        comparison = supplier_service.generate_brand_comparison(
            current_chef["id"], category, brands
        )
        return comparison
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate brand comparison: {str(e)}"
        )

# Purchase Orders
@router.post("/purchase-orders", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    items: List[Dict],
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Create a new purchase order"""
    try:
        result = supplier_service.create_purchase_order(
            current_chef["id"],
            order_data.supplier_id,
            items,
            order_data.priority or "normal"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create purchase order: {str(e)}"
        )

@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Get purchase orders for the chef"""
    query = db.query(PurchaseOrderDB).filter(PurchaseOrderDB.chef_id == current_chef["id"])
    
    if status:
        query = query.filter(PurchaseOrderDB.status == status)
    
    if supplier_id:
        query = query.filter(PurchaseOrderDB.supplier_id == supplier_id)
    
    orders = query.order_by(PurchaseOrderDB.created_at.desc()).offset(skip).limit(limit).all()
    return orders

# Supplier Analytics
@router.get("/suppliers/analytics")
async def get_supplier_analytics(
    supplier_service: SupplierService = Depends(get_supplier_service),
    current_chef: dict = Depends(get_current_chef)
):
    """Get comprehensive supplier performance analytics"""
    try:
        analytics = supplier_service.get_supplier_performance_analytics(current_chef["id"])
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {str(e)}"
        )

# Excel Export Routes
@router.post("/export")
async def export_data(
    export_request: ExportRequest,
    export_service: ExportService = Depends(get_export_service),
    db: Session = Depends(get_db),
    current_chef: dict = Depends(get_current_chef)
):
    """Export data to Excel or CSV format"""
    try:
        file_path = await export_service.export_data(
            current_chef["id"], 
            export_request.export_type,
            export_request.format,
            export_request.date_range,
            export_request.filters,
            db
        )
        
        return {
            "message": f"Data exported successfully",
            "file_path": file_path,
            "download_url": f"/download/{file_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )