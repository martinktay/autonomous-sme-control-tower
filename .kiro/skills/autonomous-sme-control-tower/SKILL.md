---
name: autonomous-sme-control-tower
description: Use this skill when building or modifying Autonomous SME Control Tower agents, prompts, BSI logic, workflow automation, dashboard flows, or hackathon submission artifacts.
---

# Autonomous SME Control Tower Skill

This skill provides implementation guidance for building the **Autonomous SME Control Tower**, a multi-agent AI system that monitors SME operations, diagnoses instability, simulates corrective strategies, executes workflows, and re-evaluates outcomes in a closed-loop system.

The goal is to build a working **agentic AI operational intelligence platform** for SMEs.

---

# When To Use This Skill

Use this skill when:

- Creating or updating FastAPI routers for invoices, signals, memory, stability, strategy, actions, voice, emails, finance, or insights
- Implementing AI agent modules
- Writing or refining prompt templates for Amazon Nova models
- Implementing Business Stability Index (BSI) calculations
- Building workflow automation using Nova Act
- Developing dashboard components for the Control Tower UI
- Working with middleware (org isolation, rate limiting, auth, tier enforcement)
- Working with utility modules (json_guard, prompt_loader, upload_validator, id_generator)
- Building finance document intelligence features
- Implementing email classification and task extraction
- Building marketing analytics or business analytics features
- Working with payment tracking and transaction management
- Writing documentation for architecture, README, or hackathon submissions

---

# Core System Concept

The Autonomous SME Control Tower operates as a **closed-loop operational control system**.

Core operational cycle: Signal Intake -> Risk Diagnosis -> Strategy Simulation -> Action Execution -> Re-evaluation -> Updated Stability Score

This loop must always remain functional.

---

# Agent Architecture

### Signal Intake Agent (signal_agent.py)
- Parse invoice documents, extract structured financial fields
- Classify email messages, assign urgency metadata, store signal records
- Uses: Nova 2 Lite, Nova Multimodal Embeddings

### Email Agent (email_agent.py)
- Classify inbound business emails, extract actionable tasks
- Uses: Nova 2 Lite

### Finance Agent (finance_agent.py)
- Classify finance documents (invoices, receipts, statements)
- Extract structured data, handle informal receipts
- Uses: Nova 2 Lite

### insights Agent (insights_agent.py)
- Generate business intelligence summaries and trend analysis
- insight types: revenue_trend, expense_alert, cashflow_warning, growth_opportunity, seasonal_pattern, supplier_risk, inventory_alert, customer_insight, market_trend, operational_efficiency, marketing_roi, customer_acquisition, campaign_performance, channel_effectiveness
- Uses: Nova 2 Lite

### Memory Agent (memory_agent.py)
- Generate embeddings, store contextual operational memory, semantic search
- Uses: Nova Multimodal Embeddings

### Risk Diagnosis Agent (risk_agent.py)
- Analyze financial signals, identify operational risks, calculate BSI
- Uses: Nova 2 Lite

### Strategy Simulation Agent (strategy_agent.py)
- Generate corrective strategies, predict BSI improvement
- Uses: Nova 2 Lite

### Action Execution Agent (action_agent.py)
- Execute operational workflows, trigger Nova Act automation
- Uses: Nova Act

### Re-evaluation Agent (reeval_agent.py)
- Recalculate BSI after execution, compute prediction accuracy
- Uses: Nova 2 Lite

### Voice Operations Agent (voice_agent.py)
- Provide spoken operational summaries, answer dashboard queries
- Uses: Nova 2 Sonic

### Alert Agent (alert_agent.py)
- Generate business alerts based on thresholds and anomalies

### Inventory Agent (inventory_agent.py)
- Analyse stock levels, predict reorder points

### Categorisation Agent (categorisation_agent.py)
- Auto-categorise transactions from uploaded data

### Mapping Agent (mapping_agent.py)
- Map CSV/Excel columns to platform schema fields

### WhatsApp Agent (whatsapp_agent.py)
- Extract business data from WhatsApp messages

### Supplier Agent (supplier_agent.py)
- Supplier intelligence and risk scoring

### Prediction Agent (prediction_agent.py)
- Inventory demand and sales predictions

### Desktop Sync Agent (desktop_sync_agent.py)
- Extract data from desktop accounting exports

### POS Agent (pos_agent.py)
- Parse POS export data

### Bank Agent (bank_agent.py)
- Bank statement reconciliation

