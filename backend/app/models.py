from sqlalchemy import Column, Integer, String, Float, Boolean
from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, index=True)


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    lead_time_days = Column(Integer)


class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, index=True)
    supplier_name = Column(String)
    product_name = Column(String, index=True)
    grade = Column(String)
    unit = Column(String)
    unit_price = Column(Float)
    lead_time_days = Column(Integer)
    sustainability = Column(Float, default=0.5)


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    stock_qty = Column(Float)
    reorder_point = Column(Float)
    reserve_qty = Column(Float)
    unit_price_per_kg = Column(Float)
    supplier_id = Column(Integer)
