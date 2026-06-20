# Quality thresholds

## Release rule

BI publication is blocked when:

- any critical rule returns one or more failing records;
- or the quality score is below 98%;
- or revenue-impacting review records remain unresolved.

## Quality score

```text
quality_score = 1 - critical_failures / total_orders
```

The score is useful as a monitoring KPI, but it does not replace the severity gate. A high score can still be blocked when a single critical rule affects revenue trust.

## Current run

| Metric | Value |
|---|---:|
| Total orders | 500 |
| Critical failures | 9 |
| Quality score | 98.2% |
| Publication status | Blocked |

## Blocking critical rules

- Duplicate IDs.
- Invalid dates.
- Missing customer or product references.
- Invalid quantities or discounts.
- Negative payment values.
- Payment without order.
- Completed order without payment.
- Payment amount mismatch.

## Warning rules

Warning rules are reviewed and trended, but do not block publication by themselves:

- inactive customer on completed order;
- inactive product on completed order;
- cancelled order with captured payment.
