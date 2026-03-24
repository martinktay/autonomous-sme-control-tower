# Autonomous SME Control Tower - System Design

## Architecture Overview

The Autonomous SME Control Tower follows a multi-agent architecture coordinated by a FastAPI backend.

### System Layers

1. **User Interface Layer** - Next.js frontend
2. **Agent Orchestration Layer** - FastAPI backend coordinating agents
3. **AI Reasoning Layer** - AWS Bedrock Nova models
4. **Operational Memory Layer** - Embeddings and semantic search
5. **Automation Layer** - Nova Act workflow execution
6. **Evaluation Layer** - Prediction accuracy measurement

---

## Frontend

**Framework**: Next.js 14 + TypeScript + Tailwind CSS

### Main Pages

- **dashboard** - BSI overview, risks, and action history
- **upload** - Invoice and email submission interface
- **memory** - Semantic search across operational signals
- **strategy** - Strategy simulation and selection
- **actions** - Action execution history and status
- **portal** - One-click closed-loop demo
- **voice** - Voice query interface and audio briefings

### Key Components

- **BSI Card** - Displays current BSI score with color-coded health indicator
- **Risk Panel** - Lists top operational risks ranked by severity
- **Strategy List** - Shows generated strategies with predicted impact
- **Action Log** - Displays action execution history with timestamps
- **Voice Widget** - Voice query input and audio response playback

---

## Backend

**Framework**: FastAPI + Python

### Backend Responsibilities

- API routing
- Agent orchestration
- Nova model invocation
- State management
- Automation triggering

### Modules

```
backend/app/
├── routers/       # API endpoint handlers
├── agents/        # Agent logic modules
├── services/      # AWS service integrations
├── models/        # Pydantic data models
└── utils/         # Helper functions
```

---

## AI Models

The system leverages AWS Bedrock Nova models for all AI capabilities.

### Nova 2 Lite

**Used for**:
- Invoice extraction
- Email classification
- Risk diagnosis
- Strategy simulation
- Re-evaluation reasoning

### Nova Multimodal Embeddings

**Used for**:
- Contextual memory
- Semantic similarity search

### Nova 2 Sonic

**Used for**:
- Voice interaction
- Spoken summaries

### Nova Act

**Used for**:
- Workflow automation
- Autonomous action execution

---

## Agents

### Signal Intake Agent

**Responsibilities**:
- Parse invoices
- Classify emails
- Generate signal metadata
- Store signal records

**Prompt Templates**:
- `/prompts/v1/signal_invoice.md`
- `/prompts/v1/signal_email.md`

---

### Memory Agent

**Responsibilities**:
- Generate embeddings using Nova Multimodal Embeddings
- Store contextual memory
- Enable semantic search across operational history

---

### Risk Diagnosis Agent

**Responsibilities**:
- Analyze signals
- Compute BSI (Business Stability Index)
- Identify operational risks

**Prompt Templates**:
- `/prompts/v1/risk_diagnosis.md`

**BSI Calculation**:
```
BSI = (liquidity_index × 0.30) + 
      (revenue_stability_index × 0.25) + 
      (operational_latency_index × 0.25) + 
      (vendor_risk_index × 0.20)
```

---

### Strategy Simulation Agent

**Responsibilities**:
- Generate corrective strategies
- Estimate BSI improvement
- Provide confidence scores

**Prompt Templates**:
- `/prompts/v1/strategy_planning.md`

---

### Action Execution Agent

**Responsibilities**:
- Execute automated workflows using Nova Act
- Log actions
- Update system state

**Supported Workflows**:
- Update invoice status
- Trigger follow-up actions

---

### Re-evaluation Agent

**Responsibilities**:
- Recompute BSI after action execution
- Compare predicted vs actual improvement
- Compute prediction accuracy

**Prompt Templates**:
- `/prompts/v1/reeval.md`

**Accuracy Calculation**:
```python
actual_improvement = new_bsi - old_bsi
prediction_accuracy = 1 - abs(predicted_improvement - actual_improvement) / predicted_improvement
```

---

### Voice Agent

