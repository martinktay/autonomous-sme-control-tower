# Autonomous SME Control Tower - Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Docker** and **Docker Compose** installed
4. **Node.js 18+** and **Python 3.10+** (for local development)

## Step 1: AWS Account Setup

### 1.1 Create IAM User

1. Log into AWS Console
2. Navigate to IAM → Users → Create User
3. User name: `autonomous-sme-admin`
4. Enable "Provide user access to the AWS Management Console" (optional)
5. Click "Next"

### 1.2 Attach Policies

Attach the following AWS managed policies:
- `AmazonDynamoDBFullAccess`
- `AmazonS3FullAccess`
- `AmazonBedrockFullAccess`

Or create a custom policy with minimum required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/autonomous-sme-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::autonomous-sme-documents",
        "arn:aws:s3:::autonomous-sme-documents/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

### 1.3 Create Access Keys

1. Select the user → Security credentials tab
2. Click "Create access key"
3. Choose "Application running outside AWS"
4. Save the Access Key ID and Secret Access Key

## Step 2: Enable Bedrock Models

### 2.1 Request Model Access

1. Navigate to AWS Bedrock Console
2. Go to "Model access" in the left sidebar
3. Click "Manage model access"
4. Enable the following models:
   - ✅ Amazon Nova Lite
   - ✅ Amazon Nova Embeddings
   - ✅ Amazon Nova Act (if available)
   - ✅ Amazon Nova Sonic (if available)
5. Click "Save changes"

**Note**: Model access approval may take a few minutes to hours depending on your AWS account status.

## Step 3: Configure AWS CLI

```bash
# Configure AWS CLI with your credentials
aws configure

# Enter when prompted:
AWS Access Key ID: <your-access-key-id>
AWS Secret Access Key: <your-secret-access-key>
Default region name: us-east-1
Default output format: json
```

Verify configuration:
```bash
aws sts get-caller-identity
```

## Step 4: Create AWS Resources

### 4.1 Run Setup Script

```bash
# Navigate to infra directory
cd infra

# Make script executable (Mac/Linux)
chmod +x setup-aws.sh

# Run setup script
bash setup-aws.sh
```

For Windows PowerShell, use the PowerShell version:
```powershell
cd infra
.\setup-aws.ps1
```

### 4.2 Verify Resources

Check DynamoDB tables:
```bash
aws dynamodb list-tables --region us-east-1
```

Check S3 bucket:
```bash
aws s3 ls
```

## Step 5: Configure Environment Variables

### 5.1 Update `.env` File

Edit the `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>

# Bedrock Models (keep defaults)
NOVA_LITE_MODEL_ID=amazon.nova-lite-v1:0
NOVA_EMBEDDINGS_MODEL_ID=amazon.nova-embed-v1:0
NOVA_ACT_MODEL_ID=amazon.nova-act-v1:0
NOVA_SONIC_MODEL_ID=amazon.nova-sonic-v1:0

# DynamoDB Tables (keep defaults)
SIGNALS_TABLE=autonomous-sme-signals
BSI_SCORES_TABLE=autonomous-sme-bsi-scores
STRATEGIES_TABLE=autonomous-sme-strategies
ACTIONS_TABLE=autonomous-sme-actions
EMBEDDINGS_TABLE=autonomous-sme-embeddings
EVALUATIONS_TABLE=autonomous-sme-evaluations

# S3 Buckets (keep defaults)
DOCUMENTS_BUCKET=autonomous-sme-documents

# Application
APP_NAME=Autonomous SME Control Tower
DEBUG=true
```

### 5.2 Update Frontend Environment

The `frontend/.env.local` file should already be configured:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 6: Deploy with Docker

### 6.1 Build and Start Services

```bash
# Navigate to infra directory
cd infra

# Build and start all services
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d --build
```

### 6.2 Verify Services

Check running containers:
```bash
docker-compose ps
```

View logs:
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

## Step 7: Access the Application

Once services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Step 8: Test the Application

### 8.1 Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 8.2 Test Frontend

1. Open browser to http://localhost:3000
2. Navigate through pages:
   - Dashboard
   - Upload (for invoices/emails)
   - Memory (semantic search)
   - Strategy (simulations)
   - Actions (execution history)
   - Portal (one-click demo)
   - Voice (voice queries)

### 8.3 Test Backend API

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

## Troubleshooting

### Issue: AWS Credentials Not Working

**Solution**:
```bash
# Verify credentials
aws sts get-caller-identity

# Check .env file has correct values
cat .env | grep AWS
```

### Issue: Bedrock Model Access Denied

**Error**: `AccessDeniedException: Could not access model`

**Solution**:
1. Go to AWS Bedrock Console
2. Check "Model access" - ensure models are enabled
3. Wait for approval (may take time for new accounts)
4. Verify IAM user has `bedrock:InvokeModel` permission

### Issue: DynamoDB Table Not Found

**Error**: `ResourceNotFoundException: Requested resource not found`

**Solution**:
```bash
# Re-run setup script
cd infra
bash setup-aws.sh

# Or create tables manually via AWS Console
```

### Issue: Docker Build Fails

**Solution**:
```bash
# Clean Docker cache
docker-compose down
docker system prune -a

# Rebuild
docker-compose up --build
```

### Issue: Frontend Can't Connect to Backend

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `frontend/.env.local` has correct API URL
3. Check Docker network: `docker network ls`
4. Restart services: `docker-compose restart`

### Issue: Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

## Alternative: Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Production Deployment

For production deployment to AWS:

### Option 1: AWS ECS (Elastic Container Service)

1. Push Docker images to ECR
2. Create ECS cluster
3. Define task definitions
4. Create services
5. Configure load balancer

### Option 2: AWS App Runner

1. Connect to GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy automatically

### Option 3: AWS Elastic Beanstalk

1. Create application
2. Upload Docker Compose file
3. Configure environment
4. Deploy

## Security Best Practices

1. **Never commit `.env` file** - it's in `.gitignore`
2. **Use AWS Secrets Manager** for production credentials
3. **Enable MFA** on AWS account
4. **Rotate access keys** regularly
5. **Use IAM roles** instead of access keys when possible
6. **Enable CloudTrail** for audit logging
7. **Set up CloudWatch** for monitoring

## Cost Optimization

- **DynamoDB**: Uses on-demand billing (pay per request)
- **S3**: Lifecycle policy deletes old logs after 30 days
- **Bedrock**: Pay per token/request
- **Estimated monthly cost**: $10-50 for development/testing

## Next Steps

1. ✅ Deploy application
2. ✅ Test all features
3. 📝 Create sample data for demo
4. 🎯 Prepare hackathon submission
5. 🚀 Scale for production use

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review AWS CloudWatch logs
- Verify AWS resource status in Console
- Test API endpoints via Swagger UI

## Summary

You now have a fully deployed Autonomous SME Control Tower with:
- ✅ AWS Bedrock Nova models integration
- ✅ DynamoDB for data storage
- ✅ S3 for document storage
- ✅ FastAPI backend
- ✅ Next.js frontend
- ✅ Docker containerization
- ✅ Multi-tenant architecture

The system is ready for testing and demonstration!
