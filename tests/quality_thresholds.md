# Quality thresholds

This file defines suggested thresholds for pipeline monitoring.

## Critical rules

Critical rules should return zero failing records before publishing executive reports.

- Duplicate order IDs
- Duplicate customer IDs
- Duplicate product IDs
- Invalid order dates
- Missing customer references
- Missing product references
- Negative quantities
- Negative payment amounts
- Payment amount mismatch

## Warning rules

Warning rules can be monitored and reviewed, but may not block publication depending on business context.

- Inactive customer used in completed order
- Inactive product used in completed order
- Pending payment
- Cancelled order with captured payment

## Suggested quality score

```text
quality_score = 1 - critical_failures / total_checked_records
```

## Suggested release rule

A BI refresh should be blocked when:

- any critical rule returns more than zero records
- or the quality score is below 98 percent
