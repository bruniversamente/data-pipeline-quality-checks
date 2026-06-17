# Data

This folder contains synthetic raw data used by the data pipeline quality project. No real customer, financial or private data is used.

## Files

- `raw/sample_customers.csv`: customer dimension source.
- `raw/sample_products.csv`: product dimension source.
- `raw/sample_orders.csv`: order header source.
- `raw/sample_order_items.csv`: order item source.
- `raw/sample_payments.csv`: payment source.

## Notes

The raw files intentionally include a small number of quality issues so the validation layer has something to detect. Examples include duplicate records, missing references and payment mismatches.

The script `scripts/generate_raw_data.py` creates a larger dataset under `data/generated/`.