### Branch Agent (branch_agent.py)
- Cross-branch performance analysis

### Forecasting Agent (forecasting_agent.py)
- Revenue and expense forecasting

---

# Services Layer

### DynamoDB Service (ddb_service.py)
- CRUD operations for all DynamoDB tables, org-scoped queries
- Validates org_id format: `^org-[a-z0-9]{12}$`

### Auth Service (auth_service.py)
- User registration and login, JWT token creation and validation
- Password hashing (PBKDF2, 600k iterations)
- Roles: owner, staff, super_admin

### Transaction Service (transaction_service.py)
- Transaction CRUD with payment status tracking (pending/paid/overdue/partial)
- Summary and cashflow aggregation

### Finance Service (finance_service.py)
- Finance document processing pipeline, classification and extraction

### Email Task Service (email_task_service.py)
- Email-to-task conversion pipeline, task persistence and retrieval

### Memory Service (memory_service.py)
- Embedding generation and storage, semantic search operations

### S3 Service (s3_service.py)
- Document upload and retrieval, pre-signed URL generation
- Server-side encryption enabled

### SES Service (ses_service.py)
- Email sending via Amazon SES, notification delivery

### Inventory Service (inventory_service.py)
- Inventory item management, stock level tracking

### Counterparty Service (counterparty_service.py)
- Supplier and customer management, balance tracking

### Alert Service (alert_service.py)
- Business alert generation and management

### Business Service (business_service.py)
- Business profile management

### Tier Service (tier_service.py)
- Pricing tier definitions and feature gating
- Upload and branch limit enforcement

### Upload Service (upload_service.py)
- Document upload pipeline, upload job tracking

---

# Middleware

### Auth Middleware (middleware/auth.py)
- JWT validation on protected routes, sets `request.state.user` and `request.state.tier`

### Org Isolation Middleware (middleware/org_isolation.py)
- Ensures all data access is scoped to the authenticated user's org_id

### Rate Limiter (middleware/rate_limiter.py)
- Tiered rate limiting per org (starter: 30/min, growth: 60/min, business: 120/min, enterprise: 300/min)

### Tier Enforcement (middleware/tier_enforcement.py)
- Blocks access to features above the user's pricing tier

---

# Utility Modules

### ID Generator (utils/id_generator.py)
- Centralized entity ID generation with prefixes
- Pattern: `{prefix}-{12_hex_chars}`
- Prefix mapping:
  - signal -> `sig-`, transaction -> `txn-`, invoice -> `inv-`, alert -> `alt-`
  - insight -> `ins-`, counterparty -> `ctp-`, inventory_item -> `itm-`, upload_job -> `job-`
  - evaluation -> `evl-`, action -> `act-`, strategy -> `str-`, bsi -> `bsi-`
  - business -> `biz-`, user -> `usr-`, branch -> `brn-`, task -> `tsk-`
  - email -> `eml-`, document -> `doc-`, org -> `org-`
- Usage: `from app.utils.id_generator import generate_id` then `generate_id("signal")` returns e.g. `sig-a1b2c3d4e5f6`

### JSON Guard (utils/json_guard.py)
- Safe JSON extraction from model responses, handles markdown fences

### Prompt Loader (utils/prompt_loader.py)
- Loads prompt templates from `/prompts/v1/`, supports variable substitution

### Upload Validator (utils/upload_validator.py)
- Validates uploaded file types and sizes

### Bedrock Client (utils/bedrock_client.py)
- Wrapper for Amazon Bedrock API calls

---

# Pydantic Models

| Model | File | Key Fields |
|-------|------|------------|
| Signal | signal.py | signal_id, org_id, source, urgency, payload |
| BSI | bsi.py | bsi_id, org_id, score, factors |
| Strategy | strategy.py | strategy_id, org_id, description, predicted_bsi |
| Action | action.py | action_id, org_id, strategy_id, status |
| Evaluation | evaluation.py | evaluation_id, org_id, action_id, accuracy |
| Email | email.py | email_id, org_id, subject, classification |
| Task | task.py | task_id, org_id, email_id, description |
| Invoice | invoice.py | invoice_id, org_id, vendor, amount |
| FinanceDocument | finance_document.py | document_id, org_id, doc_type, extracted_data |
| insight | insight.py | insight_id, org_id, insight_type, summary |
| Transaction | transaction.py | transaction_id, org_id, amount, category, payment_status |
| InventoryItem | inventory_item.py | item_id, org_id, name, quantity, reorder_point |
| Counterparty | counterparty.py | counterparty_id, org_id, name, type, balance |
| Alert | alert.py | alert_id, org_id, alert_type, severity, message |
| Business | business.py | business_id, org_id, name, tier (PricingTier enum) |
| Branch | branch.py | branch_id, org_id, business_id, name, location |
| User | user.py | user_id, org_id, email, role (owner/staff/super_admin), tier |
| UploadJob | upload_job.py | job_id, org_id, filename, status, row_count |

