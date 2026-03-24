# Tasks: Africa SME Commercial Readiness

## Phase 1: Nigeria Launch Foundation

### Task 1: Core Entity Models
- [x] Create `backend/app/models/business.py` with Business, BusinessType enum, PricingTier enum
- [x] Create `backend/app/models/branch.py` with Branch model
- [x] Create `backend/app/models/transaction.py` with Transaction model (unified revenue/expense)
- [x] Create `backend/app/models/inventory_item.py` with InventoryItem model
- [x] Create `backend/app/models/counterparty.py` with Counterparty model
- [x] Create `backend/app/models/upload_job.py` with UploadJob model
- [x] Create `backend/app/models/alert.py` with Alert model (separate from existing action alerts)
- [x] Create `backend/app/models/insight.py` with Insight model
- [x] All models include `extension_attrs: Dict[str, Any] = {}` field
- [x] Update `backend/app/models/__init__.py` with new exports
- [x] Add extension attribute JSON schemas per business type in `backend/app/config.py`

### Task 2: Business and Onboarding Backend
- [x] Create `backend/app/services/business_service.py` — Business CRUD, default branch creation, module activation
- [x] Create `backend/app/routers/businesses.py` — POST/GET/PUT /api/businesses, onboarding complete endpoint
- [x] Create `backend/app/routers/onboarding.py` — Guided onboarding flow endpoints
- [x] Create `backend/app/routers/branches.py` — Branch CRUD
- [x] Add DynamoDB table config for `autonomous-sme-businesses` and `autonomous-sme-branches` to config.py
- [x] Ensure backward compatibility: existing org_id records work as business_id alias

### Task 3: Pricing Tier System
- [x] Create `backend/app/middleware/tier_enforcement.py` — Middleware checking feature access against tier
- [x] Create `backend/app/services/tier_service.py` — Tier definitions, usage tracking, limit checking
- [x] Create `backend/app/routers/pricing.py` — GET /api/pricing/tiers, GET /api/pricing/current
- [x] Add tier limits configuration to config.py (uploads/month, branches, alerts/week, feature list)
- [x] Wire tier_enforcement middleware into FastAPI app in main.py

### Task 4: Multi-Channel Document Ingestion
- [x] Create `backend/app/services/upload_service.py` — Upload job lifecycle, file parsing (CSV, Excel, image, PDF)
- [x] Create `backend/app/routers/upload_jobs.py` — POST create job, GET status, POST mapping, POST process
- [x] Add Excel parsing support (openpyxl) to requirements.txt
- [x] Create `backend/app/agents/mapping_agent.py` — AI field mapping using Nova
- [x] Create `prompts/v1/field-mapping.md` — Prompt for column-to-field mapping
- [x] Extend upload_validator.py to support .xlsx, .csv, .jpeg, .png file types
- [x] Add DynamoDB table config for `autonomous-sme-upload-jobs`

### Task 5: Transaction and Revenue/Expense Tracking
- [x] Create `backend/app/services/transaction_service.py` — Transaction CRUD, categorisation, summaries
- [x] Create `backend/app/routers/transactions.py` — CRUD, summary, cashflow endpoints
- [x] Create `backend/app/agents/categorisation_agent.py` — AI transaction categorisation
- [x] Create `prompts/v1/transaction-categorisation.md` — Categorisation prompt
- [x] Add DynamoDB table config for `autonomous-sme-transactions`
- [x] Wire transaction data into existing BSI calculation (risk_agent)

### Task 6: Inventory Management (Supermarket Focus)
- [x] Create `backend/app/services/inventory_service.py` — Inventory CRUD, stock alerts, analytics
- [x] Create `backend/app/routers/inventory.py` — CRUD, alerts, analytics endpoints
- [x] Create `backend/app/agents/inventory_agent.py` — Stock analysis, reorder alerts, expiry warnings
- [x] Create `prompts/v1/inventory-analysis.md` — Inventory risk analysis prompt
- [x] Add DynamoDB table config for `autonomous-sme-inventory`
- [x] Wire inventory signals into BSI calculation

### Task 7: Counterparty (Supplier/Customer) Management
- [x] Create `backend/app/services/counterparty_service.py` — Counterparty CRUD, balance tracking
- [x] Create `backend/app/routers/counterparties.py` — CRUD, balance endpoints
- [x] Add auto-creation of counterparties from ingested documents (in signal_agent and finance_agent)
- [x] Add DynamoDB table config for `autonomous-sme-counterparties`

