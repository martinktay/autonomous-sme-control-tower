# Infrastructure Setup Guide

## Overview

This document describes the infrastructure setup for the Autonomous SME Control Tower, including Docker development environment, backend FastAPI application, frontend Next.js application, and AWS service integrations.

## Architecture Components

### 1. Docker Development Environment

**Location**: `infra/docker-compose.yml`

The system uses Docker Compose to orchestrate multiple services:

- **Backend Service**: FastAPI application on port 8000
- **Frontend Service**: Next.js application on port 3000
- **Network**: Bridge network `autonomous-sme` for inter-service communication

**Key Features**:
- Hot-reload enabled for both backend and frontend
- Volume mounting for live code updates
- Environment variable injection from `.env` file
- Service dependency management (frontend depends on backend)

### 2. Backend FastAPI Application

**Location**: `backend/app/`

**Structure**:
```
backend/app/
├── main.py              # FastAPI app entry point with CORS
├── config.py            # Environment configuration with Pydantic
├── routers/             # API endpoint handlers
├── agents/              # Agent logic modules
├── services/            # AWS service integrations
├── models/              # Pydantic data models
└── utils/               # Helper functions
```

**Key Features**:
- CORS middleware configured for frontend communication
- Automatic API documentation at `/docs`
- Health check endpoint at `/health`
- Modular router architecture
- Pydantic-based configuration management

### 3. Frontend Next.js Application

**Location**: `frontend/`

**Structure**:
```
frontend/
├── app/                 # Next.js 14 app directory
├── components/          # React components
├── lib/                 # Utilities and API client
├── package.json         # Dependencies
└── Dockerfile           # Container configuration
```

**Key Features**:
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Axios-based API client with centralized configuration
- Radix UI components for accessible UI

### 4. AWS Service Integrations

#### Bedrock Client (`backend/app/utils/bedrock_client.py`)

**Features**:
- Circuit breaker pattern for fault tolerance
- Exponential backoff retry logic (max 3 retries)
- Support for all Nova models:
  - Nova 2 Lite (text generation)
  - Nova Embeddings (semantic search)
  - Nova Act (agentic actions)
  - Nova Sonic (voice generation)

**Error Handling**:
- Automatic retry on throttling and service errors
- No retry on validation/access errors
- Circuit breaker opens after 5 consecutive failures
- 60-second timeout before attempting recovery

#### DynamoDB Service (`backend/app/services/ddb_service.py`)

**Features**:
- Exponential backoff retry logic
- Multi-table management:
  - `autonomous-sme-signals` - Signal records
  - `autonomous-sme-nsi-scores` - NSI snapshots
  - `autonomous-sme-strategies` - Generated strategies
  - `autonomous-sme-actions` - Action execution logs
- Org-based data partitioning for multi-tenancy

**Error Handling**:
- Retry on throughput exceeded and throttling
- No retry on validation/resource not found errors
- Exponential backoff with jitter

#### S3 Service (`backend/app/services/s3_service.py`)

**Features**:
- Document upload/download with retry logic
- Presigned URL generation for secure access
- File deletion support

**Error Handling**:
- Retry on slow down and service unavailable
- No retry on bucket/access errors
- Exponential backoff with jitter

## Configuration

### Environment Variables

**File**: `.env` (create from `.env.example`)

**Required Variables**:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Models
NOVA_LITE_MODEL_ID=amazon.nova-lite-v1:0
NOVA_EMBEDDINGS_MODEL_ID=amazon.nova-embed-v1:0
NOVA_ACT_MODEL_ID=amazon.nova-act-v1:0
NOVA_SONIC_MODEL_ID=amazon.nova-sonic-v1:0

# DynamoDB Tables
SIGNALS_TABLE=autonomous-sme-signals
NSI_SCORES_TABLE=autonomous-sme-nsi-scores
STRATEGIES_TABLE=autonomous-sme-strategies
ACTIONS_TABLE=autonomous-sme-actions

# S3 Buckets
DOCUMENTS_BUCKET=autonomous-sme-documents

# Application
APP_NAME=Autonomous SME Control Tower
DEBUG=false
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- AWS credentials with Bedrock, DynamoDB, and S3 access
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd autonomous-sme-control-tower
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Start services with Docker Compose**
   ```bash
   cd infra
   docker-compose up --build
   ```

4. **Access the application**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend: http://localhost:3000

### Verification

1. **Check backend health**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API documentation**
   Open http://localhost:8000/docs in your browser

3. **Check frontend**
   Open http://localhost:3000 in your browser

## Error Handling Patterns

### Circuit Breaker Pattern

The Bedrock client implements a circuit breaker to prevent cascading failures:

- **Closed State**: Normal operation, requests pass through
- **Open State**: After 5 consecutive failures, circuit opens and rejects requests
- **Half-Open State**: After 60 seconds, allows one test request
- **Recovery**: If test request succeeds, circuit closes

### Retry Logic

All AWS service integrations use exponential backoff:

```
Attempt 1: Immediate
Attempt 2: Wait 2^1 + jitter seconds
Attempt 3: Wait 2^2 + jitter seconds
```

Jitter is added to prevent thundering herd problem.

### Error Categories

1. **Validation Errors**: No retry, immediate failure
2. **Throttling Errors**: Retry with backoff
3. **Service Errors**: Retry with backoff
4. **Access Errors**: No retry, immediate failure

## Multi-Organization Support

All data is partitioned by `org_id`:

- DynamoDB tables use `org_id` as partition key
- API requests validate `org_id` for data isolation
- Cross-organization access is prevented
- S3 objects are organized by `org_id` prefix

## Performance Considerations

- **Backend**: Uvicorn with auto-reload in development
- **Frontend**: Next.js dev server with fast refresh
- **Database**: DynamoDB on-demand capacity
- **Storage**: S3 with standard storage class
- **API**: CORS enabled for all origins in development

## Security Notes

- AWS credentials should never be committed to version control
- Use IAM roles in production instead of access keys
- CORS should be restricted to specific origins in production
- Enable HTTPS in production deployments
- Implement rate limiting for production APIs

## Troubleshooting

### Backend won't start
- Check AWS credentials in `.env`
- Verify Docker is running
- Check port 8000 is not in use

### Frontend won't start
- Check backend is running first
- Verify port 3000 is not in use
- Check `NEXT_PUBLIC_API_URL` environment variable

### AWS service errors
- Verify AWS credentials have correct permissions
- Check AWS region is set to `us-east-1`
- Ensure Bedrock models are enabled in your account
- Verify DynamoDB tables exist
- Verify S3 bucket exists

### Circuit breaker is open
- Wait 60 seconds for automatic recovery
- Check AWS service status
- Verify credentials and permissions
- Review application logs for error patterns

## Next Steps

After infrastructure setup is complete:

1. Set up AWS resources (DynamoDB tables, S3 bucket)
2. Implement agent logic modules
3. Create prompt templates in `/prompts/v1/`
4. Build frontend pages and components
5. Test end-to-end workflows
