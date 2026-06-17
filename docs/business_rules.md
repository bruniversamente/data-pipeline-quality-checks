# Business rules

## Scope

The pipeline simulates an order-to-payment analytical flow. Raw files are loaded from CSV, transformed into typed staging tables and validated before being used in analytical marts.

## Revenue calculation

Order item net amount is calculated as:

```text
net_item_amount = quantity * unit_price * (1 - discount_pct)
```

## Order total

Order total is the sum of all item net amounts for the order.

```text
order_total = sum(net_item_amount)
```

## Valid order statuses

Accepted order statuses:

- `Completed`
- `Cancelled`

## Valid payment statuses

Accepted payment statuses:

- `Captured`
- `Pending`
- `Failed`

## Payment matching

A completed order should have a payment record. Captured payment amount should match the calculated order total within a tolerance of 0.05.

## Cancelled orders

Cancelled orders should not contribute to revenue. A cancelled order with captured payment should be flagged for review.

## Product and customer references

Every order should have a valid customer. Every order item should have a valid product.

## Quality severity

- Critical: duplicated IDs, missing required references, invalid dates, payment mismatch.
- Warning: inactive customer or inactive product used in completed orders.
- Info: pending payment or non-critical operational status.