### Task 8: Alert System
- [x] Create `backend/app/services/alert_service.py` — Alert creation, delivery, tier-based limits
- [x] Create `backend/app/routers/alerts.py` — GET alerts, PUT mark read
- [x] Create `backend/app/agents/alert_agent.py` — Generate alerts from signals and inventory
- [x] Create `prompts/v1/alert-generation.md` — Alert generation prompt
- [x] Add DynamoDB table config for `autonomous-sme-alerts`

### Task 9: Pricing Page Frontend
- [x] Create `frontend/app/pricing/page.tsx` — Full pricing page with hero, tier cards, comparison table, ROI section, CTA
- [x] Create `frontend/components/CurrencyDisplay.tsx` — Formatted ₦/$/£ display
- [x] Add NGN/USD toggle to pricing page
- [x] Ensure mobile-first responsive layout
- [x] Add pricing link to NavBar

### Task 10: Onboarding Flow Frontend
- [x] Create `frontend/app/onboarding/page.tsx` — Onboarding wizard container with step progress
- [x] Wire onboarding to business registration API
- [x] Add sample demo data option for exploration

### Task 11: Landing Page Update
- [x] Update `frontend/app/page.tsx` — Africa-focused hero copy, business type showcase, pricing preview section, "Start Free" CTA
- [x] Add business type icons section showing supported SME categories
- [x] Add pricing preview section linking to full pricing page
- [x] Update hero messaging to survival/growth focus
- [x] Ensure mobile-first responsive design

### Task 12: Supermarket Dashboard Enhancements
- [x] Create `frontend/components/InventoryTable.tsx` — Inventory list with stock alert badges
- [x] Create `frontend/components/StockAlertBadge.tsx` — Low stock / expiry visual indicator
- [x] Create `frontend/components/SupplierCard.tsx` — Supplier balance summary card
- [x] Update `frontend/app/dashboard/page.tsx` — Conditionally show inventory/supplier panels
- [x] Add sales trend chart for supermarket view
- [x] Add top products table

### Task 13: Inventory and Supplier Pages
- [x] Create `frontend/app/inventory/page.tsx` — Inventory management page
- [x] Create `frontend/app/suppliers/page.tsx` — Supplier/customer management page
- [x] Create `frontend/app/transactions/page.tsx` — Transaction list with filters
- [x] Create `frontend/app/alerts/page.tsx` — Alert centre page
- [x] Add new pages to NavBar navigation
- [x] Add API functions to `frontend/lib/api.ts` for new endpoints

### Task 14: Currency and Localisation
- [x] Add currency formatting utility supporting NGN (₦), USD ($), GBP (£), EUR (€)
- [x] Update all existing currency displays to use CurrencyDisplay component
- [x] Add locale-aware date formatting
- [x] Update business language throughout UI to avoid accounting jargon

### Task 15: Infrastructure Updates
- [x] Add new DynamoDB table definitions to `infra/setup-aws.sh`
- [x] Update `docker-compose.yml` if needed for new dependencies
- [x] Add `openpyxl` to `backend/requirements.txt` for Excel support
- [x] Update `.env.example` with any new configuration variables
- [x] Update `docs/architecture.md` with new entity model and data flow

---

## Phase 2: Automation (Future)

### Task 16: WhatsApp Ingestion
- [x] WhatsApp Business API integration for document receiving
- [x] WhatsApp insight delivery (daily/weekly summaries)

### Task 17: Desktop Sync Agent
- [x] Background agent for automated POS data sync
- [x] File watcher for designated export folders

### Task 18: Supplier Intelligence
- [x] Supplier reliability scoring
- [x] Alternative supplier recommendations
- [x] Price comparison across suppliers

### Task 19: Inventory Prediction
- [x] Demand forecasting using historical sales data
- [x] Automated reorder suggestions
- [x] Seasonal pattern detection

---

## Phase 3: Deep Integrations (Future)

### Task 20: POS Connectors
- [x] Direct integration with popular Nigerian POS systems
- [x] Near real-time sales data sync

### Task 21: Bank Sync
- [x] Bank statement import
- [x] Automated reconciliation

### Task 22: AI Forecasting Engine
- [x] Revenue forecasting
- [x] Expense prediction
- [x] Cash runway projection

### Task 23: Cross-Branch Optimisation
- [x] Stock transfer recommendations between branches
- [x] Branch performance benchmarking
- [x] Consolidated multi-branch reporting
