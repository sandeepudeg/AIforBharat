#!/bin/bash

# AWS Resource Setup Script for Supply Chain Optimizer
# This script creates all necessary AWS resources for testing and deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGION=${AWS_REGION:-us-east-1}
ENVIRONMENT=${ENVIRONMENT:-development}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Resource Setup for Supply Chain Optimizer${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"
echo ""

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${YELLOW}Creating DynamoDB tables...${NC}"
echo ""

# Create Forecasts table
echo "Creating forecasts table..."
aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  (Table may already exist)"

# Create Inventory table
echo "Creating inventory table..."
aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=inventory_id,AttributeType=S \
  --key-schema AttributeName=inventory_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  (Table may already exist)"

# Create Anomalies table
echo "Creating anomalies table..."
aws dynamodb create-table \
  --table-name anomalies \
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S \
  --key-schema AttributeName=anomaly_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  (Table may already exist)"

# Create Purchase Orders table
echo "Creating purchase_orders table..."
aws dynamodb create-table \
  --table-name purchase_orders \
  --attribute-definitions AttributeName=po_id,AttributeType=S \
  --key-schema AttributeName=po_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  (Table may already exist)"

# Create Suppliers table
echo "Creating suppliers table..."
aws dynamodb create-table \
  --table-name suppliers \
  --attribute-definitions AttributeName=supplier_id,AttributeType=S \
  --key-schema AttributeName=supplier_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION 2>/dev/null || echo "  (Table may already exist)"

echo -e "${GREEN}✓ DynamoDB tables created${NC}"
echo ""

# Create S3 bucket
echo -e "${YELLOW}Creating S3 bucket...${NC}"
BUCKET_NAME="supply-chain-reports-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "  (Bucket may already exist)"

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled \
  --region $REGION 2>/dev/null || echo "  (Versioning may already be enabled)"

echo -e "${GREEN}✓ S3 bucket created: $BUCKET_NAME${NC}"
echo ""

# Create SNS topic
echo -e "${YELLOW}Creating SNS topic...${NC}"
TOPIC_RESPONSE=$(aws sns create-topic \
  --name supply-chain-alerts \
  --region $REGION)

TOPIC_ARN=$(echo $TOPIC_RESPONSE | grep -o 'arn:aws:sns:[^"]*')
echo -e "${GREEN}✓ SNS topic created: $TOPIC_ARN${NC}"
echo ""

# Create IAM role for Lambda
echo -e "${YELLOW}Creating IAM role for Lambda...${NC}"
ROLE_NAME="supply-chain-lambda-role"

# Check if role exists
if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "  (Role already exists)"
else
    aws iam create-role \
      --role-name $ROLE_NAME \
      --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
          "Effect": "Allow",
          "Principal": {"Service": "lambda.amazonaws.com"},
          "Action": "sts:AssumeRole"
        }]
      }' 2>/dev/null || echo "  (Role may already exist)"
    
    # Attach policies
    aws iam attach-role-policy \
      --role-name $ROLE_NAME \
      --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess 2>/dev/null || true
    
    aws iam attach-role-policy \
      --role-name $ROLE_NAME \
      --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>/dev/null || true
    
    aws iam attach-role-policy \
      --role-name $ROLE_NAME \
      --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess 2>/dev/null || true
    
    aws iam attach-role-policy \
      --role-name $ROLE_NAME \
      --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess 2>/dev/null || true
fi

echo -e "${GREEN}✓ IAM role created: $ROLE_NAME${NC}"
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Resources Created Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "DynamoDB Tables:"
echo "  - forecasts"
echo "  - inventory"
echo "  - anomalies"
echo "  - purchase_orders"
echo "  - suppliers"
echo ""
echo "S3 Bucket:"
echo "  - $BUCKET_NAME"
echo ""
echo "SNS Topic:"
echo "  - $TOPIC_ARN"
echo ""
echo "IAM Role:"
echo "  - $ROLE_NAME"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update .env file with:"
echo "   S3_BUCKET=$BUCKET_NAME"
echo "   SNS_TOPIC_ARN=$TOPIC_ARN"
echo ""
echo "2. Run tests:"
echo "   python test_aws_dynamodb.py"
echo "   python test_aws_s3.py"
echo "   python test_aws_sns.py"
echo ""
echo "3. Run integration tests:"
echo "   pytest test_aws_integration.py -v"
echo ""
