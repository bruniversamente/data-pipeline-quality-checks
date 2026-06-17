"""Generate synthetic raw data for the pipeline project."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "generated" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = ["South", "Southeast", "Northeast"]
SEGMENTS = ["Consumer", "Small Business", "Enterprise"]
SOURCES = ["web", "store", "marketplace"]
PAYMENTS = ["Credit Card", "Debit Card", "Pix"]

PRODUCTS = [
    ("P001", "Notebook Basic", "Electronics", 1800.00, 2499.90, "true"),
    ("P002", "Wireless Mouse", "Electronics", 35.00, 79.90, "true"),
    ("P003", "Office Chair", "Furniture", 320.00, 649.90, "true"),
    ("P004", "Desk Lamp", "Home", 55.00, 129.90, "true"),
    ("P005", "Backpack", "Accessories", 70.00, 159.90, "true"),
    ("P006", "Monitor 24", "Electronics", 520.00, 899.90, "true"),
]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    customers = []
    for idx in range(1, 101):
        customers.append({
            "customer_id": f"C{idx:04d}",
            "customer_name": f"Customer {idx}",
            "customer_segment": random.choice(SEGMENTS),
            "region": random.choice(REGIONS),
            "created_at": (date(2025, 1, 1) + timedelta(days=random.randint(0, 420))).isoformat(),
            "is_active": random.choice(["true", "true", "true", "false"]),
        })

    products = [
        {
            "product_id": product_id,
            "product_name": name,
            "category": category,
            "unit_cost": cost,
            "list_price": price,
            "is_active": active,
        }
        for product_id, name, category, cost, price, active in PRODUCTS
    ]

    orders = []
    items = []
    payments = []
    start = date(2026, 1, 1)

    for idx in range(1, 501):
        order_id = f"O{idx:05d}"
        customer = random.choice(customers)
        order_date = start + timedelta(days=random.randint(0, 120))
        status = random.choice(["Completed", "Completed", "Completed", "Cancelled"])
        orders.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": customer["customer_id"],
            "order_status": status,
            "source_system": random.choice(SOURCES),
        })

        order_total = 0
        for item_idx in range(random.randint(1, 4)):
            product = random.choice(PRODUCTS)
            quantity = random.randint(1, 3)
            discount = random.choice([0, 0.03, 0.05, 0.10])
            amount = quantity * product[4] * (1 - discount)
            order_total += amount
            items.append({
                "order_item_id": f"OI{len(items) + 1:06d}",
                "order_id": order_id,
                "product_id": product[0],
                "quantity": quantity,
                "unit_price": product[4],
                "discount_pct": discount,
            })

        payments.append({
            "payment_id": f"PAY{idx:06d}",
            "order_id": order_id,
            "payment_date": order_date.isoformat(),
            "payment_method": random.choice(PAYMENTS),
            "payment_status": "Captured" if status == "Completed" else "Pending",
            "payment_amount": round(order_total, 2),
        })

    write_csv(OUT / "customers.csv", customers)
    write_csv(OUT / "products.csv", products)
    write_csv(OUT / "orders.csv", orders)
    write_csv(OUT / "order_items.csv", items)
    write_csv(OUT / "payments.csv", payments)
    print(f"Generated files in {OUT}")
    print(f"Customers: {len(customers)} | Orders: {len(orders)} | Items: {len(items)} | Payments: {len(payments)}")


if __name__ == "__main__":
    main()