---

# DynamoDB Tables

| Table | Partition Key | Sort Key |
|-------|--------------|----------|
| signals | org_id | signal_id |
| bsi-scores | org_id | bsi_id |
| strategies | org_id | strategy_id |
| actions | org_id | action_id |
| evaluations | org_id | evaluation_id |
| embeddings | org_id | embedding_id |
| tasks | org_id | task_id |
| users | org_id | user_id |
| transactions | org_id | transaction_id |
| inventory | org_id | item_id |
| counterparties | org_id | counterparty_id |
| alerts | org_id | alert_id |
| businesses | org_id | business_id |
| branches | org_id | branch_id |
| insights | org_id | insight_id |
| upload-jobs | org_id | job_id |

---

# Frontend Pages

| Route | Page | Min Tier |
|-------|------|----------|
| /dashboard | Main dashboard | starter |
| /upload | Data upload | starter |
| /transactions | Transaction tracking & payments | starter |
| /finance | Finance overview | starter |
| /finance/upload | Finance doc upload | starter |
| /finance/export | Data export | starter |
| /alerts | Business alerts | starter |
| /inventory | Stock management | growth |
| /suppliers | Supplier management | growth |
| /supplier-intelligence | Supplier intel | growth |
| /predictions | Demand predictions | growth |
| /emails | Email inbox | growth |
| /emails/tasks | Email tasks | growth |
| /whatsapp | WhatsApp ingestion | growth |
| /pos | POS connector | business |
| /bank-sync | Bank sync | business |
| /sync | Desktop sync | business |
| /portal | AI analysis portal | business |
| /strategy | Strategy simulation | business |
| /actions | Action execution | business |
| /forecasting | Revenue forecasting | business |
| /voice | Voice assistant | business |
| /memory | Semantic search | business |
| /analytics | Business analytics | business |
| /analytics/marketing | Marketing insights | business |
| /branch-optimisation | Multi-branch ops | business |
| /pricing | Pricing & plans | public |
| /help | Help & FAQs | public |
| /login | Login | public |
| /register | Registration | public |
| /onboarding | New user onboarding | public |
| /admin | Super admin panel | super_admin only |

---

# Frontend Components

| Component | Purpose |
|-----------|---------|
| Sidebar | Tier-aware collapsible sidebar with grouped navigation |
| AppShell | Layout wrapper, shows sidebar for authenticated pages |
| NavBar | Top bar with logo, alerts, user menu, business name |
| BsiCard | BSI score display |
| RiskPanel | Risk diagnosis display |
| ActionLog | Action execution log |
| StrategyList | Strategy cards |
| insightsPanel | Business insights |
| CashflowChart | Cashflow visualisation |
| PnlSummary | Profit & loss summary |
| SalesTrendChart | Sales trend chart |
| TopProductsTable | Top products table |
| InventoryTable | Inventory list |
| StockAlertBadge | Low stock indicator |
| SupplierCard | Supplier info card |
| CurrencyDisplay | Naira/USD currency formatter |
| BSITrendChart | BSI trend over time |

---

# Sidebar Navigation Groups

| Group | Features | Min Tier |
|-------|----------|----------|
| Core | Dashboard, Upload, Transactions, Finance, Alerts | starter |
| Inventory & Supply | Stock, Suppliers, Supplier Intel, Predictions | growth |
| Communication | Emails, Tasks, WhatsApp | growth |
| Data Connectors | POS, Bank Sync, Desktop Sync | business |
| AI & Analytics | Analyse, Strategies, Actions, Forecasting, Voice, Search Memory | business |
| Marketing & Analytics | Business Analytics, Marketing insights | business |
| Multi-Branch | Branch Optimisation | business |

Bottom links: Admin Panel (super_admin only), Pricing & Plans, Help & FAQs

---

# Pricing Tiers

