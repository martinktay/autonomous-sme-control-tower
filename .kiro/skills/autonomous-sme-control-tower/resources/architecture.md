# Architecture Overview

## System Design

The Autonomous SME Control Tower follows a multi-agent architecture with clear separation of concerns.

## Agent Modules

### 1. Signal Intake Agent
- **Purpose**: Ingest and classify business signals
- **Inputs**: Invoices (PDF/image), emails, documents
- **Outputs**: Structured signal data
- **Models**: Nova 2 Lite for extraction, Nova embeddings for classification

### 2. Risk Diagnosis Agent
- **Purpose**: Analyze signals and calculate NSI
- **Inputs**: Structured signals, historical data
- **Outputs**: Risk assessment, NSI score, sub-indices
- **Models**: Nova 2 Lite for analysis

### 3. Strategy Simulation Agent
- **Purpose**: Generate and evaluate potential actions
- **Inputs**: Risk assessment, business context
- **Outputs**: Ranked strategy options with predicted outcomes
- **Models**: Nova 2 Lite for strategy generation

### 4. Action Execution Agent
- **Purpose**: Execute approved strategies autonomously
- **Inputs**: Selected strategy, execution parameters
- **Outputs**: Action results, execution logs
- **Models**: Nova Act for agentic actions

### 5. Re-evaluation Agent
- **Purpose**: Measure outcomes and refine approach
- **Inputs**: Action results, original predictions
- **Outputs**: Accuracy metrics, updated NSI weights
- **Models**: Nova 2 Lite for analysis

### 6. Voice Brief Agent (Optional)
- **Purpose**: Provide audio summaries
- **Inputs**: Dashboard data, recent actions
- **Outputs**: Audio briefing
- **Models**: Nova Sonic

## Data Flow

```
Upload → Extract → Store (S3) → Classify → Score (NSI) → 
Simulate → Execute → Log → Re-evaluate → Update NSI
```

## Storage Architecture

- **DynamoDB Tables**:
  - signals (org_id, timestamp)
  - nsi_scores (org_id, timestamp)
  - strategies (org_id, strategy_id)
  - actions (org_id, action_id)
  
- **S3 Buckets**:
  - invoices/
  - documents/
  - logs/

## API Design

RESTful endpoints organized by domain:
- `/api/invoices` - Invoice upload and extraction
- `/api/signals` - Signal management
- `/api/memory` - Embeddings and retrieval
- `/api/stability` - NSI calculations
- `/api/strategy` - Strategy simulation
- `/api/actions` - Action execution
- `/api/voice` - Voice briefings
