from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

from models import (
    Base, Brand, Category, Product, CrossReference,
    Customer, Vehicle, VinRequest,
    Warehouse, Stock, Supplier, PurchaseOrder,
    Order, OrderItem, PricingLog
)

DATABASE_URL = "postgresql+psycopg2://postgres:1212@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

session = Session()

# =========================
# Очистка БД
# =========================
def clear_db():
    session.query(OrderItem).delete()
    session.query(Order).delete()
    session.query(Stock).delete()
    session.query(Product).delete()
    session.query(Brand).delete()
    session.query(Category).delete()
    session.query(Customer).delete()
    session.query(Warehouse).delete()
    session.query(Supplier).delete()
    session.commit()


# =========================
# Заполнение
# =========================

def seed():

    # --- Бренды ---
    brands = [
        Brand(name="Toyota"),
        Brand(name="BMW"),
        Brand(name="Bosch"),
        Brand(name="Valeo")
    ]
    session.add_all(brands)
    session.commit()

    # --- Категории ---
    categories = [
        Category(name="Фильтры"),
        Category(name="Тормоза"),
        Category(name="Двигатель")
    ]
    session.add_all(categories)
    session.commit()

    # --- Товары ---
    products = []
    for i in range(50):
        brand = random.choice(brands)
        category = random.choice(categories)

        articul = f"A-{i}-{random.randint(1000,9999)}"

        product = Product(
            brand_id=brand.id,
            articul=articul,
            clean_articul=articul.replace("-", ""),
            name=f"Запчасть {i}",
            category_id=category.id,
            min_balance=random.randint(1, 10)
        )
        products.append(product)

    session.add_all(products)
    session.commit()

    # --- Кросс-номера ---
    for _ in range(20):
        p1, p2 = random.sample(products, 2)
        session.add(CrossReference(
            product_id_1=p1.id,
            product_id_2=p2.id,
            source="manual"
        ))
    session.commit()

    # --- Клиенты ---
    customers = []
    for i in range(10):
        customer = Customer(
            full_name=f"Клиент {i}",
            phone=f"+7999{i:04}",
            discount_level=random.choice([0, 5, 10])
        )
        customers.append(customer)

    session.add_all(customers)
    session.commit()

    # --- Машины ---
    vehicles = []
    for c in customers:
        vehicle = Vehicle(
            customer_id=c.id,
            vin=f"VIN{random.randint(10000,99999)}",
            license_plate=f"A{i}BC",
            brand="Toyota",
            model="Camry",
            year=2010 + random.randint(0, 10)
        )
        vehicles.append(vehicle)

    session.add_all(vehicles)
    session.commit()

    # --- Склады ---
    warehouses = [
        Warehouse(name="Основной", address="Москва"),
        Warehouse(name="Склад 2", address="СПб")
    ]
    session.add_all(warehouses)
    session.commit()

    # --- Остатки ---
    stocks = []
    for product in products:
        for wh in warehouses:
            stocks.append(Stock(
                product_id=product.id,
                warehouse_id=wh.id,
                quantity=random.randint(0, 50),
                cell_address=f"A-{random.randint(1,10)}"
            ))

    session.add_all(stocks)
    session.commit()

    # --- Поставщики ---
    suppliers = [
        Supplier(name="AutoTrade", delivery_days=3),
        Supplier(name="PartsAPI", delivery_days=5)
    ]
    session.add_all(suppliers)
    session.commit()

    # --- Заказы ---
    orders = []
    for c in customers:
        order = Order(
            customer_id=c.id,
            status="new",
            payment_method="card",
            total_price=0
        )
        session.add(order)
        session.commit()

        total = 0

        for _ in range(3):
            product = random.choice(products)
            qty = random.randint(1, 5)
            price = random.randint(1000, 5000)

            total += price * qty

            session.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                buy_price=price * 0.7,
                sell_price=price
            ))

        order.total_price = total
        orders.append(order)

    session.commit()

    print("База успешно заполнена!")


if __name__ == "__main__":
    clear_db()
    seed()