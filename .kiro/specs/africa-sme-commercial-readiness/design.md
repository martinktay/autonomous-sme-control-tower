# Design: Africa SME Commercial Readiness

## Architecture Overview

This design extends the existing Autonomous SME Control Tower with commercial-grade multi-tenant architecture, flexible schema support, Africa-focused UI, and tiered pricing. The existing agent pipeline (signal → risk → strategy → action → reeval) remains intact and is enhanced with new entity types and business-type-aware intelligence.

---

## Flexible Schema Design

### Design Principle

Core shared schema + JSON extension fields per business type. This avoids schema redesign when adding new SME categories while keeping unified analytics possible.

### DynamoDB Table Design

All tables use `org_id` (now aliased as `business_id`) as partition key. New tables are added alongside existing ones.

#### New Tables

```
autonomous-sme-businesses        PK: business_id
autonomous-sme-branches          PK: business_id, SK: branch_id
autonomous-sme-users             PK: business_id, SK: user_id
autonomous-sme-transactions      PK: business_id, SK: transaction_id
autonomous-sme-revenue-records   PK: business_id, SK: record_id
autonomous-sme-expense-records   PK: business_id, SK: record_id
autonomous-sme-payments          PK: business_id, SK: payment_id
autonomous-sme-counterparties    PK: business_id, SK: counterparty_id
autonomous-sme-inventory         PK: business_id, SK: item_id
autonomous-sme-products          PK: business_id, SK: product_id
autonomous-sme-alerts            PK: business_id, SK: alert_id
autonomous-sme-insights          PK: business_id, SK: insight_id
autonomous-sme-upload-jobs       PK: business_id, SK: job_id
```

#### Existing Tables (Retained)

```
autonomous-sme-signals           (invoice/email signals — still used by agent pipeline)
autonomous-sme-bsi-scores        (BSI snapshots)
autonomous-sme-strategies        (strategy proposals)
autonomous-sme-actions           (action execution logs)
autonomous-sme-evaluations       (reeval results)
autonomous-sme-embeddings        (semantic memory)
autonomous-sme-tasks             (email-extracted tasks)
```

### Core Entity Models

#### Business Model

```python
class Business(BaseModel):
    business_id: str                    # UUID, replaces org_id for new records
    business_name: str
    business_type: BusinessType         # enum: supermarket, mini_mart, kiosk, artisan, salon, food_vendor, agriculture, professional_service, other
    country: str = "NG"
    state_region: Optional[str] = None
    currency: str = "NGN"
    phone: Optional[str] = None
    email: Optional[str] = None
    pricing_tier: PricingTier = PricingTier.STARTER  # starter, growth, business, enterprise
    onboarding_complete: bool = False
    modules_enabled: List[str] = []     # e.g. ["inventory", "supplier_tracking"]
    extension_attrs: Dict[str, Any] = {}
    created_at: datetime
```

#### Branch Model

```python
class Branch(BaseModel):
    branch_id: str
    business_id: str
    branch_name: str
    address: Optional[str] = None
    is_primary: bool = True
    extension_attrs: Dict[str, Any] = {}
    created_at: datetime
```

#### Transaction Model (Unified)

```python
class Transaction(BaseModel):
    transaction_id: str
    business_id: str
    branch_id: Optional[str] = None
    transaction_type: str               # "revenue" | "expense" | "payment" | "transfer"
    category: Optional[str] = None      # AI-classified or user-set
    amount: float
    currency: str = "NGN"
    counterparty_id: Optional[str] = None
    counterparty_name: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    payment_status: str = "pending"     # pending, paid, overdue, partial
    source_document_id: Optional[str] = None
    extension_attrs: Dict[str, Any] = {}
    created_at: datetime
```

#### Inventory Item Model

```python
class InventoryItem(BaseModel):
    item_id: str
    business_id: str
    branch_id: Optional[str] = None
    product_id: Optional[str] = None
    name: str
    sku: Optional[str] = None
    quantity_on_hand: float = 0
    unit: str = "units"
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_point: Optional[float] = None
    category: Optional[str] = None
    extension_attrs: Dict[str, Any] = {}  # supermarket: shelf_location, expiry_date, supplier_lead_days
    last_updated: datetime
    created_at: datetime
```

#### Counterparty Model

