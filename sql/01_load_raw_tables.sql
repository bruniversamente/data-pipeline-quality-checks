-- Load raw CSV files into DuckDB.
-- Raw tables are intentionally permissive so quality checks can detect issues later.

CREATE OR REPLACE TABLE raw_customers AS
SELECT *
FROM read_csv_auto('data/raw/sample_customers.csv', all_varchar = true);

CREATE OR REPLACE TABLE raw_products AS
SELECT *
FROM read_csv_auto('data/raw/sample_products.csv', all_varchar = true);

CREATE OR REPLACE TABLE raw_orders AS
SELECT *
FROM read_csv_auto('data/raw/sample_orders.csv', all_varchar = true);

CREATE OR REPLACE TABLE raw_order_items AS
SELECT *
FROM read_csv_auto('data/raw/sample_order_items.csv', all_varchar = true);

CREATE OR REPLACE TABLE raw_payments AS
SELECT *
FROM read_csv_auto('data/raw/sample_payments.csv', all_varchar = true);

SELECT 'raw_customers' AS table_name, COUNT(*) AS rows_loaded FROM raw_customers
UNION ALL SELECT 'raw_products', COUNT(*) FROM raw_products
UNION ALL SELECT 'raw_orders', COUNT(*) FROM raw_orders
UNION ALL SELECT 'raw_order_items', COUNT(*) FROM raw_order_items
UNION ALL SELECT 'raw_payments', COUNT(*) FROM raw_payments;
