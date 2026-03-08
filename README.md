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
- Next.js 14
- TypeScript
- Tailwind CSS

### Infrastructure
- Docker + Docker Compose
- AWS us-east-1

## Project Structure

```
autonomous-sme-control-tower/
  backend/          # FastAPI application
  frontend/         # Next.js dashboard
  infra/            # Docker configs
  prompts/v1/       # Versioned prompt templates
  docs/             # Documentation
  .kiro/            # Kiro workspace config
```

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure AWS credentials
3. Run with Docker Compose:

```bash
cd infra
docker-compose up
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Core Features

- Invoice upload and extraction
- Email classification
- Embeddings-based memory
- NSI calculation and tracking
- Strategy simulation
- Autonomous action execution
- Outcome re-evaluation
- Voice briefings

## MVP Scope

The current MVP demonstrates:
- Working closed-loop system
- Multi-agent architecture
- Nova model integration
- NSI measurement
- Strategy automation
- Prediction accuracy tracking

## Development

This project uses Kiro IDE with workspace-specific steering and skills for consistent development.
