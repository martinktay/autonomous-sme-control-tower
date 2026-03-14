#!/bin/bash

# AWS Setup Script for Autonomous SME Control Tower
# This script creates the required DynamoDB tables and S3 bucket

set -e

echo "Setting up AWS resources for Autonomous SME Control Tower..."
echo "Region: us-east-1"
echo ""

# Create DynamoDB Tables

echo "Creating DynamoDB table: autonomous-sme-signals..."
aws dynamodb create-table \
  --table-name autonomous-sme-signals \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=signal_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=signal_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-nsi-scores..."
aws dynamodb create-table \
  --table-name autonomous-sme-nsi-scores \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=nsi_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=nsi_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-strategies..."
aws dynamodb create-table \
  --table-name autonomous-sme-strategies \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=strategy_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=strategy_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-actions..."
aws dynamodb create-table \
  --table-name autonomous-sme-actions \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=execution_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=execution_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-evaluations..."
aws dynamodb create-table \
  --table-name autonomous-sme-evaluations \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=evaluation_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=evaluation_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-embeddings..."
aws dynamodb create-table \
  --table-name autonomous-sme-embeddings \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=embedding_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=embedding_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "Creating DynamoDB table: autonomous-sme-tasks..."
aws dynamodb create-table \
  --table-name autonomous-sme-tasks \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=task_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=task_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo ""
echo "Creating S3 bucket: autonomous-sme-documents..."

aws s3 mb s3://autonomous-sme-documents --region us-east-1

echo ""
echo "Configuring S3 bucket lifecycle policy..."

cat > /tmp/lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "DeleteOldLogs",
      "Status": "Enabled",
      "Prefix": "logs/",
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket autonomous-sme-documents \
  --lifecycle-configuration file:///tmp/lifecycle-policy.json

rm /tmp/lifecycle-policy.json

echo ""
echo "✅ AWS resources created successfully!"
echo ""
echo "DynamoDB Tables:"
echo "  - autonomous-sme-signals"
echo "  - autonomous-sme-nsi-scores"
echo "  - autonomous-sme-strategies"
echo "  - autonomous-sme-actions"
echo "  - autonomous-sme-evaluations"
echo "  - autonomous-sme-embeddings"
echo "  - autonomous-sme-tasks"
echo ""
echo "S3 Buckets:"
echo "  - autonomous-sme-documents"
echo ""

# ==================== SES Email Setup ====================

echo "Setting up SES email..."

# Check if a sender email was provided
SES_SENDER_EMAIL="${SES_SENDER_EMAIL:-}"
if [ -n "$SES_SENDER_EMAIL" ]; then
  echo "Verifying sender email: $SES_SENDER_EMAIL"
  aws ses verify-email-identity \
    --email-address "$SES_SENDER_EMAIL" \
    --region us-east-1
  echo "  ✉ Verification email sent to $SES_SENDER_EMAIL"
  echo "  → Check your inbox and click the verification link"
else
  echo "  ⚠ No SES_SENDER_EMAIL set. Skipping email verification."
  echo "  → Set SES_SENDER_EMAIL in .env and re-run, or verify manually in AWS Console."
fi

echo ""
echo "SES Notes:"
echo "  - New AWS accounts start in SES sandbox mode"
echo "  - In sandbox, you can only send to verified email addresses"
echo "  - To send to anyone, request production access in AWS Console → SES → Account dashboard"
echo ""

echo "Next steps:"
echo "1. Enable Bedrock model access in AWS Console:"
echo "   - Nova 2 Lite (amazon.nova-lite-v1:0)"
echo "   - Nova embeddings (amazon.nova-embed-v1:0)"
echo "   - Nova Act (amazon.nova-act-v1:0)"
echo "   - Nova Sonic (amazon.nova-sonic-v1:0)"
echo ""
echo "2. Update .env file with your AWS credentials and SES_SENDER_EMAIL"
echo "3. Verify your sender email (check inbox for AWS verification link)"
echo "4. Run: docker-compose up"
echo ""
