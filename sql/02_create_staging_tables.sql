-- Create typed staging tables from raw inputs.
-- Engine: DuckDB

CREATE OR REPLACE TABLE stg_customers AS
SELECT
    customer_id,
    customer_name,
    customer_segment,
    region,
    TRY_CAST(created_at AS DATE) AS created_at,
    CASE LOWER(is_active)
        WHEN 'true' THEN TRUE
        WHEN 'false' THEN FALSE
        ELSE NULL
    END AS is_active
FROM raw_customers;

CREATE OR REPLACE TABLE stg_products AS
SELECT
    product_id,
    product_name,
    category,
    TRY_CAST(unit_cost AS DOUBLE) AS unit_cost,
    TRY_CAST(list_price AS DOUBLE) AS list_price,
    CASE LOWER(is_active)
        WHEN 'true' THEN TRUE
        WHEN 'false' THEN FALSE
        ELSE NULL
    END AS is_active
FROM raw_products;

CREATE OR REPLACE TABLE stg_orders AS
SELECT
    order_id,
    TRY_CAST(order_date AS DATE) AS order_date,
    customer_id,
    order_status,
    source_system
FROM raw_orders;

CREATE OR REPLACE TABLE stg_order_items AS
SELECT
    order_item_id,
    order_id,
    product_id,
    TRY_CAST(quantity AS INTEGER) AS quantity,
    TRY_CAST(unit_price AS DOUBLE) AS unit_price,
    TRY_CAST(discount_pct AS DOUBLE) AS discount_pct,
    ROUND(
        TRY_CAST(quantity AS DOUBLE) * TRY_CAST(unit_price AS DOUBLE) * (1 - TRY_CAST(discount_pct AS DOUBLE)),
        2
    ) AS net_item_amount
FROM raw_order_items;

CREATE OR REPLACE TABLE stg_payments AS
SELECT
    payment_id,
    order_id,
    TRY_CAST(payment_date AS DATE) AS payment_date,
    payment_method,
    payment_status,
    TRY_CAST(payment_amount AS DOUBLE) AS payment_amount
FROM raw_payments;

-- Deduplicated helper tables for analytical marts.
CREATE OR REPLACE TABLE stg_customers_unique AS
SELECT * EXCLUDE(row_number)
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC NULLS LAST) AS row_number
    FROM stg_customers
)
WHERE row_number = 1;

CREATE OR REPLACE TABLE stg_orders_unique AS
SELECT * EXCLUDE(row_number)
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_date DESC NULLS LAST) AS row_number
    FROM stg_orders
)
WHERE row_number = 1;

CREATE OR REPLACE TABLE stg_order_items_unique AS
SELECT * EXCLUDE(row_number)
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_item_id ORDER BY order_id) AS row_number
    FROM stg_order_items
)
WHERE row_number = 1;

SELECT 'stg_customers' AS table_name, COUNT(*) AS row_count FROM stg_customers
UNION ALL SELECT 'stg_products', COUNT(*) FROM stg_products
UNION ALL SELECT 'stg_orders', COUNT(*) FROM stg_orders
UNION ALL SELECT 'stg_order_items', COUNT(*) FROM stg_order_items
UNION ALL SELECT 'stg_payments', COUNT(*) FROM stg_payments;
