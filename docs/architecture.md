# Architecture

## System Overview

The Autonomous SME Control Tower is a multi-agent AI system built on AWS Bedrock Nova models. It provides autonomous operational intelligence for small and medium enterprises through a continuous closed-loop cycle.

## Multi-Agent Architecture

### Signal Intake Agent
- Extracts structured data from invoices using Nova 2 Lite
- Classifies business emails by category and priority
- Stores raw documents in S3 and metadata in DynamoDB
- Generates embeddings for semantic search

### Risk Diagnosis Agent
- Analyzes operational signals to calculate Business Stability Index (BSI)
- Computes sub-indices: liquidity, revenue stability, operational latency, vendor risk
- Identifies top risks with explanations
- Stores BSI snapshots with timestamps

### Strategy Simulation Agent
- Generates 2-3 corrective strategies based on risk diagnosis
- Estimates predicted BSI improvement for each option
- Provides confidence scores and cost estimates
- Marks strategies as automatable or manual

### Action Execution Agent
- Executes automatable strategies via Nova Act
- Logs execution status and results
- Tracks predicted vs actual outcomes
- Handles errors gracefully

### Re-evaluation Agent
- Recalculates BSI after action execution
- Compares predicted vs actual improvement
- Computes prediction accuracy metrics
- Suggests BSI weight adjustments based on learnings

### Memory Agent
- Generates embeddings using Nova Multimodal Embeddings
- Enables semantic search across operational history
- Retrieves similar past situations for context

### Voice Agent
- Generates spoken briefings using Nova 2 Sonic
- Summarizes current stability, risks, and recent actions
- Provides audio responses to dashboard queries

### Categorisation Agent
- AI-powered transaction categorisation using Nova
- Maps raw transaction descriptions to standard categories

### Mapping Agent
- AI field mapping for multi-channel document ingestion
- Maps uploaded CSV/Excel columns to system fields with confidence scores

### Inventory Agent
- Stock analysis, reorder alerts, expiry warnings
- Feeds inventory signals into BSI calculation

### Alert Agent
- Generates alerts from signals, inventory, and financial data
- Respects tier-based alert limits

### Finance Agent
- Document classification (invoice, receipt, statement, informal)
- Data extraction from financial documents
- Informal receipt handling for African market

### Insights Agent
- Generates AI business insights (tax, cashflow, profitability)
- Produces actionable recommendations in plain language

## Data Flow

```
1. INGEST
   Upload → S3 Storage → Signal Extraction → DynamoDB

2. DIAGNOSE
   Signals → Risk Analysis → BSI Calculation → Store Score

3. SIMULATE
   BSI + Risks → Strategy Generation → Rank Options

4. EXECUTE
   Select Strategy → Nova Act Execution → Log Results

5. EVALUATE
   Recalculate BSI → Compare Predictions → Update Accuracy
```

## Storage Architecture

### DynamoDB Tables
- `autonomous-sme-signals`: Signal records keyed by org_id
- `autonomous-sme-bsi-scores`: BSI snapshots keyed by org_id + timestamp
- `autonomous-sme-strategies`: Strategy simulations
- `autonomous-sme-actions`: Action execution logs
- `autonomous-sme-businesses`: Business registration and onboarding state
- `autonomous-sme-branches`: Multi-location branch records
- `autonomous-sme-transactions`: Unified revenue/expense/payment tracking
- `autonomous-sme-inventory`: Stock items with quantity, reorder levels, expiry
- `autonomous-sme-counterparties`: Supplier and customer records with balances
- `autonomous-sme-alerts`: AI-generated business alerts
- `autonomous-sme-upload-jobs`: Multi-channel document ingestion job tracking

### S3 Buckets
- `autonomous-sme-documents`: Invoice files, raw documents, uploaded spreadsheets

## Entity Model

All entities are scoped by `org_id` (aliased as `business_id`) for multi-tenant isolation. Each model includes an `extension_attrs` dict for business-type-specific fields.

- Business → has many Branches, Transactions, Inventory Items, Counterparties, Alerts
- Transaction → categorised as revenue/expense/payment/transfer, linked to Counterparty
- InventoryItem → tracks quantity, reorder level, expiry, cost price, sell price
- Counterparty → supplier or customer with balance tracking
- UploadJob → tracks multi-channel document ingestion lifecycle (upload → map → process)
- Alert → AI-generated notifications with severity, read status, tier-based limits
- FinanceDocument → classified and extracted financial documents (invoices, receipts, statements)

## Pricing Tier System

Four tiers enforce feature access via middleware:
- Starter (free): 20 uploads/month, 1 branch, 5 alerts/week
- Growth: Unlimited uploads, daily alerts, cashflow insights
- Business: Multi-branch (up to 10), forecasting, staff analytics
- Enterprise: Unlimited branches, POS integration, real-time alerts

## API Design

RESTful endpoints organized by domain:
- `/api/invoices` - Invoice upload and extraction
- `/api/signals` - Signal retrieval
- `/api/memory` - Embeddings search
- `/api/stability` - BSI calculation and history
- `/api/strategy` - Strategy simulation
- `/api/actions` - Action execution and history
- `/api/voice` - Voice briefings
- `/api/orchestration` - Full closed-loop execution
- `/api/businesses` - Business registration, onboarding, branch management
- `/api/pricing` - Tier definitions and current tier lookup
- `/api/transactions` - Transaction CRUD, summaries, cashflow
- `/api/inventory` - Stock management, alerts, analytics
- `/api/counterparties` - Supplier/customer CRUD, balance tracking
- `/api/alerts` - Alert retrieval and read status
- `/api/upload-jobs` - Multi-channel document ingestion pipeline
- `/api/finance` - Document upload, insights, analytics, P&L, export
- `/api/emails` - Email ingestion, task extraction, SES sending

## Frontend Architecture

Next.js 14 app with pages:
- `/` - Africa-focused landing page with business type showcase and pricing preview
- `/onboarding` - Multi-step business registration wizard
- `/pricing` - Tier comparison with NGN/USD toggle
- `/portal` - One-click closed-loop demo
- `/dashboard` - BSI, risks, actions, inventory/supplier overview
- `/upload` - Invoice upload interface
- `/strategy` - Strategy simulation view
- `/actions` - Action history
- `/transactions` - Transaction list with filters and summary
- `/inventory` - Stock management with alert badges
- `/suppliers` - Supplier/customer management
- `/alerts` - Alert centre
- `/finance` - Financial document management, P&L, cashflow, export
- `/emails` - Email ingestion and task management
- `/memory` - Semantic search
- `/voice` - Voice briefings
- `/help` - FAQ and guides

Reusable components:
- `BsiCard` - Displays BSI with color coding
- `RiskPanel` - Lists top risks
- `ActionLog` - Shows recent actions
- `InsightsPanel` - AI-generated business insights
- `CurrencyDisplay` - Formatted currency display (NGN, USD, GBP, EUR)
- `InventoryTable` - Stock list with alert badges
- `StockAlertBadge` - Low stock / expiry visual indicator
- `SupplierCard` - Supplier balance summary
- `CashflowChart` - Cashflow visualization
- `PnlSummary` - Profit and loss summary
- `OrgSwitcher` - Multi-org context switcher

## Technology Stack

- Backend: FastAPI + Python + boto3
- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- AI: AWS Bedrock Nova models
- Storage: DynamoDB + S3
- Infrastructure: Docker + Docker Compose
