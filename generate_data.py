import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker
from transfrom_order_date import parse_date

fake = Faker()
random.seed(42)  # reproducible results while you're learning

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_CUSTOMERS = 50
NUM_PRODUCTS = 20
NUM_ORDERS = 200

CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports"]
COUNTRY_VARIANTS = ["US", "USA", "United States", "Germany", "DE", "Germany "]  # inconsistent on purpose


def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        email = fake.email() if random.random() > 0.05 else ""  # 5% missing emails
        customers.append({
            "customer_id": i,
            "name": fake.name(),
            "email": email,
            "signup_date": fake.date_between(start_date="-2y", end_date="today").isoformat(),
            "country": random.choice(COUNTRY_VARIANTS),
        })
    return customers


def generate_products():
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        products.append({
            "product_id": i,
            "name": fake.word().capitalize() + " " + fake.word().capitalize(),
            "category": random.choice(CATEGORIES),
            "unit_price": round(random.uniform(5, 300), 2),
        })
    return products


def random_date_format(date_obj):
    # Half the time write as YYYY-MM-DD, half as MM/DD/YYYY
    if random.random() > 0.5:
        return date_obj.isoformat()
    return date_obj.strftime("%m/%d/%Y")


def generate_orders():
    orders = []
    for i in range(1, NUM_ORDERS + 1):
        order_date = fake.date_between(start_date="-1y", end_date="today")

        # 3% chance of referencing a product_id that doesn't exist (orphan FK)
        product_id = random.randint(1, NUM_PRODUCTS)
        if random.random() < 0.03:
            product_id = NUM_PRODUCTS + random.randint(1, 5)

        quantity = random.randint(1, 5)
        if random.random() < 0.04:  # 4% missing quantity
            quantity = ""

        orders.append({
            "order_id": i,
            "customer_id": random.randint(1, NUM_CUSTOMERS),
            "product_id": product_id,
            "quantity": quantity,
            "order_date": random_date_format(order_date),
            "status": random.choice(["completed", "pending", "cancelled"]),
        })

    # Inject duplicate rows (~5% of orders duplicated)
    duplicates = random.sample(orders, k=int(NUM_ORDERS * 0.05))
    orders.extend(duplicates)
    random.shuffle(orders)
    return orders


def write_csv(filename, rows, fieldnames):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders()

    for order in orders:
        order["order_date"] = parse_date(order["order_date"])

    write_csv("customers.csv", customers, ["customer_id", "name", "email", "signup_date", "country"])
    write_csv("products.csv", products, ["product_id", "name", "category", "unit_price"])
    write_csv("orders.csv", orders, ["order_id", "customer_id", "product_id", "quantity", "order_date", "status"])