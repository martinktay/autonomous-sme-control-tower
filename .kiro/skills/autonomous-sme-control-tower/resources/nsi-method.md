# NSI Method (Nova Stability Index)

## Overview

The Nova Stability Index (NSI) is a composite metric that measures the operational health and stability of an SME based on multiple business signals.

## Sub-Indices

The NSI is calculated from several sub-indices:

1. **Financial Health** - Cash flow, payment patterns, invoice aging
2. **Operational Efficiency** - Process completion rates, turnaround times
3. **Risk Exposure** - Identified threats, compliance issues
4. **Growth Trajectory** - Revenue trends, customer acquisition

## Calculation Method

```
NSI = weighted_average([
  financial_health * 0.4,
  operational_efficiency * 0.3,
  risk_exposure * 0.2,
  growth_trajectory * 0.1
])
```

Each sub-index is scored 0-100, with higher scores indicating better stability.

## Prediction Accuracy

- Track NSI predictions vs actual outcomes
- Refine weights based on historical accuracy
- Use embeddings to find similar historical patterns

## Implementation Notes

- Store NSI calculations in DynamoDB with timestamp
- Trigger re-calculation on new signal ingestion
- Use Nova embeddings to find similar business patterns
