# Development Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- AWS Account with Bedrock access

## Local Development Setup

### 1. Clone and Configure

```bash
git clone https://github.com/martinktay/autonomous-sme-control-tower.git
cd autonomous-sme-control-tower
cp .env.example .env
# Edit .env with your AWS credentials
```

### 2. Python Virtual Environment (for local testing)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 3. Docker Development (recommended)

```bash
cd infra
docker-compose up
```

This starts:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### 4. Frontend Development (optional standalone)

```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_org_isolation.py -v
```

## Project Structure

```
autonomous-sme-control-tower/
  venv/             # Python virtual environment (local only)
  backend/          # FastAPI application
  frontend/         # Next.js application
  infra/            # Docker configs
  prompts/v1/       # Prompt templates
  docs/             # Documentation
```

## Environment Variables

Required in `.env`:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (default: us-east-1)
- `SIGNALS_TABLE`
- `NSI_SCORES_TABLE`
- `STRATEGIES_TABLE`
- `ACTIONS_TABLE`
- `S3_BUCKET`

## Troubleshooting

### ModuleNotFoundError
Ensure virtual environment is activated and dependencies are installed:
```bash
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Docker Issues
```bash
docker-compose down
docker-compose up --build
```

### AWS Credentials
Verify credentials are set in `.env` or AWS CLI is configured.