```python
class Counterparty(BaseModel):
    counterparty_id: str
    business_id: str
    name: str
    counterparty_type: str              # "supplier" | "customer"
    phone: Optional[str] = None
    email: Optional[str] = None
    balance_owed: float = 0.0           # what we owe them
    balance_owing: float = 0.0          # what they owe us
    last_transaction_date: Optional[datetime] = None
    extension_attrs: Dict[str, Any] = {}
    created_at: datetime
```

#### Upload Job Model

```python
class UploadJob(BaseModel):
    job_id: str
    business_id: str
    branch_id: Optional[str] = None
    file_count: int = 1
    file_names: List[str] = []
    status: str = "pending"             # pending, mapping, processing, complete, failed
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    field_mappings: Optional[Dict[str, str]] = None  # source_col → target_field
    unmapped_fields: List[str] = []
    errors: List[str] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
```

#### Alert Model

```python
class Alert(BaseModel):
    alert_id: str
    business_id: str
    branch_id: Optional[str] = None
    alert_type: str                     # low_stock, overdue_payment, cashflow_warning, expense_spike, supplier_issue
    severity: str                       # critical, warning, info
    title: str
    description: str                    # plain language
    recommended_action: Optional[str] = None
    is_read: bool = False
    created_at: datetime
```

#### Insight Model

```python
class Insight(BaseModel):
    insight_id: str
    business_id: str
    insight_type: str                   # sales_trend, profitable_product, cost_saving, seasonal_pattern
    title: str
    description: str
    data: Dict[str, Any] = {}           # supporting metrics
    created_at: datetime
```

### Extension Attributes by Business Type

```json
{
  "supermarket": {
    "inventory_item": ["shelf_location", "reorder_point", "supplier_lead_days", "expiry_date", "barcode"],
    "transaction": ["pos_terminal_id", "cashier_id", "receipt_number"]
  },
  "salon": {
    "product_or_service": ["service_duration_mins", "stylist_name", "booking_required"],
    "transaction": ["appointment_id", "client_name"]
  },
  "agriculture": {
    "inventory_item": ["harvest_date", "storage_condition", "grade"],
    "transaction": ["farm_plot", "season"]
  },
  "food_vendor": {
    "inventory_item": ["preparation_date", "shelf_life_hours"],
    "transaction": ["delivery_zone"]
  }
}
```

---

## Pricing Tier Enforcement

### Middleware Design

Add `PricingTierMiddleware` to the existing middleware stack (alongside `OrgIsolationMiddleware` and `RateLimiterMiddleware`).

```python
TIER_LIMITS = {
    "starter": {
        "uploads_per_month": 20,
        "branches": 1,
        "alerts_per_week": 5,
        "features": ["manual_upload", "basic_dashboard", "weekly_summary", "data_export"]
    },
    "growth": {
        "uploads_per_month": -1,  # unlimited
        "branches": 1,
        "alerts_per_week": -1,
        "features": ["manual_upload", "basic_dashboard", "daily_alerts", "cashflow_insights",
                     "inventory_risk", "supplier_tracking", "whatsapp_summary", "data_export"]
    },
    "business": {
        "uploads_per_month": -1,
        "branches": 10,
        "alerts_per_week": -1,
        "features": ["*", "multi_branch", "auto_sync", "advanced_forecasting", "staff_analytics"]
    },
    "enterprise": {
        "uploads_per_month": -1,
        "branches": -1,
        "alerts_per_week": -1,
        "features": ["*", "realtime_pos", "ai_pricing", "supplier_intelligence", "executive_dashboard"]
    }
}
```

---

## UI Design

### Pricing Page Layout

