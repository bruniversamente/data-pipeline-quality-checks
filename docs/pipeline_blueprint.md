# Pipeline blueprint

## Purpose

This project demonstrates a controlled analytical pipeline with quality gates. The design mirrors a production pattern: raw ingestion, typed staging, validation, quarantined records and BI-ready marts.

## Layer 1 - Raw

Goal: load source files without changing business meaning.

Inputs:

- `sample_customers.csv`
- `sample_products.csv`
- `sample_orders.csv`
- `sample_order_items.csv`
- `sample_payments.csv`

Raw values are loaded permissively só invalid values can be detected instead of silently discarded.

## Layer 2 - Staging

Goal: convert values into analytical types and normalize fields.

Examples:

- parse dates with `TRY_CAST`;
- convert quantities, prices and payment amounts to numeric fields;
- standardize boolean fields;
- calculate `net_item_amount`.

## Layer 3 - Data quality

Goal: identify rows that are unsafe for BI consumption.

Rule groups:

- uniqueness;
- validity;
- referential integrity;
- payment consistency;
- operational warnings.

The pipeline writes rule-level results to `dq_summary`.

## Layer 4 - Analytical marts

Goal: create tables that BI tools can consume directly.

Outputs:

- `mart_orders`: one row per deduplicated order with quality flags;
- `mart_order_items`: one row per deduplicated order item with product and margin fields;
- `dq_summary`: quality monitoring table.

## Layer 5 - Portfolio outputs

`scripts/build_outputs.py` produces:

- CSV extracts in `outputs/`;
- `outputs/executive_findings.md`;
- `outputs/dashboard_data.json`;
- `dashboard/data_pipeline_quality_dashboard.html`.

## Automation

The GitHub Actions workflow installs dependencies and runs `scripts/build_outputs.py` plus `scripts/run_pipeline.py`. A pull request breaks if the pipeline cannot regenerate its validation outputs.
