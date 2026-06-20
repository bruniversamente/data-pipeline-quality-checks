"""Generate synthetic raw data for the pipeline project.

The generated files intentionally include a small, controlled set of data
quality issues so the pipeline can demonstrate validation, quarantine and
publication gating.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
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

ANOMALOUS_ORDER_IDS = {
    "missing_customer": "O00017",
    "missing_product": "O00041",
    "payment_mismatch": "O00083",
    "missing_payment": "O00111",
    "cancelled_captured": "O00147",
    "invalid_quantity": "O00189",
}


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

        if order_id in {
            ANOMALOUS_ORDER_IDS["missing_customer"],
            ANOMALOUS_ORDER_IDS["missing_product"],
            ANOMALOUS_ORDER_IDS["payment_mismatch"],
            ANOMALOUS_ORDER_IDS["missing_payment"],
            ANOMALOUS_ORDER_IDS["invalid_quantity"],
        }:
            status = "Completed"
        if order_id == ANOMALOUS_ORDER_IDS["cancelled_captured"]:
            status = "Cancelled"

        orders.append({
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "customer_id": "C9999" if order_id == ANOMALOUS_ORDER_IDS["missing_customer"] else customer["customer_id"],
            "order_status": status,
            "source_system": random.choice(SOURCES),
        })

        order_total = 0
        for item_idx in range(random.randint(1, 4)):
            product = random.choice(PRODUCTS)
            quantity = random.randint(1, 3)
            discount = random.choice([0, 0.03, 0.05, 0.10])
            product_id = "P999" if order_id == ANOMALOUS_ORDER_IDS["missing_product"] and item_idx == 0 else product[0]
            if order_id == ANOMALOUS_ORDER_IDS["invalid_quantity"] and item_idx == 0:
                quantity = 0
            amount = quantity * product[4] * (1 - discount)
            order_total += amount
            items.append({
                "order_item_id": f"OI{len(items) + 1:06d}",
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": product[4],
                "discount_pct": discount,
            })

        if order_id == ANOMALOUS_ORDER_IDS["missing_payment"]:
            continue

        payment_amount = order_total
        if order_id == ANOMALOUS_ORDER_IDS["payment_mismatch"]:
            payment_amount = order_total - 75

        payments.append({
            "payment_id": f"PAY{idx:06d}",
            "order_id": order_id,
            "payment_date": order_date.isoformat(),
            "payment_method": random.choice(PAYMENTS),
            "payment_status": "Captured" if status == "Completed" or order_id == ANOMALOUS_ORDER_IDS["cancelled_captured"] else "Pending",
            "payment_amount": round(payment_amount, 2),
        })

    # Duplicate rows are deterministic and small enough to be easy to inspect.
    customers.append(customers[9].copy())
    orders.append(orders[24].copy())
    items.append(items[29].copy())

    write_csv(OUT / "sample_customers.csv", customers)
    write_csv(OUT / "sample_products.csv", products)
    write_csv(OUT / "sample_orders.csv", orders)
    write_csv(OUT / "sample_order_items.csv", items)
    write_csv(OUT / "sample_payments.csv", payments)
    print(f"Generated files in {OUT}")
    print(f"Customers: {len(customers)} | Orders: {len(orders)} | Items: {len(items)} | Payments: {len(payments)}")


if __name__ == "__main__":
    main()