```
┌─────────────────────────────────────────────────────────┐
│  HERO SECTION                                           │
│  "AI Business Control for African SMEs"                 │
│  "Know your cashflow, stock risks, and profit           │
│   in one screen"                                        │
│  [Start Free]  [See Pricing ↓]                          │
├─────────────────────────────────────────────────────────┤
│  TIER CARDS (side-by-side, mobile: stacked)             │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Starter  │ │ Growth   │ │ Business │ │Enterprise│  │
│  │ ₦0/mo    │ │₦15-25K/mo│ │₦40-70K/mo│ │₦100-250K │  │
│  │ [FREE]   │ │          │ │ POPULAR  │ │          │  │
│  │ badge    │ │          │ │ badge    │ │          │  │
│  │          │ │          │ │          │ │          │  │
│  │ • Manual │ │ • Unlim  │ │ • Multi  │ │ • RT POS │  │
│  │   upload │ │   uploads│ │   branch │ │ • AI     │  │
│  │ • Basic  │ │ • Daily  │ │ • Auto   │ │   pricing│  │
│  │   dash   │ │   alerts │ │   sync   │ │ • Exec   │  │
│  │ • 1 loc  │ │ • Cash   │ │ • Adv    │ │   dash   │  │
│  │ • 5 alert│ │   flow   │ │   forecast│ │ • Dedic  │  │
│  │ • Weekly │ │ • Inv    │ │ • Staff  │ │   onboard│  │
│  │   summary│ │   risk   │ │   analyt │ │          │  │
│  │          │ │ • Supplier│ │          │ │          │  │
│  │[Start    │ │[Upgrade] │ │[Upgrade] │ │[Contact] │  │
│  │ Free]    │ │          │ │          │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  FEATURE COMPARISON TABLE                               │
│  Feature          Starter  Growth  Business  Enterprise │
│  Document upload    20/mo   Unlim   Unlim     Unlim    │
│  Branches           1       1       10        Unlim    │
│  AI Alerts          5/wk    Daily   Daily     RT       │
│  Cashflow insights  —       ✓       ✓         ✓        │
│  Inventory risk     —       ✓       ✓         ✓        │
│  Multi-branch       —       —       ✓         ✓        │
│  POS integration    —       —       —         ✓        │
│  ...                                                    │
├─────────────────────────────────────────────────────────┤
│  ROI SECTION                                            │
│  "Prevent stock losses" | "Improve cashflow" |          │
│  "Track supplier obligations"                           │
├─────────────────────────────────────────────────────────┤
│  FINAL CTA                                              │
│  "Start free. Upgrade when you grow."                   │
│  [Start Free]                                           │
└─────────────────────────────────────────────────────────┘
```

### Onboarding Flow (Supermarket)

```
Step 1: Create Account
┌─────────────────────────────────┐
│  Welcome to SME Control Tower   │
│                                 │
│  Business Name: [___________]   │
│  Phone/Email:   [___________]   │
│  Country:       [Nigeria ▼  ]   │
│  State:         [Lagos   ▼  ]   │
│                                 │
│  [Continue →]                   │
│  ━━━━━○───────── Step 1 of 5   │
└─────────────────────────────────┘

Step 2: Select Business Type
┌─────────────────────────────────┐
│  What type of business?         │
│                                 │
│  ┌─────────┐  ┌─────────┐      │
│  │ 🛒      │  │ 🏪      │      │
│  │Supermart│  │Mini Mart │      │
│  └─────────┘  └─────────┘      │
│  ┌─────────┐  ┌─────────┐      │
│  │ ✂️      │  │ 🍲      │      │
│  │ Salon   │  │Food Vend│      │
│  └─────────┘  └─────────┘      │
│  ┌─────────┐  ┌─────────┐      │
│  │ 🌾      │  │ 🔧      │      │
│  │ Farm    │  │ Artisan │      │
│  └─────────┘  └─────────┘      │
│                                 │
│  [Continue →]                   │
│  ━━━━━━━━━○─── Step 2 of 5     │
└─────────────────────────────────┘

Step 3: Enable Modules
┌─────────────────────────────────┐
│  We recommend these for your    │
│  supermarket:                   │
│                                 │
│  ☑ Inventory Intelligence       │
│  ☑ Supplier Tracking            │
│  ☑ Sales Analytics              │
│  ☐ Staff Analytics (Business+)  │
│                                 │
│  [Continue →]                   │
│  ━━━━━━━━━━━━━○ Step 3 of 5    │
└─────────────────────────────────┘

Step 4: Upload First Data
┌─────────────────────────────────┐
│  Upload your sales or stock     │
│  data to get started            │
│                                 │
│  ┌─────────────────────────┐    │
│  │  📁 Drop CSV/Excel here │    │
│  │  or click to browse     │    │
│  └─────────────────────────┘    │
│                                 │
│  Or try with sample data →      │
│                                 │
│  [Continue →]                   │
│  ━━━━━━━━━━━━━━━━━○ Step 4/5   │
└─────────────────────────────────┘

Step 5: Field Mapping (if needed)
┌─────────────────────────────────┐
│  We mapped your columns:        │
│                                 │
│  "Product"  → Product Name  ✓   │
│  "Qty Sold" → Quantity      ✓   │
│  "Price"    → Selling Price ✓   │
│  "Date"     → Date          ✓   │
│  "Cashier"  → [Select field ▼]  │
│                                 │
│  [Confirm & Process →]          │
│  ━━━━━━━━━━━━━━━━━━━━━○ 5/5    │
└─────────────────────────────────┘

→ Dashboard with first insights
```

