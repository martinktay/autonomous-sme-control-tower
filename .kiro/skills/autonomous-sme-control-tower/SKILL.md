---
name: autonomous-sme-control-tower
description: Use this skill when building or modifying Autonomous SME Control Tower agents, prompts, NSI logic, workflow automation, dashboard flows, or hackathon submission artifacts.
---

# Autonomous SME Control Tower Skill

This skill provides implementation guidance for building the **Autonomous SME Control Tower**, a multi-agent AI system that monitors SME operations, diagnoses instability, simulates corrective strategies, executes workflows, and re-evaluates outcomes in a closed-loop system.

The goal is to build a working **agentic AI operational intelligence platform** for SMEs.

---

# When To Use This Skill

Use this skill when:

• Creating or updating FastAPI routers for invoices, signals, memory, stability, strategy, actions, voice, emails, finance, or insights  
• Implementing AI agent modules  
• Writing or refining prompt templates for Amazon Nova models  
• Implementing Nova Stability Index (NSI) calculations  
• Building workflow automation using Nova Act  
• Developing dashboard components for the Control Tower UI  
• Working with middleware (org isolation, rate limiting)  
• Working with utility modules (json_guard, prompt_loader, upload_validator)  
• Building finance document intelligence features  
• Implementing email classification and task extraction  
• Writing documentation for architecture, README, or hackathon submissions  

---

# Core System Concept

The Autonomous SME Control Tower operates as a **closed-loop operational control system**.

Core operational cycle:

```
Signal Intake (invoices, emails, finance docs)
    ↓
Risk Diagnosis
    ↓
Strategy Simulation
    ↓
Action Execution
    ↓
Re-evaluation
    ↓
Updated Stability Score
```

This loop must always remain functional.

The project's primary goal is to demonstrate this **autonomous decision loop**.

---

# Agent Architecture

The system contains several specialized agents.

### Signal Intake Agent (`signal_agent.py`)

**Responsibilities**:
• Parse invoice documents  
• Extract structured financial fields  
• Classify email messages  
• Assign urgency metadata  
• Store signal records  

**Uses**: Nova 2 Lite, Nova Multimodal Embeddings

---

### Email Agent (`email_agent.py`)

**Responsibilities**:
• Classify inbound business emails  
• Extract actionable tasks from email content  
• Assign priority and urgency  
• Generate structured task records  

**Uses**: Nova 2 Lite

---

### Finance Agent (`finance_agent.py`)

**Responsibilities**:
• Classify finance documents (invoices, receipts, statements)  
• Extract structured data from finance documents  
• Handle informal receipts and handwritten documents  
• Generate finance insights and analytics  

**Uses**: Nova 2 Lite

---

### Insights Agent (`insights_agent.py`)

**Responsibilities**:
• Generate business intelligence summaries  
• Analyze trends across signals and operations  
• Produce actionable insight recommendations  

**Uses**: Nova 2 Lite

---

### Memory Agent (`memory_agent.py`)

**Responsibilities**:
• Generate embeddings  
• Store contextual operational memory  
• Support semantic search of signals  

**Uses**: Nova Multimodal Embeddings

---

### Risk Diagnosis Agent (`risk_agent.py`)

**Responsibilities**:
• Analyze financial signals  
• Identify operational risks  
• Calculate Nova Stability Index  

**Uses**: Nova 2 Lite

---

### Strategy Simulation Agent (`strategy_agent.py`)

**Responsibilities**:
• Generate corrective strategies  
• Predict NSI improvement  
• Provide confidence scores  

**Example outputs**:
• Trigger invoice collections  
• Prioritize customer response  
• Delay vendor payment

**Uses**: Nova 2 Lite

---

### Action Execution Agent (`action_agent.py`)

**Responsibilities**:
• Execute operational workflows  
• Trigger Nova Act automation  
• Update operational state  
• Log executed actions  

**Uses**: Nova Act

---

### Re-evaluation Agent (`reeval_agent.py`)

**Responsibilities**:
• Recalculate NSI after execution  
• Compare predicted vs actual improvement  
• Compute prediction accuracy  

**Uses**: Nova 2 Lite

---

### Voice Operations Agent (`voice_agent.py`)

**Responsibilities**:
• Provide spoken operational summaries  
• Answer dashboard queries  

**Uses**: Nova 2 Sonic

---

# Services Layer

### DynamoDB Service (`ddb_service.py`)
• CRUD operations for all DynamoDB tables  
• Org-scoped queries  

### Finance Service (`finance_service.py`)
• Finance document processing pipeline  
• Document classification and extraction orchestration  

### Email Task Service (`email_task_service.py`)
• Email-to-task conversion pipeline  
• Task persistence and retrieval  

### Memory Service (`memory_service.py`)
• Embedding generation and storage  
• Semantic search operations  

### S3 Service (`s3_service.py`)
• Document upload and retrieval  
• Pre-signed URL generation  

