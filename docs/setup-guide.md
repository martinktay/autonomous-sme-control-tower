# Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- AWS account with Bedrock access
- AWS CLI configured (for resource setup)
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Step 1: Clone Repository

```bash
git clone https://github.com/martinktay/autonomous-sme-control-tower.git
cd autonomous-sme-control-tower
```

## Step 2: Configure AWS Credentials

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your AWS credentials:
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
```

## Step 3: Create AWS Resources

Run the setup script to create DynamoDB tables and S3 bucket:

```bash
cd infra
chmod +x setup-aws.sh
./setup-aws.sh
```

Or create manually via AWS Console:
- DynamoDB tables: autonomous-sme-signals, autonomous-sme-bsi-scores, autonomous-sme-strategies, autonomous-sme-actions
- S3 bucket: autonomous-sme-documents

## Step 4: Enable Bedrock Models

In AWS Console:
1. Go to Amazon Bedrock
2. Navigate to Model access
3. Request access to:
   - Nova 2 Lite
   - Nova Multimodal Embeddings
   - Nova Act
   - Nova 2 Sonic

## Step 5: Run with Docker

```bash
cd infra
docker-compose up
```

Services will be available at:
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Step 6: Test the System

1. Open http://localhost:3000/portal
2. Enter org_id: `demo-org`
3. Click "Run Closed Loop"
4. Watch the autonomous cycle execute

## Local Development (Without Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Bedrock Access Denied
- Verify model access is enabled in AWS Console
- Check IAM permissions for Bedrock API calls

### DynamoDB Errors
- Verify tables exist in us-east-1
- Check table names match .env configuration

### CORS Issues
- Backend allows all origins in development
- Update CORS settings for production

## Next Steps

- Upload test invoices via `/upload`
- View dashboard at `/dashboard`
- Run closed loop at `/portal`
- Check action history at `/actions`
