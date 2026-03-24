# Product Manager Prompt — Autonomous SME Control Tower

## Current State (March 2026)

### What It Is
An AI-powered operations platform for small and medium enterprises. Business owners upload invoices, emails, and financial documents. The system analyses them using AWS Bedrock Nova models, calculates a business health score (BSI — Business Stability Index, 0–100), identifies risks, generates strategies, executes automatable actions, and re-evaluates outcomes in a closed loop.

### Target Market
- SMEs in Nigeria (96% of all businesses), UK (99.9%), and globally
- Business owners without in-house accountants, data analysts, or IT teams
- Companies doing ₦5M–₦500M / £50K–£5M annual revenue

### Core Loop (Working)
1. **Ingest** — Upload invoices (PDF/image), paste emails, upload financial docs
2. **Diagnose** — AI calculates BSI with 4 sub-indices (cash flow, revenue stability, operations speed, vendor risk)
3. **Simulate** — Generates 2–3 strategies when BSI < 70, with predicted improvement and confidence scores
4. **Execute** — Runs automatable strategies via Nova Act
5. **Evaluate** — Recalculates BSI, measures prediction accuracy, feeds back into the loop

### What's Built
- **Backend**: FastAPI with 12 API routers, 8 AI agents, 5 services, 9 Pydantic models, 224 passing tests
- **Frontend**: Next.js 14 with 11 pages, 14 components, org switcher for multi-tenancy demo
- **Infrastructure**: Docker-compose, DynamoDB (7 tables), S3, Bedrock (4 Nova models)
- **Security**: Org isolation middleware, rate limiting, CORS lockdown, deep health checks

### Feature Inventory
| Feature | Status | User Value |
|---------|--------|------------|
| Invoice upload + extraction | ✅ Working | Core data ingestion |
| Email ingestion + classification | ✅ Working | Automated email triage |
| Task extraction from emails | ✅ Working | Auto-generates action items |
| BSI health score | ✅ Working | Single number business health |
| Risk diagnosis | ✅ Working | Early warning system |
| Strategy simulation | ✅ Working | AI-generated improvement plans |
| Action execution | ✅ Working | Automated workflow execution |
| Re-evaluation loop | ✅ Working | Measures strategy effectiveness |
| Finance doc intelligence | ✅ Working | Cashflow, P&L, reconciliation |
| Voice briefing | ✅ Working | Audio summary of business state |
| Semantic memory search | ✅ Working | Natural language data search |
| Multi-org switching | ✅ Working | Demo multiple businesses |

### Known Gaps
- No real OCR pipeline (placeholder text extraction)
- No authentication (X-Org-ID header only)
- No email sending capability (SES not configured)
- No push notifications or alerts
- No pagination on list endpoints
- No prompt injection protection

### Key Metrics to Track (Proposed)
- Time from upload to first insight (target: < 10s)
- BSI prediction accuracy (target: > 70%)
- Tasks auto-generated per email (measure AI extraction quality)
- User sessions per week per org
- Documents processed per org per month

### Competitive Positioning
Unlike QuickBooks/Xero (accounting tools) or generic AI assistants, this is a closed-loop autonomous system that doesn't just report — it diagnoses, recommends, acts, and learns. The BSI score gives SME owners a single number to understand their business health, similar to a credit score but for operations.

### Next Priorities (Recommended)
1. **Real OCR** — Integrate AWS Textract for actual document extraction
2. **Authentication** — JWT-based auth with Cognito
3. **Email sending** — SES integration for auto-replies and notifications
4. **Mobile-responsive polish** — Ensure all pages work well on phones
5. **Onboarding flow** — Guided first-time experience
6. **Alerting** — Push/email alerts when BSI drops below threshold
