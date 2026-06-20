-- Create analytics-ready marts.
-- Run after quality checks.

CREATE OR REPLACE TABLE mart_order_items AS
SELECT
    items.order_item_id,
    items.order_id,
    orders.order_date,
    orders.customer_id,
    customers.customer_segment,
    customers.region,
    orders.order_status,
    orders.source_system,
    items.product_id,
    products.product_name,
    products.category,
    items.quantity,
    items.unit_price,
    products.unit_cost,
    items.discount_pct,
    items.net_item_amount,
    ROUND(items.quantity * products.unit_cost, 2) AS item_cost,
    ROUND(items.net_item_amount - items.quantity * products.unit_cost, 2) AS gross_margin,
    CASE WHEN products.product_id IS NULL THEN TRUE ELSE FALSE END AS has_product_issue,
    CASE WHEN items.quantity IS NULL OR items.quantity <= 0 THEN TRUE ELSE FALSE END AS has_quantity_issue
FROM stg_order_items_unique AS items
LEFT JOIN stg_orders_unique AS orders
    ON items.order_id = orders.order_id
LEFT JOIN stg_products AS products
    ON items.product_id = products.product_id
LEFT JOIN stg_customers_unique AS customers
    ON orders.customer_id = customers.customer_id;

CREATE OR REPLACE TABLE mart_orders AS
WITH order_totals AS (
    SELECT
        order_id,
        ROUND(SUM(net_item_amount), 2) AS order_total,
        COUNT(*) AS item_count
    FROM stg_order_items_unique
    GROUP BY order_id
),
payment_summary AS (
    SELECT
        order_id,
        ROUND(SUM(CASE WHEN payment_status = 'Captured' THEN payment_amount ELSE 0 END), 2) AS captured_payment_amount,
        MAX(payment_status) AS latest_payment_status,
        COUNT(*) AS payment_records
    FROM stg_payments
    GROUP BY order_id
),
item_quality AS (
    SELECT
        items.order_id,
        BOOL_OR(products.product_id IS NULL) AS has_product_reference_issue,
        BOOL_OR(items.quantity IS NULL OR items.quantity <= 0) AS has_item_quantity_issue
    FROM stg_order_items_unique AS items
    LEFT JOIN stg_products AS products
        ON items.product_id = products.product_id
    GROUP BY items.order_id
)
SELECT
    orders.order_id,
    orders.order_date,
    orders.customer_id,
    customers.customer_segment,
    customers.region,
    orders.order_status,
    orders.source_system,
    totals.item_count,
    totals.order_total,
    payments.captured_payment_amount,
    payments.latest_payment_status,
    payments.payment_records,
    CASE WHEN customers.customer_id IS NULL THEN TRUE ELSE FALSE END AS has_customer_issue,
    CASE WHEN orders.order_date IS NULL THEN TRUE ELSE FALSE END AS has_date_issue,
    CASE WHEN payments.order_id IS NULL THEN TRUE ELSE FALSE END AS has_missing_payment_issue,
    COALESCE(item_quality.has_product_reference_issue, FALSE) AS has_product_reference_issue,
    COALESCE(item_quality.has_item_quantity_issue, FALSE) AS has_item_quantity_issue,
    CASE
        WHEN orders.order_status = 'Completed'
         AND ABS(COALESCE(payments.captured_payment_amount, 0) - COALESCE(totals.order_total, 0)) > 0.05
        THEN TRUE ELSE FALSE
    END AS has_payment_mismatch_issue,
    CASE
        WHEN customers.customer_id IS NULL
          OR orders.order_date IS NULL
          OR payments.order_id IS NULL
          OR COALESCE(item_quality.has_product_reference_issue, FALSE)
          OR COALESCE(item_quality.has_item_quantity_issue, FALSE)
          OR (
              orders.order_status = 'Completed'
              AND ABS(COALESCE(payments.captured_payment_amount, 0) - COALESCE(totals.order_total, 0)) > 0.05
          )
        THEN 'Review'
        ELSE 'Ready'
    END AS data_quality_status
FROM stg_orders_unique AS orders
LEFT JOIN stg_customers_unique AS customers
    ON orders.customer_id = customers.customer_id
LEFT JOIN order_totals AS totals
    ON orders.order_id = totals.order_id
LEFT JOIN payment_summary AS payments
    ON orders.order_id = payments.order_id
LEFT JOIN item_quality
    ON orders.order_id = item_quality.order_id;

SELECT 'mart_orders' AS table_name, COUNT(*) AS row_count FROM mart_orders
UNION ALL
SELECT 'mart_order_items', COUNT(*) FROM mart_order_items
UNION ALL
SELECT 'dq_summary', COUNT(*) FROM dq_summary;
