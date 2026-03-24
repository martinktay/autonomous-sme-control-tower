# Architecture Overview

## System Design

The Autonomous SME Control Tower follows a multi-agent architecture with clear separation of concerns.

## Agent Modules

### 1. Signal Intake Agent (`signal_agent.py`)
- **Purpose**: Ingest and classify business signals
- **Inputs**: Invoices (PDF/image), emails, documents
- **Outputs**: Structured signal data
- **Models**: Nova 2 Lite for extraction, Nova embeddings for classification

### 2. Email Agent (`email_agent.py`)
- **Purpose**: Classify emails and extract actionable tasks
- **Inputs**: Email subject, body, sender
- **Outputs**: Classification, priority, extracted tasks
- **Models**: Nova 2 Lite

### 3. Finance Agent (`finance_agent.py`)
- **Purpose**: Process finance documents with intelligent classification and extraction
- **Inputs**: Invoices, receipts, statements, informal documents
- **Outputs**: Classified document type, extracted structured data, insights
- **Models**: Nova 2 Lite

### 4. Insights Agent (`insights_agent.py`)
- **Purpose**: Generate business intelligence from operational data
- **Inputs**: Aggregated signals, trends, operational metrics
- **Outputs**: Insight summaries, recommendations
- **Models**: Nova 2 Lite

### 5. Memory Agent (`memory_agent.py`)
- **Purpose**: Manage operational memory via embeddings
- **Inputs**: Signal data, documents
- **Outputs**: Embeddings, semantic search results
- **Models**: Nova Multimodal Embeddings

### 6. Risk Diagnosis Agent (`risk_agent.py`)
- **Purpose**: Analyze signals and calculate BSI
- **Inputs**: Structured signals, historical data
- **Outputs**: Risk assessment, BSI score, sub-indices
- **Models**: Nova 2 Lite for analysis

### 7. Strategy Simulation Agent (`strategy_agent.py`)
- **Purpose**: Generate and evaluate potential actions
- **Inputs**: Risk assessment, business context
- **Outputs**: Ranked strategy options with predicted outcomes
- **Models**: Nova 2 Lite for strategy generation

### 8. Action Execution Agent (`action_agent.py`)
- **Purpose**: Execute approved strategies autonomously
- **Inputs**: Selected strategy, execution parameters
- **Outputs**: Action results, execution logs
- **Models**: Nova Act for agentic actions

### 9. Re-evaluation Agent (`reeval_agent.py`)
- **Purpose**: Measure outcomes and refine approach
- **Inputs**: Action results, original predictions
- **Outputs**: Accuracy metrics, updated BSI weights
- **Models**: Nova 2 Lite for analysis

### 10. Voice Brief Agent (`voice_agent.py`)
- **Purpose**: Provide audio summaries and answer queries
- **Inputs**: Dashboard data, recent actions, user queries
- **Outputs**: Audio briefing, query responses
- **Models**: Nova Sonic

## Services Layer

- `ddb_service.py` – DynamoDB CRUD for all tables
- `finance_service.py` – Finance document processing pipeline
- `email_task_service.py` – Email-to-task conversion
- `memory_service.py` – Embedding storage and semantic search
- `s3_service.py` – Document storage in S3
- `ses_service.py` – Email sending via SES

## Middleware

- `org_isolation.py` – Enforces org_id tenant isolation on all requests
- `rate_limiter.py` – Per-org request rate limiting

## Utility Modules

- `bedrock_client.py` – Centralized Bedrock model invocation
- `json_guard.py` – Safe JSON parsing from model output
- `prompt_loader.py` – Template loading from prompts/v1/
- `upload_validator.py` – File upload validation

## Data Flow

```
Upload → Extract → Store (S3) → Classify → Score (BSI) → 
Simulate → Execute → Log → Re-evaluate → Update BSI
```

## Storage Architecture

- **DynamoDB Tables**:
  - signals (org_id, timestamp)
  - bsi_scores (org_id, timestamp)
  - strategies (org_id, strategy_id)
  - actions (org_id, action_id)
  - evaluations (org_id, eval_id)
  
- **S3 Buckets**:
  - invoices/
  - documents/
  - logs/

## API Design

RESTful endpoints organized by domain:
- `/api/invoices` – Invoice upload and extraction
- `/api/signals` – Signal management
- `/api/memory` – Embeddings and retrieval
- `/api/stability` – BSI calculations
- `/api/strategy` – Strategy simulation
- `/api/actions` – Action execution
- `/api/voice` – Voice briefings
- `/api/emails` – Email classification and tasks
- `/api/finance` – Finance document intelligence
- `/api/insights` – Business insights
- `/api/orchestration` – Full-loop orchestration
