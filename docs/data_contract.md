# Data contract

This document defines minimum expectations for the raw input files.

## `sample_customers.csv`

Required fields:

- `customer_id`
- `customer_name`
- `customer_segment`
- `region`
- `created_at`
- `is_active`

Rules:

- `customer_id` must be unique.
- `created_at` must be a valid date.
- `is_active` must be `true` or `false`.

## `sample_products.csv`

Required fields:

- `product_id`
- `product_name`
- `category`
- `unit_cost`
- `list_price`
- `is_active`

Rules:

- `product_id` must be unique.
- `unit_cost` and `list_price` must be greater than or equal to zero.
- `is_active` must be `true` or `false`.

## `sample_orders.csv`

Required fields:

- `order_id`
- `order_date`
- `customer_id`
- `order_status`
- `source_system`

Rules:

- `order_id` must be unique.
- `order_date` must be a valid date.
- `customer_id` must exist in customers.
- `order_status` must be an accepted status.

## `sample_order_items.csv`

Required fields:

- `order_item_id`
- `order_id`
- `product_id`
- `quantity`
- `unit_price`
- `discount_pct`

Rules:

- `order_item_id` must be unique.
- `order_id` must exist in orders.
- `product_id` must exist in products.
- `quantity` must be greater than zero.
- `discount_pct` must be between 0 and 1.

## `sample_payments.csv`

Required fields:

- `payment_id`
- `order_id`
- `payment_date`
- `payment_method`
- `payment_status`
- `payment_amount`

Rules:

- `payment_id` must be unique.
- `order_id` must exist in orders.
- `payment_date` must be a valid date.
- `payment_amount` must be greater than or equal to zero.
