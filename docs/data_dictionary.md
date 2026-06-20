# Data dictionary

## Raw tables

### `raw_customers`

| Field | Description |
|---|---|
| `customer_id` | Customer identifier. |
| `customer_name` | Customer name. |
| `customer_segment` | Customer segment. |
| `region` | Customer region. |
| `created_at` | Customer creation date. |
| `is_active` | Active customer flag. |

### `raw_products`

| Field | Description |
|---|---|
| `product_id` | Product identifier. |
| `product_name` | Product name. |
| `category` | Product category. |
| `unit_cost` | Product unit cost. |
| `list_price` | Product list price. |
| `is_active` | Active product flag. |

### `raw_orders`

| Field | Description |
|---|---|
| `order_id` | Order identifier. |
| `order_date` | Order date. |
| `customer_id` | Customer identifier. |
| `order_status` | Order status. |
| `source_system` | Source system that generated the order. |

### `raw_order_items`

| Field | Description |
|---|---|
| `order_item_id` | Order item identifier. |
| `order_id` | Related order. |
| `product_id` | Related product. |
| `quantity` | Quantity sold. |
| `unit_price` | Sale unit price. |
| `discount_pct` | Discount percentage. |

### `raw_payments`

| Field | Description |
|---|---|
| `payment_id` | Payment identifier. |
| `order_id` | Related order. |
| `payment_date` | Payment date. |
| `payment_method` | Payment method. |
| `payment_status` | Payment status. |
| `payment_amount` | Payment amount. |

## Analytical outputs

### `mart_orders`

Order-level analytical table with customer, status, total amount, payment status and quality flags.

### `mart_order_items`

Item-level analytical table with product, quantity, price, cost and margin fields.

### `dq_summary`

Aggregated view with data quality rule results and severity.

## Exported outputs

### `quality_score.csv`

Run-level quality score, total orders and count of critical failures.

### `failed_rules.csv`

Only quality rules with one or more failing records.

### `source_system_quality.csv`

Order readiness by source system.

### `records_requiring_review.csv`

Orders marked as `Review`, including issue summary fields for investigation.

### `dashboard_data.json`

Compact dataset used by the static HTML dashboard.
