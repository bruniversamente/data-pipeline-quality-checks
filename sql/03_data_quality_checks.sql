-- Data quality checks for the pipeline.
-- Run after staging tables are created.

CREATE OR REPLACE TABLE dq_summary AS
SELECT 'duplicate_customer_id' AS rule_name, 'Critical' AS severity, COUNT(*) AS failed_records
FROM (
    SELECT customer_id
    FROM stg_customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate_order_id', 'Critical', COUNT(*)
FROM (
    SELECT order_id
    FROM stg_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate_order_item_id', 'Critical', COUNT(*)
FROM (
    SELECT order_item_id
    FROM stg_order_items
    GROUP BY order_item_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'invalid_order_date', 'Critical', COUNT(*)
FROM raw_orders AS raw
LEFT JOIN stg_orders AS stg
    ON raw.order_id = stg.order_id
WHERE raw.order_date IS NOT NULL
  AND stg.order_date IS NULL
UNION ALL
SELECT 'missing_customer_reference', 'Critical', COUNT(*)
FROM stg_orders AS orders
LEFT JOIN stg_customers_unique AS customers
    ON orders.customer_id = customers.customer_id
WHERE customers.customer_id IS NULL
UNION ALL
SELECT 'missing_product_reference', 'Critical', COUNT(*)
FROM stg_order_items AS items
LEFT JOIN stg_products AS products
    ON items.product_id = products.product_id
WHERE products.product_id IS NULL
UNION ALL
SELECT 'invalid_quantity', 'Critical', COUNT(*)
FROM stg_order_items
WHERE quantity IS NULL OR quantity <= 0
UNION ALL
SELECT 'invalid_discount', 'Critical', COUNT(*)
FROM stg_order_items
WHERE discount_pct IS NULL OR discount_pct < 0 OR discount_pct > 1
UNION ALL
SELECT 'negative_payment_amount', 'Critical', COUNT(*)
FROM stg_payments
WHERE payment_amount IS NULL OR payment_amount < 0
UNION ALL
SELECT 'payment_without_order', 'Critical', COUNT(*)
FROM stg_payments AS payments
LEFT JOIN stg_orders_unique AS orders
    ON payments.order_id = orders.order_id
WHERE orders.order_id IS NULL
UNION ALL
SELECT 'completed_order_without_payment', 'Critical', COUNT(*)
FROM stg_orders_unique AS orders
LEFT JOIN stg_payments AS payments
    ON orders.order_id = payments.order_id
WHERE orders.order_status = 'Completed'
  AND payments.order_id IS NULL
UNION ALL
SELECT 'payment_amount_mismatch', 'Critical', COUNT(*)
FROM (
    WITH order_totals AS (
        SELECT
            order_id,
            ROUND(SUM(net_item_amount), 2) AS order_total
        FROM stg_order_items_unique
        GROUP BY order_id
    ),
    payment_totals AS (
        SELECT
            order_id,
            ROUND(SUM(CASE WHEN payment_status = 'Captured' THEN payment_amount ELSE 0 END), 2) AS captured_payment_amount
        FROM stg_payments
        GROUP BY order_id
    )
    SELECT
        orders.order_id,
        order_totals.order_total,
        payment_totals.captured_payment_amount
    FROM stg_orders_unique AS orders
    LEFT JOIN order_totals
        ON orders.order_id = order_totals.order_id
    LEFT JOIN payment_totals
        ON orders.order_id = payment_totals.order_id
    WHERE orders.order_status = 'Completed'
) AS totals
WHERE ABS(COALESCE(captured_payment_amount, 0) - COALESCE(order_total, 0)) > 0.05
UNION ALL
SELECT 'cancelled_order_with_captured_payment', 'Warning', COUNT(*)
FROM stg_orders_unique AS orders
INNER JOIN stg_payments AS payments
    ON orders.order_id = payments.order_id
WHERE orders.order_status = 'Cancelled'
  AND payments.payment_status = 'Captured'
UNION ALL
SELECT 'inactive_customer_on_completed_order', 'Warning', COUNT(*)
FROM stg_orders_unique AS orders
LEFT JOIN stg_customers_unique AS customers
    ON orders.customer_id = customers.customer_id
WHERE orders.order_status = 'Completed'
  AND customers.is_active = FALSE
UNION ALL
SELECT 'inactive_product_on_completed_order', 'Warning', COUNT(*)
FROM stg_orders_unique AS orders
LEFT JOIN stg_order_items_unique AS items
    ON orders.order_id = items.order_id
LEFT JOIN stg_products AS products
    ON items.product_id = products.product_id
WHERE orders.order_status = 'Completed'
  AND products.is_active = FALSE;

SELECT * FROM dq_summary ORDER BY severity, failed_records DESC, rule_name;