### SES Service (`ses_service.py`)
• Email sending via Amazon SES  
• Notification delivery  

---

# Middleware

### Org Isolation (`org_isolation.py`)
• Enforces org_id on all requests  
• Prevents cross-tenant data access  

### Rate Limiter (`rate_limiter.py`)
• Request rate limiting per org  
• Protects against abuse  

---

# Utility Modules

### Bedrock Client (`bedrock_client.py`)
• Centralized Amazon Bedrock invocation  
• Model selection and configuration  

### JSON Guard (`json_guard.py`)
• Safe JSON parsing from model responses  
• Handles malformed output gracefully  

### Prompt Loader (`prompt_loader.py`)
• Loads prompt templates from prompts/v1/  
• Injects runtime variables  

### Upload Validator (`upload_validator.py`)
• Validates uploaded file types and sizes  
• Security checks on document uploads  

---

# Nova Stability Index (NSI)

The Nova Stability Index is the primary operational health metric.

**Range**: 0 – 100

**Example weighted risk components**:
• Cash runway risk  
• Invoice aging risk  
• Revenue concentration risk  
• Expense volatility risk  
• Customer response latency risk  

**The dashboard must display**:
• Current NSI  
• Stability trend  
• Top operational risks  

---

# Prompt Templates

All prompts live in `prompts/v1/`:

| File | Purpose |
|------|---------|
| `signal-invoice.md` | Invoice data extraction |
| `signal-email.md` | Email classification |
| `risk-diagnosis.md` | Risk analysis and NSI |
| `strategy-planning.md` | Strategy generation |
| `reeval.md` | Outcome re-evaluation |
| `voice.md` | Voice briefing script |
| `voice-query.md` | Voice query handling |
| `email-task-extraction.md` | Email-to-task extraction |
| `finance-document-classification.md` | Finance doc type classification |
| `finance-document-extraction.md` | Finance doc data extraction |
| `finance-informal-receipt.md` | Informal receipt handling |
| `finance-insights.md` | Finance analytics insights |
| `business-insights.md` | General business insights |

---

# Pydantic Models

All models live in `backend/app/models/`:

| File | Purpose |
|------|---------|
| `signal.py` | Signal records |
| `invoice.py` | Invoice data |
| `nsi.py` | NSI scores and sub-indices |
| `strategy.py` | Strategy proposals |
| `action.py` | Executed actions |
| `evaluation.py` | Re-evaluation results |
| `email.py` | Email classification and tasks |
| `finance_document.py` | Finance document types |
| `task.py` | Task records |

---

# Frontend Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/dashboard` | Main control tower dashboard |
| `/upload` | Document upload |
| `/strategy` | Strategy simulation view |
| `/actions` | Action log and execution |
| `/voice` | Voice operations interface |
| `/emails` | Email inbox and classification |
| `/emails/tasks` | Extracted email tasks |
| `/finance` | Finance document hub |
| `/finance/upload` | Finance doc upload |
| `/finance/review` | Finance doc review queue |
| `/finance/export` | Finance data export |
| `/memory` | Semantic memory browser |
| `/portal` | Organization portal |
| `/help` | Help and FAQ |

---

# Frontend Components

Key UI components in `frontend/components/`:

• `NsiCard` – NSI score display  
• `RiskPanel` – Risk breakdown  
• `StrategyList` – Strategy proposals  
• `ActionLog` – Action execution log  
• `InsightsPanel` – Business insights  
• `CashflowChart` – Cash flow visualization  
• `PnlSummary` – Profit and loss summary  
• `FinanceAnalytics` – Finance analytics dashboard  
• `FinanceInsightsPanel` – Finance-specific insights  
• `ReconciliationPanel` – Document reconciliation  
• `ReviewQueue` – Finance doc review queue  
• `NSITrendChart` – NSI trend over time  
• `VoiceWidget` – Voice interaction widget  
• `OrgSwitcher` – Multi-tenant org selector  
• `NavBar` – Navigation bar  
• `FaqAccordion` – Help page FAQ  
• `charts/BarChart` – Bar chart component  
• `charts/PieChart` – Pie chart component  

---

# Project Rules

### Infrastructure

• Prefer Docker-first development  
• Store uploaded documents in S3  
• Store operational state in DynamoDB  

### Multi-Tenant Readiness

All records must include `org_id`. This preserves SaaS readiness.

### Prompt Management

Prompts must live in `prompts/v1/`.

**Rules**:
• Use strict JSON responses  
• Define explicit output schema  
• Avoid free-form text responses  
• Validate responses before storing  
• Load prompts via `prompt_loader.py`  

### Data Storage

DynamoDB tables:

```
autonomous-sme-signals
autonomous-sme-nsi-scores
autonomous-sme-strategies
autonomous-sme-actions
autonomous-sme-evaluations
```

Each record should include `org_id` and `created_at`.

### Automation Guidance

