-- KPI and data quality monitoring queries.
-- Run after marts are created.

-- 1. Data quality summary
SELECT
    severity,
    COUNT(*) AS rules_checked,
    SUM(failed_records) AS total_failed_records,
    SUM(CASE WHEN failed_records > 0 THEN 1 ELSE 0 END) AS failed_rules
FROM dq_summary
GROUP BY severity
ORDER BY severity;

-- 2. Overall quality score
WITH totals AS (
    SELECT COUNT(*) AS total_orders FROM mart_orders
),
critical AS (
    SELECT SUM(failed_records) AS critical_failures
    FROM dq_summary
    WHERE severity = 'Critical'
)
SELECT
    total_orders,
    critical_failures,
    ROUND(1 - COALESCE(critical_failures, 0) / NULLIF(total_orders, 0), 4) AS quality_score
FROM totals
CROSS JOIN critical;

-- 3. Orders by quality status
SELECT
    data_quality_status,
    COUNT(*) AS orders
FROM mart_orders
GROUP BY data_quality_status
ORDER BY orders DESC;

-- 4. Revenue-ready orders
SELECT
    source_system,
    COUNT(*) AS completed_orders,
    ROUND(SUM(order_total), 2) AS order_total,
    ROUND(SUM(captured_payment_amount), 2) AS captured_payment_amount
FROM mart_orders
WHERE order_status = 'Completed'
  AND data_quality_status = 'Ready'
GROUP BY source_system
ORDER BY order_total DESC;

-- 5. Product-level analytical output
SELECT
    category,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units,
    ROUND(SUM(net_item_amount), 2) AS net_revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin
FROM mart_order_items
WHERE order_status = 'Completed'
  AND has_product_issue = FALSE
  AND has_quantity_issue = FALSE
GROUP BY category
ORDER BY net_revenue DESC;

-- 6. Records requiring review
SELECT
    order_id,
    order_date,
    customer_id,
    order_status,
    source_system,
    order_total,
    captured_payment_amount,
    has_customer_issue,
    has_date_issue,
    has_missing_payment_issue,
    has_payment_mismatch_issue
FROM mart_orders
WHERE data_quality_status = 'Review'
ORDER BY order_id;
