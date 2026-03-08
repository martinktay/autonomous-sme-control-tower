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
- Analyzes operational signals to calculate Nova Stability Index (NSI)
- Computes sub-indices: liquidity, revenue stability, operational latency, vendor risk
- Identifies top risks with explanations
- Stores NSI snapshots with timestamps

### Strategy Simulation Agent
- Generates 2-3 corrective strategies based on risk diagnosis
- Estimates predicted NSI improvement for each option
- Provides confidence scores and cost estimates
- Marks strategies as automatable or manual

### Action Execution Agent
- Executes automatable strategies via Nova Act
- Logs execution status and results
- Tracks predicted vs actual outcomes
- Handles errors gracefully

### Re-evaluation Agent
- Recalculates NSI after action execution
- Compares predicted vs actual improvement
- Computes prediction accuracy metrics
- Suggests NSI weight adjustments based on learnings

### Memory Agent
- Generates embeddings using Nova Multimodal Embeddings
- Enables semantic search across operational history
- Retrieves similar past situations for context

### Voice Agent
- Generates spoken briefings using Nova 2 Sonic
- Summarizes current stability, risks, and recent actions
- Provides audio responses to dashboard queries

## Data Flow

```
1. INGEST
   Upload → S3 Storage → Signal Extraction → DynamoDB

2. DIAGNOSE
   Signals → Risk Analysis → NSI Calculation → Store Score

3. SIMULATE
   NSI + Risks → Strategy Generation → Rank Options

4. EXECUTE
   Select Strategy → Nova Act Execution → Log Results

5. EVALUATE
   Recalculate NSI → Compare Predictions → Update Accuracy
```

## Storage Architecture

### DynamoDB Tables
- `autonomous-sme-signals`: Signal records keyed by org_id
- `autonomous-sme-nsi-scores`: NSI snapshots keyed by org_id + timestamp
- `autonomous-sme-strategies`: Strategy simulations
- `autonomous-sme-actions`: Action execution logs

### S3 Buckets
- `autonomous-sme-documents`: Invoice files, raw documents

## API Design

RESTful endpoints organized by domain:
- `/api/invoices` - Invoice upload and extraction
- `/api/signals` - Signal retrieval
- `/api/memory` - Embeddings search
- `/api/stability` - NSI calculation and history
- `/api/strategy` - Strategy simulation
- `/api/actions` - Action execution and history
- `/api/voice` - Voice briefings
- `/api/orchestration` - Full closed-loop execution

## Frontend Architecture

Next.js 14 app with pages:
- `/portal` - One-click closed-loop demo
- `/dashboard` - NSI, risks, actions overview
- `/upload` - Invoice upload interface
- `/strategy` - Strategy simulation view
- `/actions` - Action history
- `/memory` - Semantic search
- `/voice` - Voice briefings

Reusable components:
- `NsiCard` - Displays NSI with color coding
- `RiskPanel` - Lists top risks
- `ActionLog` - Shows recent actions

## Technology Stack

- Backend: FastAPI + Python + boto3
- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- AI: AWS Bedrock Nova models
- Storage: DynamoDB + S3
- Infrastructure: Docker + Docker Compose