For the MVP, implement one reliable Nova Act workflow.

**Recommended workflow**: Trigger invoice collection reminder.

This should:
• Update invoice status  
• Log action  
• Trigger follow-up  

---

# Key Files

```
backend/app/agents/       # Agent logic modules
backend/app/routers/      # API route handlers
backend/app/models/       # Pydantic data models
backend/app/services/     # Business logic services
backend/app/utils/        # Helper functions (bedrock_client, json_guard, prompt_loader, upload_validator)
backend/app/middleware/   # Org isolation, rate limiting
prompts/v1/              # Versioned prompt templates
frontend/app/            # Next.js pages
frontend/components/     # React UI components
docs/                    # Documentation
demo-data/               # Demo CSV data and upload scripts
```

---

# Documentation Requirements

Important documentation files:

```
docs/architecture.md
docs/nsi-method.md
docs/devlog.md
docs/demo-script.md
docs/implementation-status.md
docs/infrastructure-setup.md
docs/setup-guide.md
```

---

# Hackathon Positioning

When generating descriptions for the AWS Nova Hackathon, emphasize:

• Multi-agent AI architecture  
• Deep Nova model integration  
• Closed-loop operational intelligence  
• Measurable operational impact  
• Workflow automation  
• Finance document intelligence  
• Email-to-task automation  

The Autonomous SME Control Tower should be presented as:

```
An autonomous operational intelligence system for SMEs
```

---

# Africa SME Commercial Readiness

## Market Focus

The platform is evolving from a hackathon demo to a commercially-ready product targeting:
- Nigeria and West Africa SMEs
- East Africa informal and semi-formal SMEs
- Supermarkets, mini marts, kiosks, artisans, food vendors, agriculture, professional services

## Strategic Positioning

This is NOT accounting software. It is an AI business survival and growth assistant for SMEs operating in African market realities.

## Supported Business Segments

- Supermarkets and retail stores
- Mini marts and kiosks
- Artisans and trade businesses
- Beauty and salon SMEs
- Food vendors and catering SMEs
- Agriculture SMEs
- Professional service SMEs

## Schema Architecture

- Core shared schema plus business-type extension layers
- Core entities: business, branch, user, document, transaction, revenue_record, expense_record, payment, counterparty, supplier, customer, inventory_item, product_or_service, alert, insight, upload_job, integration_source
- Extension fields (JSON) or modular extension tables per business category
- Unified analytics queries must work across all business categories

## Document Ingestion Channels

- PDF upload, Image upload, Excel upload, CSV upload
- Camera capture, WhatsApp ingestion, Email ingestion
- POS export ingestion, Manual entry forms

## Pricing Tiers (NGN)

| Tier | Price | Target |
|------|-------|--------|
| Starter | Free | Informal SMEs, small traders |
| Growth | ₦15,000–25,000/mo | Active supermarkets and SMEs |
| Business | ₦40,000–70,000/mo | Multi-branch SMEs |
| Enterprise | ₦100,000–250,000/mo | Large retail chains |

## Implementation Phases

1. Phase 1 (Nigeria Launch): Pricing page, flexible onboarding, manual ingestion, basic AI dashboards, supermarket pilot
2. Phase 2 (Automation): WhatsApp ingestion, desktop sync agent, supplier intelligence, inventory prediction
3. Phase 3 (Deep Integrations): POS connectors, bank sync, AI forecasting engine, cross-branch optimisation

---

# Guardrails and Anti-Drift Rules

## CRITICAL: Do Not

- Do NOT invent features, endpoints, or models not defined in the spec or existing codebase
- Do NOT create new DynamoDB tables without explicit spec approval
- Do NOT add new agents without following the nova-agent-builder build sequence
- Do NOT hardcode prompts in Python files — always use prompts/v1/ via prompt_loader.py
- Do NOT skip Pydantic validation on any model output
- Do NOT bypass org_id isolation on any data operation
- Do NOT create frontend pages without corresponding backend API endpoints
- Do NOT introduce new AWS services without documenting in docs/infrastructure-setup.md
- Do NOT generate placeholder or mock data in production code paths
- Do NOT use free-form text responses from Nova models — always enforce JSON schema
- Do NOT create pricing or billing logic without explicit spec tasks
- Do NOT assume business segment schemas — use extension fields pattern only

## CRITICAL: Always

- Always validate all model responses through json_guard.py
- Always scope all data queries by org_id
- Always load prompts via prompt_loader.py
- Always use Pydantic models for request/response contracts
- Always follow the build sequence: Model → Prompt → Agent → Service → Router → Frontend
- Always update docs/devlog.md when architecture changes
- Always include created_at timestamps on persistent records
- Always handle file upload validation through upload_validator.py
- Always test with the existing test patterns in backend/tests/

---

# Reference Resources

See:

- resources/nsi-method.md
- resources/architecture.md
- resources/prompts-guide.md
