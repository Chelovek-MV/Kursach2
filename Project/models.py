from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey,
    Float, DateTime, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

# =========================
# 1. Каталог
# =========================

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    articul = Column(String, nullable=False)
    clean_articul = Column(String, nullable=False)

    name = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))

    min_balance = Column(Integer, default=0)

    brand = relationship("Brand")
    category = relationship("Category")

    __table_args__ = (
        Index("ix_products_articul", "articul"),
        Index("ix_products_clean_articul", "clean_articul"),
        UniqueConstraint("brand_id", "articul", name="uq_brand_articul"),
    )


class CrossReference(Base):
    __tablename__ = "cross_references"

    id = Column(Integer, primary_key=True)

    product_id_1 = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_id_2 = Column(Integer, ForeignKey("products.id"), nullable=False)

    source = Column(String)

    __table_args__ = (
        UniqueConstraint("product_id_1", "product_id_2", name="uq_cross_pair"),
    )


# =========================
# 2. CRM
# =========================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)

    full_name = Column(String)
    phone = Column(String, index=True)
    telegram_id = Column(String)
    discount_level = Column(Float, default=0)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    vin = Column(String, index=True)
    license_plate = Column(String, index=True)

    brand = Column(String)
    model = Column(String)
    year = Column(Integer)

    customer = relationship("Customer")


class VinRequest(Base):
    __tablename__ = "vin_requests"

    id = Column(Integer, primary_key=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    status = Column(String, index=True)

    manager_id = Column(Integer)
    comment = Column(Text)

    vehicle = relationship("Vehicle")


# =========================
# 3. Склад
# =========================

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    quantity = Column(Integer, default=0)
    cell_address = Column(String)

    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_stock"),
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    api_key = Column(String)
    api_endpoint = Column(String)
    delivery_days = Column(Integer)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    status = Column(String, index=True)

    total_amount = Column(Float)

    supplier = relationship("Supplier")


# =========================
# 4. Продажи
# =========================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, index=True)

    payment_method = Column(String)
    total_price = Column(Float)

    customer = relationship("Customer")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer)
    buy_price = Column(Float)
    sell_price = Column(Float)

    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
    )


class PricingLog(Base):
    __tablename__ = "pricing_log"

    id = Column(Integer, primary_key=True)

    articul = Column(String, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    price = Column(Float)
    delivery_time = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# =========================
# Подключение и создание БД
# =========================

DATABASE_URL = "postgresql+psycopg2://postgres:1212@localhost:5432/mydb"

engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db()