# Autonomous SME Control Tower

AI-powered autonomous operations platform for small and medium enterprises.

## Overview

The Autonomous SME Control Tower is a Nova-first multi-agent system that helps SMEs manage their business operations intelligently through a continuous operational cycle:

1. **Ingest** - Collect business data (invoices, emails, documents)
2. **Diagnose** - Analyze signals and calculate Nova Stability Index (NSI)
3. **Simulate** - Generate and evaluate potential strategies
4. **Execute** - Take autonomous actions via Nova Act
5. **Evaluate** - Measure outcomes and refine predictions

## Technology Stack

### Backend
- FastAPI + Python
- AWS Bedrock (Nova 2 Lite, Nova embeddings, Nova Act, Nova Sonic)
- DynamoDB for operational data
- S3 for document storage

### Frontend
- Next.js 14 + TypeScript
- Tailwind CSS
- Axios for API calls

### Infrastructure
- Docker + Docker Compose
- AWS us-east-1

## Project Structure

```
autonomous-sme-control-tower/
  backend/          # FastAPI application
    app/
      routers/      # API endpoints
      agents/       # AI agent modules
      services/     # AWS integrations
      models/       # Pydantic schemas
      utils/        # Helper functions
  frontend/         # Next.js dashboard
    app/            # Pages
    components/     # Reusable UI
  infra/            # Docker configs
  prompts/v1/       # Versioned prompts
  docs/             # Documentation
  .kiro/            # Kiro workspace
```

## Quick Start

1. Clone and configure:
```bash
git clone https://github.com/martinktay/autonomous-sme-control-tower.git
cd autonomous-sme-control-tower
cp .env.example .env
# Edit .env with your AWS credentials
```

2. Run with Docker:
```bash
cd infra
docker-compose up
```

3. Access:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Portal Demo: http://localhost:3000/portal

## Multi-Agent Architecture

### 7 Specialized Agents

1. **Signal Agent** - Invoice extraction, email classification
2. **Risk Agent** - NSI calculation and risk diagnosis
3. **Strategy Agent** - Strategy simulation and ranking
4. **Action Agent** - Autonomous execution via Nova Act
5. **Re-evaluation Agent** - Outcome assessment and accuracy tracking
6. **Memory Agent** - Embeddings-based semantic search
7. **Voice Agent** - Audio briefings via Nova Sonic

## Core Features

- Invoice upload and extraction
- Email classification
- Embeddings-based memory
- NSI calculation with sub-indices
- Strategy simulation
- Autonomous action execution
- Outcome re-evaluation
- Prediction accuracy tracking
- Voice briefings
- One-click closed-loop demo

## API Endpoints

- `POST /api/invoices/upload` - Upload invoice
- `POST /api/stability/calculate` - Calculate NSI
- `POST /api/strategy/simulate` - Generate strategies
- `POST /api/actions/execute` - Execute action
- `POST /api/orchestration/run-loop` - Run complete cycle
- `GET /api/voice/{org_id}/summary` - Get voice briefing

## Nova Model Usage

- **Nova 2 Lite**: Invoice extraction, email classification, risk diagnosis, strategy generation, re-evaluation
- **Nova Embeddings**: Semantic memory and similarity search
- **Nova Act**: Autonomous workflow execution
- **Nova Sonic**: Voice briefings and audio summaries

## Development

Built with Kiro IDE using workspace-specific steering and skills for consistent development patterns.

## Hackathon Focus

This project demonstrates:
- Multi-agent AI architecture
- Deep Nova integration across all models
- Closed-loop autonomy with measurable outcomes
- Real workflow automation
- Operational intelligence for SMEs