**Responsibilities**:
- Generate spoken operational summaries using Nova 2 Sonic
- Process voice queries
- Provide audio briefings

**Prompt Templates**:
- `/prompts/v1/voice.md`

**Supported Queries**:
- "How stable is my business?"
- "Which invoices are overdue?"

---

## Data Storage

### DynamoDB Tables

All tables use `org_id` as partition key for multi-tenancy.

- **autonomous-sme-signals** - Signal records (invoices, emails)
- **autonomous-sme-bsi-scores** - BSI snapshots with timestamps
- **autonomous-sme-strategies** - Generated strategies
- **autonomous-sme-actions** - Action execution logs
- **autonomous-sme-evaluations** - Prediction accuracy records

### S3 Buckets

- **autonomous-sme-documents** - Invoice documents and raw files

**Structure**:
```
autonomous-sme-documents/
├── invoices/{org_id}/{invoice_id}.pdf
├── documents/{org_id}/{document_id}.{ext}
└── logs/{org_id}/{date}/{log_file}.json
```

---

## Data Flow

The system follows a closed-loop operational cycle:

### 1. INGEST
User uploads invoice or email → Signal Agent extracts data → Store in DynamoDB → Generate embeddings → Store in Memory Agent

### 2. DIAGNOSE
Retrieve signals for org_id → Risk Agent calculates BSI → Compute sub-indices → Identify operational risks → Store BSI snapshot

### 3. SIMULATE
Strategy Agent proposes corrective actions → Estimate BSI improvement → Provide confidence scores → Store strategies

### 4. EXECUTE
User selects strategy → Nova Act executes workflow → Action Agent logs execution → Update system state

### 5. EVALUATE
Re-evaluation Agent recalculates BSI → Compare predicted vs actual → Compute prediction accuracy → Dashboard displays updated state

---

## API Endpoints

### Invoice Router (`/api/invoices`)
- `POST /api/invoices/upload` - Upload and process invoice
- `GET /api/invoices/{invoice_id}` - Retrieve invoice details
- `GET /api/invoices` - List invoices for org_id

### Signal Router (`/api/signals`)
- `POST /api/signals/email` - Submit email for processing
- `GET /api/signals` - List signals for org_id
- `GET /api/signals/{signal_id}` - Retrieve signal details

### Memory Router (`/api/memory`)
- `POST /api/memory/search` - Semantic search across signals
- `GET /api/memory/embeddings/{signal_id}` - Retrieve embedding

### Stability Router (`/api/stability`)
- `POST /api/stability/calculate` - Calculate current BSI
- `GET /api/stability/history` - Retrieve BSI trend
- `GET /api/stability/risks` - Get current risk assessment

### Strategy Router (`/api/strategy`)
- `POST /api/strategy/simulate` - Generate strategies
- `GET /api/strategy` - List strategies for org_id
- `GET /api/strategy/{strategy_id}` - Retrieve strategy details

### Action Router (`/api/actions`)
- `POST /api/actions/execute` - Execute workflow
- `GET /api/actions` - List action history
- `GET /api/actions/{action_id}` - Retrieve action details

### Voice Router (`/api/voice`)
- `POST /api/voice/query` - Process voice query
- `GET /api/voice/briefing` - Generate operational briefing

### Orchestration Router (`/api/orchestration`)
- `POST /api/orchestration/run-loop` - Execute full closed-loop cycle

---

## Data Models

### Core Pydantic Models

#### Invoice Model
```python
class Invoice(BaseModel):
    invoice_id: str
    org_id: str
    vendor_name: str
    amount: float
    currency: str
    due_date: datetime
    description: str
    status: str = "pending"
    created_at: datetime
    s3_key: Optional[str]
```

#### Email Model
```python
class Email(BaseModel):
    email_id: str
    org_id: str
    sender: str
    subject: str
    classification: str  # payment_reminder, customer_inquiry, operational_message, other
    content: str
    created_at: datetime
```

#### Signal Model
```python
class Signal(BaseModel):
    signal_id: str
    org_id: str
    signal_type: str  # invoice, email
    content: dict
    embedding_ref: Optional[str]
    created_at: datetime
    processing_status: str = "processed"
```

