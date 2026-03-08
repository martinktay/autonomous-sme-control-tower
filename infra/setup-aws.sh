#!/bin/bash

# Setup script for AWS resources
# Run this after configuring AWS credentials

echo "Setting up AWS resources for Autonomous SME Control Tower..."

# DynamoDB Tables
echo "Creating DynamoDB tables..."

aws dynamodb create-table \
  --table-name autonomous-sme-signals \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name autonomous-sme-nsi-scores \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name autonomous-sme-strategies \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name autonomous-sme-actions \
  --attribute-definitions \
    AttributeName=org_id,AttributeType=S \
    AttributeName=action_id,AttributeType=S \
  --key-schema \
    AttributeName=org_id,KeyType=HASH \
    AttributeName=action_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# S3 Bucket
echo "Creating S3 bucket..."

aws s3 mb s3://autonomous-sme-documents --region us-east-1

echo "AWS resources created successfully!"
echo "Update your .env file with the resource names if different."