| Tier | Price (NGN) | Price (USD) | Uploads/mo | Branches |
|------|-------------|-------------|------------|----------|
| Starter | Free | Free | 20 | 1 |
| Growth | 14,900/mo | ~$9.50/mo | Unlimited | 1 |
| Business | 39,900/mo | ~$25/mo | Unlimited | 10 |
| Enterprise | 99,900/mo | ~$63/mo | Unlimited | Unlimited |

---

# ID Generation Rules

All entity IDs MUST be generated via `generate_id()` from `backend/app/utils/id_generator.py`.

```python
from app.utils.id_generator import generate_id

signal_id = generate_id("signal")   # -> sig-a1b2c3d4e5f6
txn_id = generate_id("transaction") # -> txn-f6e5d4c3b2a1
```

The `org_id` format `org-{12_hex}` is validated by `ddb_service.py` regex `^org-[a-z0-9]{12}$`.

---

# Prompt Templates

All prompts live in `/prompts/v1/`. Load via `prompt_loader.py`.

| File | Agent |
|------|-------|
| signal_invoice.md | Signal Agent |
| signal_email.md | Signal Agent |
| risk_diagnosis.md | Risk Agent |
| strategy_planning.md | Strategy Agent |
| reeval.md | Re-evaluation Agent |
| voice.md | Voice Agent |
| finance-document-classification.md | Finance Agent |
| finance-document-extraction.md | Finance Agent |
| finance-informal-receipt.md | Finance Agent |
| whatsapp-message-extraction.md | WhatsApp Agent |
| whatsapp-insight-summary.md | WhatsApp Agent |
| alert-generation.md | Alert Agent |
| inventory-analysis.md | Inventory Agent |
| transaction-categorisation.md | Categorisation Agent |
| field-mapping.md | Mapping Agent |
| pos-data-extraction.md | POS Agent |
| bank-reconciliation.md | Bank Agent |
| revenue-forecasting.md | Forecasting Agent |
| cross-branch-optimisation.md | Branch Agent |
| supplier-intelligence.md | Supplier Agent |
| inventory-prediction.md | Prediction Agent |
| desktop-sync-extraction.md | Desktop Sync Agent |

---

# Key Files

| File | Purpose |
|------|---------|
| backend/app/main.py | FastAPI app entry, CORS, middleware registration |
| backend/app/config.py | Environment config, AWS settings |
| backend/app/utils/id_generator.py | Centralized ID generation |
| backend/app/utils/json_guard.py | Safe JSON extraction |
| backend/app/utils/prompt_loader.py | Prompt template loading |
| backend/app/utils/upload_validator.py | File upload validation |
| backend/app/middleware/auth.py | JWT auth middleware |
| backend/app/middleware/org_isolation.py | Org data isolation |
| backend/app/middleware/rate_limiter.py | Tiered rate limiting |
| backend/app/middleware/tier_enforcement.py | Feature tier gating |
| backend/app/services/ddb_service.py | DynamoDB operations |
| backend/app/services/auth_service.py | Auth and JWT |
| backend/app/services/tier_service.py | Pricing tier logic |
| backend/seed_demo_data.py | Demo data seeder |
| backend/seed_realistic_data.py | Realistic Nigerian SME data seeder |
| backend/seed_test_users.py | Test user accounts seeder |
| backend/seed_super_admin.py | Super admin account seeder |
| frontend/lib/api.ts | API client (apiFetch) |
| frontend/lib/auth-context.tsx | Auth context provider |
| frontend/lib/org-context.tsx | Org context (derives from JWT) |
| frontend/components/Sidebar.tsx | Tier-aware sidebar navigation |
| frontend/components/AppShell.tsx | Authenticated layout shell |

---

# Guardrails

1. **Do NOT use `uuid.uuid4()` directly** — always use `generate_id(entity_type)` from `app.utils.id_generator`
2. **All records MUST include `org_id`** — multi-tenant isolation is mandatory
3. **All model responses MUST be valid JSON** — use `json_guard.safe_parse()` to extract
4. **All prompts MUST live in `/prompts/v1/`** — never inline prompts in Python code
5. **Prompt templates use `{variable}` substitution** — loaded via `prompt_loader.py`
6. **Never hardcode business-type-specific logic** — use the core shared schema
7. **Tier feature checks** — use `TierService.has_feature(tier, feature_name)` before granting access
8. **Password hashing** — PBKDF2 with 600,000 iterations (re-seed users after changing iterations)
9. **Rate limiting** — tiered per org: starter 30/min, growth 60/min, business 120/min, enterprise 300/min
10. **CORS** — restricted to configured allowed origins only