#### BSI Snapshot Model
```python
class BSISnapshot(BaseModel):
    bsi_id: str
    org_id: str
    bsi_score: float  # 0-100
    liquidity_index: float
    revenue_stability_index: float
    operational_latency_index: float
    vendor_risk_index: float
    confidence: str  # high, medium, low
    reasoning: dict
    timestamp: datetime
```

#### Strategy Model
```python
class Strategy(BaseModel):
    strategy_id: str
    org_id: str
    bsi_snapshot_id: str
    description: str
    predicted_bsi_improvement: float
    confidence_score: float  # 0-1
    automation_eligibility: bool
    reasoning: str
    created_at: datetime
```

#### Action Execution Model
```python
class ActionExecution(BaseModel):
    execution_id: str
    org_id: str
    strategy_id: str
    action_type: str
    target_entity: str
    execution_status: str  # success, failed, pending
    error_reason: Optional[str]
    timestamp: datetime
```

#### Evaluation Model
```python
class Evaluation(BaseModel):
    evaluation_id: str
    org_id: str
    execution_id: str
    old_bsi: float
    new_bsi: float
    predicted_improvement: float
    actual_improvement: float
    prediction_accuracy: float
    timestamp: datetime
```

---

## Error Handling

### Error Categories

1. **Validation Errors** - Invalid input data (HTTP 422)
2. **Extraction Errors** - Failed signal processing (HTTP 500)
3. **Model Invocation Errors** - Bedrock API failures (HTTP 503)
4. **Parsing Errors** - Invalid JSON from models (HTTP 500)
5. **Storage Errors** - DynamoDB/S3 failures (HTTP 500)
6. **Workflow Execution Errors** - Nova Act failures (logged, HTTP 200 with failed status)
7. **Data Isolation Violations** - Cross-org access attempts (HTTP 403)

### Error Recovery Patterns

- **Graceful Degradation**: Continue with reduced functionality when non-critical operations fail
- **Retry Logic**: Exponential backoff for transient errors (max 3 retries)
- **Circuit Breaker**: Stop calling failing services after 5 consecutive failures

### Logging Requirements

All errors logged as structured JSON with:
- Timestamp (ISO 8601)
- Error type and message
- Stack trace
- Request context (org_id)
- Operation and input parameters

---

## Testing Strategy

### Property-Based Testing

**Framework**: `hypothesis` library for Python

**Configuration**:
- Minimum 100 iterations per property test
- Each test references its design document property
- Tag format: `# Feature: autonomous-sme-control-tower, Property {number}: {property_text}`

### Unit Testing

**Framework**: `pytest`

**Focus Areas**:
- Specific examples from requirements
- Edge cases (e.g., BSI = 50 when insufficient data)
- Integration points between components
- Error conditions

### Integration Testing

**Key Scenarios**:
1. Full closed-loop workflow
2. Multi-organization data isolation
3. Error recovery and graceful degradation

### Test Coverage Goals

- Unit test coverage: Minimum 80%
- Property test coverage: All correctness properties tested
- Integration test coverage: All major workflows

---

## Security & Multi-Tenancy

### Data Isolation

- All DynamoDB tables partitioned by `org_id`
- API requests validate `org_id` and enforce data isolation
- No cross-organization data access permitted
- Security events logged for access violations

### Authentication & Authorization

- Validate `org_id` from request context
- Reject unauthorized access attempts (HTTP 403)
- Do not reveal existence of other organizations' data

---

## Performance Requirements

- Invoice processing: < 5 seconds
- Email processing: < 3 seconds
- Dashboard data refresh: Every 30 seconds
- BSI calculation: On-demand or triggered by new signals

---

## Deployment

### Docker Development Environment

- `docker-compose.yml` starts backend, frontend, and dependencies
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Environment configuration via `.env` files

### AWS Resources

- DynamoDB tables with on-demand capacity
- S3 bucket with lifecycle policies
- Bedrock model access in `us-east-1` region