### Updated Landing Page Structure

```
┌─────────────────────────────────────────────────────────┐
│  NAV: Logo | Dashboard | Pricing | Help | [Start Free]  │
├─────────────────────────────────────────────────────────┤
│  HERO                                                   │
│  "Control Your Business Before Problems Start"          │
│  "AI that helps African SMEs sell more and lose less"   │
│                                                         │
│  • Works with receipts, POS exports, manual records     │
│  • Simple dashboards in everyday business language      │
│  • Designed for African payment realities               │
│  • Free plan to get started                             │
│                                                         │
│  [Start Free]  [See How It Works ↓]                     │
├─────────────────────────────────────────────────────────┤
│  BUSINESS TYPES SUPPORTED                               │
│  🛒 Supermarkets  🏪 Mini Marts  ✂️ Salons              │
│  🍲 Food Vendors  🌾 Farms       🔧 Artisans            │
├─────────────────────────────────────────────────────────┤
│  HOW IT WORKS (3 steps)                                 │
│  1. Upload your data (receipts, POS, Excel)             │
│  2. AI analyses and shows your business health          │
│  3. Get alerts and recommendations to grow              │
├─────────────────────────────────────────────────────────┤
│  FEATURES GRID (existing, enhanced)                     │
├─────────────────────────────────────────────────────────┤
│  SOCIAL PROOF / TESTIMONIALS (future)                   │
├─────────────────────────────────────────────────────────┤
│  PRICING PREVIEW                                        │
│  "Start free. Upgrade when you grow."                   │
│  [See Full Pricing →]                                   │
├─────────────────────────────────────────────────────────┤
│  FINAL CTA                                              │
│  [Start Free — No Credit Card Required]                 │
└─────────────────────────────────────────────────────────┘
```

### Dashboard Enhancements for Supermarkets

When `business_type == "supermarket"`, the dashboard adds:

```
┌─────────────────────────────────────────────────────────┐
│  BSI Score  │  Revenue Today  │  Expenses Today         │
│  [72/100]   │  ₦485,000       │  ₦312,000               │
├─────────────┼─────────────────┼─────────────────────────┤
│  ALERTS                                                 │
│  🔴 Low stock: Rice (5kg) — 12 units left, reorder at 50│
│  🟡 Overdue: Supplier ABC owes delivery since 3 days    │
│  🟢 Sales up 15% this week vs last week                 │
├─────────────────────────────────────────────────────────┤
│  SALES TREND (chart)  │  TOP PRODUCTS (table)           │
│  [line chart 7 days]  │  1. Rice 5kg — ₦45K             │
│                       │  2. Palm Oil — ₦38K              │
│                       │  3. Indomie — ₦29K               │
├─────────────────────────────────────────────────────────┤
│  INVENTORY RISKS      │  SUPPLIER OBLIGATIONS            │
│  • 8 items below      │  • Total owed: ₦1.2M            │
│    reorder point      │  • Due this week: ₦340K          │
│  • 3 items expiring   │  • Overdue: ₦180K                │
│    within 7 days      │                                  │
├─────────────────────────────────────────────────────────┤
│  CASHFLOW SURVIVAL    │  AI INSIGHTS                     │
│  "At current burn     │  "Your rice margin dropped 8%    │
│   rate, you have 23   │   this month. Consider switching │
│   days of runway"     │   supplier or adjusting price."  │
└─────────────────────────────────────────────────────────┘
```

---

## Backend Architecture Changes

### New Routers

```
backend/app/routers/
  businesses.py       # Business CRUD, onboarding
  branches.py         # Branch management
  inventory.py        # Inventory CRUD, stock alerts
  counterparties.py   # Supplier/customer management
  transactions.py     # Unified transaction management
  upload_jobs.py      # Batch upload and field mapping
  alerts.py           # Alert management
  pricing.py          # Tier info and feature gating
  onboarding.py       # Guided onboarding flow
```

### New Agents

```
backend/app/agents/
  inventory_agent.py      # Stock analysis, reorder alerts, expiry warnings
  categorisation_agent.py # AI transaction categorisation
  mapping_agent.py        # AI field mapping for CSV/Excel uploads
  alert_agent.py          # Alert generation from signals
```

### New Services

```
backend/app/services/
  business_service.py     # Business entity management
  inventory_service.py    # Inventory operations
  upload_service.py       # Upload job processing pipeline
  alert_service.py        # Alert creation and delivery
  tier_service.py         # Pricing tier enforcement
```

