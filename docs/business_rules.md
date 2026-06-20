# Business rules

## Scope

The pipeline validates an order-to-payment analytical flow before BI publication. It receives customers, products, orders, order items and payments as raw CSV files, then creates staging tables, quality checks and analytical marts.

## Revenue calculation

Item revenue is calculated as:

```text
net_item_amount = quantity * unit_price * (1 - discount_pct)
```

Order revenue is the sum of item revenue by order.

Cancelled orders are excluded from BI-ready revenue.

## Payment matching

A completed order must have a payment record.

Captured payment amount must match the calculated order total with a tolerance of 0.05.

Payment totals and item totals are aggregated separately before comparison. This avoids multiplying payment values when an order has more than one item.

## Data quality status

Each order receives one of two statuses:

- `Ready`: can feed BI marts.
- `Review`: must be investigated before executive reporting.

An order is marked as `Review` when it has missing customer, invalid date, missing payment, missing product reference, invalid item quantity or payment mismatch.

## Publication gate

Executive BI publication is blocked when:

- at least one critical rule fails;
- or the quality score is below 98%;
- or revenue-impacting records are unresolved.

## Severity model

Critical rules block publication:

- duplicate customer ID;
- duplicate order ID;
- duplicate order item ID;
- invalid order date;
- missing customer reference;
- missing product reference;
- invalid quantity;
- invalid discount;
- negative payment amount;
- payment without order;
- completed order without payment;
- payment amount mismatch.

Warning rules require monitoring, but may not block publication by themselves:

- cancelled order with captured payment;
- inactive customer on completed order;
- inactive product on completed order.
