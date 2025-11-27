import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import google.generativeai as genai
from models import (
    SupplierDB, SupplierProductDB, PurchaseOrderDB, PurchaseOrderItemDB,
    InventoryItemDB, AIConsultantRecommendationDB, ChefDB
)
from services.pricing_service import PricingService

class SupplierService:
    def __init__(self, db: Session, gemini_api_key: str):
        self.db = db
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.pricing_service = PricingService()
        
    async def get_supplier_recommendations(self, chef_id: int, item_name: str, 
                                         quantity_needed: float, urgency: str = "normal") -> Dict:
        """Get AI-powered supplier recommendations for a specific item"""
        
        # Get current inventory item
        inventory_item = self.db.query(InventoryItemDB).filter(
            and_(InventoryItemDB.chef_id == chef_id, 
                 InventoryItemDB.item_name.ilike(f"%{item_name}%"))
        ).first()
        
        if not inventory_item:
            return {"error": "Inventory item not found"}
        
        # Get all suppliers for this chef
        suppliers = self.db.query(SupplierDB).filter(
            and_(SupplierDB.chef_id == chef_id, SupplierDB.is_active == True)
        ).all()
        
        # Get supplier products matching the item
        supplier_products = self.db.query(SupplierProductDB).filter(
            and_(
                SupplierProductDB.supplier_id.in_([s.id for s in suppliers]),
                SupplierProductDB.product_name.ilike(f"%{item_name}%"),
                SupplierProductDB.is_active == True
            )
        ).all()
        
        # Get real-time pricing data
        async with self.pricing_service:
            pricing_data = await self.pricing_service.get_item_pricing(
                item_name, inventory_item.unit, region="tunisia"
            )
        
        # Prepare comparison data
        comparison_data = []
        for product in supplier_products:
            supplier = self.db.query(SupplierDB).filter(SupplierDB.id == product.supplier_id).first()
            
            # Calculate total cost including delivery and minimum order considerations
            total_cost = product.price * quantity_needed
            if supplier.minimum_order and total_cost < supplier.minimum_order:
                total_cost = supplier.minimum_order
            
            comparison_data.append({
                "supplier_name": supplier.name,
                "supplier_rating": supplier.rating,
                "product_name": product.product_name,
                "brand": product.brand,
                "unit_price": float(product.price),
                "total_cost": float(total_cost),
                "currency": product.currency,
                "availability": product.availability,
                "lead_time": product.lead_time,
                "quality_rating": product.quality_rating,
                "delivery_time": supplier.delivery_time,
                "payment_terms": supplier.payment_terms,
                "minimum_order": supplier.minimum_order,
                "total_spent_with_supplier": supplier.total_spent,
                "certifications": product.certifications or []
            })
        
        # Generate AI recommendation
        prompt = f"""
        As a restaurant procurement AI consultant, analyze these supplier options for {item_name}:
        
        Current inventory: {inventory_item.current_stock} {inventory_item.unit}
        Monthly consumption: {inventory_item.average_monthly_consumption} {inventory_item.unit}
        Urgency level: {urgency}
        
        Supplier comparison data:
        {json.dumps(comparison_data, indent=2, default=str)}
        
        Market pricing reference: {pricing_data}
        
        Provide recommendations considering:
        1. Best value for money (price vs quality)
        2. Reliability and delivery time
        3. Payment terms flexibility
        4. Brand reputation (especially for brands like Josper, Houna, etc.)
        5. Total cost of ownership
        6. Chef's historical preferences
        
        Return a JSON with:
        - top_3_suppliers with detailed justifications
        - cost_savings_analysis
        - brand_recommendations with pros/cons
        - action_items for the chef
        - urgency_specific_advice
        """
        
        try:
            response = self.model.generate_content(prompt)
            ai_recommendations = json.loads(response.text)
            
            # Save recommendation to database
            recommendation = AIConsultantRecommendationDB(
                chef_id=chef_id,
                recommendation_type="supplier_comparison",
                title=f"Supplier Recommendations for {item_name}",
                description=f"AI analysis for sourcing {quantity_needed} {inventory_item.unit} of {item_name}",
                comparison_data=comparison_data,
                recommended_suppliers=ai_recommendations.get("top_3_suppliers", []),
                cost_savings_potential=ai_recommendations.get("potential_savings", 0),
                brand_recommendations=ai_recommendations.get("brand_recommendations", []),
                quality_score=ai_recommendations.get("quality_score", 0),
                reliability_score=ai_recommendations.get("reliability_score", 0),
                value_score=ai_recommendations.get("value_score", 0),
                action_items=ai_recommendations.get("action_items", []),
                implementation_priority=urgency,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            
            self.db.add(recommendation)
            self.db.commit()
            
            return {
                "recommendation_id": recommendation.id,
                "comparison_data": comparison_data,
                "ai_recommendations": ai_recommendations,
                "market_pricing": pricing_data,
                "urgency": urgency
            }
            
        except Exception as e:
            return {
                "error": f"AI recommendation generation failed: {str(e)}",
                "comparison_data": comparison_data,
                "market_pricing": pricing_data
            }
    
    def check_inventory_alerts(self, chef_id: int) -> List[Dict]:
        """Check inventory levels and generate alerts with AI recommendations"""
        
        inventory_items = self.db.query(InventoryItemDB).filter(
            InventoryItemDB.chef_id == chef_id
        ).all()
        
        alerts = []
        
        for item in inventory_items:
            alert_generated = False
            alert_message = ""
            alert_type = ""
            suggested_action = ""
            priority = "medium"
            
            # Check critical stock level
            if item.current_stock <= item.critical_stock:
                alert_type = "critical_stock"
                alert_message = f"CRITICAL: {item.item_name} stock is critically low ({item.current_stock} {item.unit})"
                suggested_action = f"URGENT: Order {item.minimum_stock * 2} {item.unit} immediately"
                priority = "critical"
                alert_generated = True
            
            # Check minimum stock level
            elif item.current_stock <= item.minimum_stock:
                alert_type = "low_stock"
                
                # AI-powered consumption analysis
                days_until_out = self._calculate_days_until_stock_out(item)
                
                if days_until_out <= 7:  # Less than a week
                    alert_message = f"LOW STOCK: {item.item_name} will run out in {days_until_out} days"
                    suggested_action = f"Order {item.average_monthly_consumption * 0.5} {item.unit} within 2 days"
                    priority = "high"
                else:
                    alert_message = f"LOW STOCK: {item.item_name} is below minimum threshold"
                    suggested_action = f"Consider ordering {item.average_monthly_consumption * 0.3} {item.unit} this week"
                    priority = "medium"
                
                alert_generated = True
            
            # Check expiry dates
            if item.expiry_date and item.expiry_date <= datetime.utcnow() + timedelta(days=7):
                alert_type = "expiry_warning"
                days_until_expiry = (item.expiry_date - datetime.utcnow()).days
                alert_message = f"EXPIRY WARNING: {item.item_name} expires in {days_until_expiry} days"
                suggested_action = f"Use {item.item_name} immediately or consider donating/selling"
                priority = "high"
                alert_generated = True
            
            # Generate AI-powered restock recommendation
            if alert_generated:
                ai_suggestion = self._generate_restock_recommendation(item, alert_type)
                if ai_suggestion:
                    suggested_action = ai_suggestion
                
                # Create alert in database
                alert = InventoryAlertDB(
                    chef_id=chef_id,
                    inventory_item_id=item.id,
                    alert_type=alert_type,
                    alert_message=alert_message,
                    suggested_action=suggested_action,
                    priority=priority
                )
                
                self.db.add(alert)
                alerts.append({
                    "item_name": item.item_name,
                    "alert_type": alert_type,
                    "current_stock": item.current_stock,
                    "unit": item.unit,
                    "alert_message": alert_message,
                    "suggested_action": suggested_action,
                    "priority": priority,
                    "days_until_out": days_until_out if 'days_until_out' in locals() else None
                })
        
        if alerts:
            self.db.commit()
        
        return alerts
    
    def _calculate_days_until_stock_out(self, item: InventoryItemDB) -> int:
        """Calculate days until item runs out based on consumption patterns"""
        if item.average_monthly_consumption <= 0:
            return 999  # No consumption data available
        
        daily_consumption = item.average_monthly_consumption / 30
        if daily_consumption <= 0:
            return 999
        
        days_remaining = item.current_stock / daily_consumption
        return int(days_remaining)
    
    def _generate_restock_recommendation(self, item: InventoryItemDB, alert_type: str) -> str:
        """Generate AI-powered restock recommendation"""
        
        prompt = f"""
        As a restaurant inventory AI consultant, provide a specific restock recommendation for:
        
        Item: {item.item_name}
        Current stock: {item.current_stock} {item.unit}
        Average monthly consumption: {item.average_monthly_consumption} {item.unit}
        Alert type: {alert_type}
        
        Consider:
        1. Optimal order quantity to minimize costs while ensuring availability
        2. Seasonal variations if any
        3. Supplier lead times and reliability
        4. Storage constraints
        5. Cash flow optimization
        
        Provide a concise, actionable recommendation for the chef.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            # Fallback recommendation
            if alert_type == "critical_stock":
                return f"Order {item.minimum_stock * 2} {item.unit} immediately from preferred supplier"
            elif alert_type == "low_stock":
                return f"Order {item.average_monthly_consumption * 0.4} {item.unit} within 3 days"
            else:
                return f"Monitor {item.item_name} closely and plan next order"
    
    def generate_brand_comparison(self, chef_id: int, category: str, 
                                brands: List[str]) -> Dict:
        """Generate detailed brand comparison for equipment like Josper, Houna, etc."""
        
        # Get supplier products for these brands
        brand_products = self.db.query(SupplierProductDB).filter(
            and_(
                SupplierProductDB.brand.in_(brands),
                SupplierProductDB.category.ilike(f"%{category}%"),
                SupplierProductDB.is_active == True
            )
        ).all()
        
        # Group by brand
        brand_comparison = {}
        for product in brand_products:
            brand = product.brand
            if brand not in brand_comparison:
                brand_comparison[brand] = {
                    "products": [],
                    "avg_price": 0,
                    "avg_quality_rating": 0,
                    "availability_score": 0,
                    "supplier_count": 0
                }
            
            brand_comparison[brand]["products"].append({
                "product_name": product.product_name,
                "price": float(product.price),
                "quality_rating": product.quality_rating,
                "availability": product.availability,
                "lead_time": product.lead_time,
                "certifications": product.certifications or []
            })
        
        # Calculate averages for each brand
        for brand, data in brand_comparison.items():
            if data["products"]:
                data["avg_price"] = sum(p["price"] for p in data["products"]) / len(data["products"])
                data["avg_quality_rating"] = sum(p["quality_rating"] for p in data["products"]) / len(data["products"])
                data["availability_score"] = sum(1 for p in data["products"] if p["availability"] == "in_stock") / len(data["products"])
                data["supplier_count"] = len(data["products"])
        
        # Generate AI brand recommendation
        prompt = f"""
        As a restaurant equipment AI consultant, analyze these brand options for {category}:
        
        Brand comparison data:
        {json.dumps(brand_comparison, indent=2, default=str)}
        
        Brands to analyze: {', '.join(brands)}
        
        Provide a detailed comparison considering:
        1. Price-to-quality ratio
        2. Brand reputation and reliability
        3. Service and support availability
        4. Resale value
        5. Technology and innovation
        6. Local market presence
        7. Chef community feedback
        
        Return JSON with:
        - brand_rankings with scores and justifications
        - best_value_brand
        - premium_choice_brand
        - budget_friendly_brand
        - specific_model_recommendations
        - implementation_timeline
        """
        
        try:
            response = self.model.generate_content(prompt)
            ai_analysis = json.loads(response.text)
            
            return {
                "brand_comparison": brand_comparison,
                "ai_analysis": ai_analysis,
                "recommendation_timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            return {
                "brand_comparison": brand_comparison,
                "error": f"AI analysis failed: {str(e)}",
                "recommendation_timestamp": datetime.utcnow()
            }
    
    def create_purchase_order(self, chef_id: int, supplier_id: int, 
                            items: List[Dict], priority: str = "normal") -> Dict:
        """Create a purchase order with AI-optimized recommendations"""
        
        # Generate unique order number
        order_number = f"PO-{chef_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in items:
            product = self.db.query(SupplierProductDB).filter(
                SupplierProductDB.id == item["product_id"]
            ).first()
            
            if not product:
                continue
            
            quantity = item["quantity"]
            unit_price = float(product.price)
            total_price = quantity * unit_price
            
            order_items.append({
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "notes": item.get("notes", "")
            })
            
            total_amount += total_price
        
        # Create purchase order
        purchase_order = PurchaseOrderDB(
            chef_id=chef_id,
            supplier_id=supplier_id,
            order_number=order_number,
            total_amount=total_amount,
            priority=priority,
            status="pending"
        )
        
        self.db.add(purchase_order)
        self.db.flush()  # Get the ID
        
        # Create order items
        for item_data in order_items:
            order_item = PurchaseOrderItemDB(
                order_id=purchase_order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                notes=item_data["notes"]
            )
            self.db.add(order_item)
        
        # Update supplier statistics
        supplier = self.db.query(SupplierDB).filter(SupplierDB.id == supplier_id).first()
        supplier.total_orders += 1
        supplier.total_spent += total_amount
        supplier.last_order_date = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "order_id": purchase_order.id,
            "order_number": order_number,
            "total_amount": total_amount,
            "items_count": len(order_items),
            "status": "created"
        }
    
    def get_supplier_performance_analytics(self, chef_id: int) -> Dict:
        """Get comprehensive supplier performance analytics"""
        
        suppliers = self.db.query(SupplierDB).filter(
            SupplierDB.chef_id == chef_id
        ).all()
        
        analytics = {
            "total_suppliers": len(suppliers),
            "active_suppliers": len([s for s in suppliers if s.is_active]),
            "verified_suppliers": len([s for s in suppliers if s.is_verified]),
            "supplier_categories": {},
            "top_suppliers": [],
            "performance_metrics": {}
        }
        
        # Analyze supplier categories and brands
        for supplier in suppliers:
            if supplier.specialties:
                for specialty in supplier.specialties:
                    if specialty not in analytics["supplier_categories"]:
                        analytics["supplier_categories"][specialty] = 0
                    analytics["supplier_categories"][specialty] += 1
            
            if supplier.brands_carried:
                for brand in supplier.brands_carried:
                    brand_key = f"brand_{brand}"
                    if brand_key not in analytics["supplier_categories"]:
                        analytics["supplier_categories"][brand_key] = 0
                    analytics["supplier_categories"][brand_key] += 1
        
        # Top suppliers by spending
        top_suppliers = sorted(suppliers, key=lambda x: x.total_spent, reverse=True)[:5]
        analytics["top_suppliers"] = [
            {
                "name": s.name,
                "total_spent": s.total_spent,
                "total_orders": s.total_orders,
                "average_order_value": s.total_spent / max(s.total_orders, 1),
                "rating": s.rating,
                "last_order": s.last_order_date
            }
            for s in top_suppliers
        ]
        
        # Calculate performance metrics
        total_spending = sum(s.total_spent for s in suppliers)
        analytics["performance_metrics"] = {
            "total_spending": total_spending,
            "average_supplier_rating": sum(s.rating for s in suppliers) / len(suppliers) if suppliers else 0,
            "average_order_frequency": sum(s.total_orders for s in suppliers) / len(suppliers) if suppliers else 0,
            "supplier_diversification": len(set(specialty for s in suppliers if s.specialties for specialty in s.specialties))
        }
        
        return analytics