### New Middleware

```
backend/app/middleware/
  tier_enforcement.py     # Check feature access against pricing tier
```

### New Prompts

```
prompts/v1/
  field-mapping.md              # AI column mapping for CSV/Excel
  transaction-categorisation.md # Auto-categorise revenue/expense
  inventory-analysis.md         # Stock risk analysis
  supermarket-insights.md       # Supermarket-specific intelligence
  alert-generation.md           # Generate alerts from signals
```

---

## API Endpoints (New)

### Business & Onboarding
- `POST /api/businesses` — Register new business
- `GET /api/businesses/{business_id}` — Get business details
- `PUT /api/businesses/{business_id}` — Update business
- `POST /api/businesses/{business_id}/onboarding/complete` — Mark onboarding done

### Branches
- `POST /api/branches` — Create branch
- `GET /api/branches` — List branches for business
- `PUT /api/branches/{branch_id}` — Update branch

### Inventory
- `GET /api/inventory` — List inventory items
- `POST /api/inventory` — Add inventory item
- `PUT /api/inventory/{item_id}` — Update item
- `GET /api/inventory/alerts` — Get stock alerts (low stock, expiry)
- `GET /api/inventory/analytics` — Turnover rates, fast/slow movers

### Transactions
- `GET /api/transactions` — List transactions (filterable)
- `POST /api/transactions` — Create transaction
- `GET /api/transactions/summary` — Revenue vs expense summary
- `GET /api/transactions/cashflow` — Cashflow over time

### Counterparties
- `GET /api/counterparties` — List suppliers/customers
- `POST /api/counterparties` — Create counterparty
- `GET /api/counterparties/{id}/balance` — Balance summary

### Upload Jobs
- `POST /api/upload-jobs` — Create upload job with files
- `GET /api/upload-jobs/{job_id}` — Get job status
- `POST /api/upload-jobs/{job_id}/mapping` — Submit field mapping
- `POST /api/upload-jobs/{job_id}/process` — Process after mapping confirmed

### Alerts
- `GET /api/alerts` — List alerts for business
- `PUT /api/alerts/{alert_id}/read` — Mark alert as read

### Pricing
- `GET /api/pricing/tiers` — Get tier definitions
- `GET /api/pricing/current` — Get current business tier and usage

---

## Frontend New Pages

```
frontend/app/
  pricing/page.tsx          # Pricing page
  onboarding/page.tsx       # Guided onboarding wizard
  onboarding/type/page.tsx  # Business type selection
  onboarding/modules/page.tsx
  onboarding/upload/page.tsx
  onboarding/mapping/page.tsx
  inventory/page.tsx        # Inventory management
  suppliers/page.tsx        # Supplier/customer management
  transactions/page.tsx     # Transaction list
  alerts/page.tsx           # Alert centre
```

### New Components

```
frontend/components/
  PricingCard.tsx           # Tier card with features and CTA
  PricingTable.tsx          # Feature comparison table
  OnboardingWizard.tsx      # Step-by-step onboarding
  BusinessTypeSelector.tsx  # Visual business type picker
  FieldMappingUI.tsx        # Column mapping interface
  InventoryTable.tsx        # Inventory list with alerts
  StockAlertBadge.tsx       # Low stock / expiry indicator
  SupplierCard.tsx          # Supplier balance summary
  CurrencyDisplay.tsx       # Formatted currency with symbol
  TierBadge.tsx             # Current tier indicator
  UpgradePrompt.tsx         # Feature-gated upgrade CTA
```

---

## Backward Compatibility

- Existing `org_id` field maps to `business_id` — add alias support
- Existing signal/BSI/strategy/action/evaluation pipeline unchanged
- Existing frontend pages continue to work
- New entities are additive, not replacing existing ones
- Migration path: existing demo orgs get `business_type: "other"` and `pricing_tier: "starter"`

---

## Error Handling

Same patterns as existing system:
- Validation errors: HTTP 422
- Feature gating: HTTP 403 with upgrade message
- Processing errors: HTTP 500 with structured error
- Upload mapping failures: HTTP 200 with status "mapping_required"

---

## Security

- All new tables partitioned by business_id
- Tier enforcement middleware prevents feature abuse
- Upload validation extended for Excel/CSV (max file size, row limits per tier)
- Rate limiting adjusted per tier (higher limits for paid tiers)
