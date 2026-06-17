# Pipeline blueprint

This document describes the proposed pipeline structure.

## Layer 1 - Raw

Goal: load source files without changing business meaning.

Inputs:

- customers
- products
- orders
- order items
- payments

All fields are initially loaded as strings or permissive types to avoid failing the pipeline before validation.

## Layer 2 - Staging

Goal: standardize field names, parse types and prepare data for validation.

Examples:

- Parse dates with `TRY_CAST`.
- Convert numeric fields to decimal values.
- Normalize status fields.
- Create calculated item amount.

## Layer 3 - Quality checks

Goal: identify records that should be reviewed before BI consumption.

Rule groups:

- Completeness
- Uniqueness
- Validity
- Referential integrity
- Business consistency

## Layer 4 - Analytical marts

Goal: create clean tables for BI and KPI reporting.

Outputs:

- `mart_orders`
- `mart_order_items`
- `dq_summary`

## Suggested production improvements

- Add scheduling with Airflow, Prefect or GitHub Actions.
- Persist data quality history by run date.
- Add alerting for critical failures.
- Add source-level quality scoring.
- Add incremental loading.
