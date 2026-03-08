# Nova Stability Index (NSI) Method

## Overview

The Nova Stability Index is a composite metric (0-100) that quantifies the operational health and stability of an SME based on multiple business signals.

## Sub-Indices

### 1. Liquidity Index (30% weight)
Measures cash flow health and payment capacity.

Factors:
- Cash runway (months of operating expenses)
- Payment velocity (days to pay invoices)
- Outstanding receivables aging

Scoring:
- 80-100: Strong cash position, >6 months runway
- 60-79: Adequate liquidity, 3-6 months runway
- 40-59: Tight cash flow, 1-3 months runway
- 0-39: Critical liquidity risk, <1 month runway

### 2. Revenue Stability Index (25% weight)
Measures revenue predictability and concentration risk.

Factors:
- Revenue volatility (month-over-month variance)
- Customer concentration (% from top 3 customers)
- Revenue trend direction

Scoring:
- 80-100: Stable, diversified revenue
- 60-79: Moderate volatility or concentration
- 40-59: High volatility or concentration risk
- 0-39: Unstable revenue base

### 3. Operational Latency Index (25% weight)
Measures operational efficiency and responsiveness.

Factors:
- Invoice processing time
- Customer response time
- Task completion rates

Scoring:
- 80-100: Efficient operations, fast response
- 60-79: Acceptable performance
- 40-59: Delays and inefficiencies
- 0-39: Severe operational bottlenecks

### 4. Vendor Risk Index (20% weight)
Measures supply chain and vendor relationship health.

Factors:
- Vendor concentration
- Payment terms compliance
- Vendor relationship quality

Scoring:
- 80-100: Diversified, healthy vendor relationships
- 60-79: Moderate vendor dependency
- 40-59: High vendor concentration risk
- 0-39: Critical vendor dependencies

## NSI Calculation

```
NSI = (liquidity_index × 0.30) + 
      (revenue_stability_index × 0.25) + 
      (operational_latency_index × 0.25) + 
      (vendor_risk_index × 0.20)
```

## Interpretation

- **80-100**: Strong stability - business is healthy and resilient
- **60-79**: Moderate stability - some risks but manageable
- **40-59**: Elevated risk - corrective action recommended
- **0-39**: Critical instability - urgent intervention needed

## Prediction Accuracy

The system tracks prediction accuracy by:
1. Recording predicted NSI improvement before action
2. Measuring actual NSI change after action
3. Computing accuracy score: `1 - |predicted - actual| / predicted`
4. Adjusting sub-index weights based on historical accuracy

## Implementation Notes

- NSI is recalculated after each new signal ingestion
- Historical NSI scores enable trend analysis
- Re-evaluation agent refines weights over time
- All calculations are auditable and logged
