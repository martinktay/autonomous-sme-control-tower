---
inclusion: always
name: tech
description: Technology stack, AWS services, and development conventions.
---

# Technology Stack

## Backend

- **Framework**: FastAPI + Python
- **API Design**: RESTful endpoints with strict typing
- **Data Validation**: Pydantic models

## Frontend

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **UI Components**: Modern, responsive design

## AWS Services

- **Bedrock Models**:
  - Nova 2 Lite (text generation)
  - Nova embeddings (semantic search)
  - Nova Act (agentic actions)
  - Nova Sonic (voice/audio)
- **Storage**: 
  - DynamoDB (operational data, keyed by org_id)
  - S3 (document/invoice storage)

## Development Environment

- **Containerization**: Docker-first local development
- **Orchestration**: docker-compose for multi-service setup
- **Environment**: .env files for configuration

## Model Output Standards

- Enforce strict JSON output from all model prompts
- Validate responses against Pydantic schemas
- Handle parsing errors gracefully

## Prompt Management

- Store all prompt templates in `/prompts/v1/`
- Keep prompt logic separate from Python code
- Version prompts explicitly (v1, v2, etc.)
