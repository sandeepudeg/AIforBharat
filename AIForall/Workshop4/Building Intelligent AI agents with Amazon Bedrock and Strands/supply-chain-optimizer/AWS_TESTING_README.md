# AWS Testing Guide for Supply Chain Optimizer

This guide provides everything you need to test the Supply Chain Optimizer system with real AWS services.

## Overview

The Supply Chain Optimizer has been fully implemented and tested locally with 669 passing tests. This guide helps you:

1. Set up AWS resources (DynamoDB, S3, SNS, RDS)
2. Configure the application for AWS
3. Run connection tests for each service
4. Execute integration tests with real AWS services
5. Deploy to production (optional)

## Quick Start (5 minutes)

### 1. Install AWS CLI

**Windows**:
```bash
# Using pip
pip install awscli

# Or download installer from https://aws.amazon.com/cli/
```

**macOS**:
```bash
brew install awscli
```

**Linux**:
```bash
pip install awscli
```

### 2. Configure AWS Credentials

```bash
aws configure

# Enter your credentials:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

### 3. Create AWS Resources

**Windows**:
```bash
setup_aws_resources.bat
```

**macOS/Linux**:
```bash
chmod +x setup_aws_resources.sh
./setup_aws_resources.sh
```

### 4. Configure Environment

Create `.env` file in project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Tables
DYNAMODB_FORECASTS_TABLE=forecasts
DYNAMODB_INVENTORY_TABLE=inventory
DYNAMODB_ANOMALIES_TABLE=anomalies
DYNAMODB_PURCHASE_ORDERS_TABLE=purchase_orders
DYNAMODB_SUPPLIERS_TABLE=suppliers

# S3 Configuration (from setup script output)
S3_BUCKET=supply-chain-reports-XXXXX
S3_REGION=us-east-1

# SNS Configuration (from setup script output)
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Run Tests

```bash
# Test DynamoDB
python test_aws_dynamodb.py

# Test S3
python test_aws_s3.py

# Test SNS
python test_aws_sns.py

# Run all integration tests
pytest test_aws_integration.py -v
```

## Detailed Setup Guide

### Prerequisites

- Python 3.9 or higher
- AWS Account with billing enabled
- AWS CLI installed and configured
- boto3 library: `pip install boto3`

### AWS Services Used

| Service | Purpose | Cost |
|---------|---------|------|
| DynamoDB | Real-time data storage (forecasts, inventory, anomalies) | ~$0.25/month |
| S3 | Report and archive storage | ~$2.30/month |
| SNS | Alert notifications | ~$0.50/month |
| RDS (optional) | Relational data storage | ~$10/month |
| Lambda (optional) | Serverless compute | ~$0.20/month |
| CloudWatch | Monitoring and logging | ~$5/month |
| **Total** | | **~$18/month** |

### Step-by-Step Setup

#### Step 1: AWS Account Setup

1. Create AWS account at https://aws.amazon.com
2. Create IAM user with programmatic access
3. Attach policies:
   - AmazonDynamoDBFullAccess
   - AmazonS3FullAccess
   - AmazonSNSFullAccess
   - CloudWatchLogsFullAccess
4. Download access key and secret key

#### Step 2: Install AWS CLI

```bash
# Verify installation
aws --version

# Should output: aws-cli/2.x.x Python/3.x.x ...
```

#### Step 3: Configure Credentials

```bash
aws configure

# Interactive setup:
# AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

Verify configuration:
```bash
aws sts get-caller-identity

# Should output your AWS account info
```

#### Step 4: Create AWS Resources

**Option A: Automated Setup (Recommended)**

```bash
# Windows
setup_aws_resources.bat

# macOS/Linux
./setup_aws_resources.sh
```

This creates:
- 5 DynamoDB tables
- 1 S3 bucket
- 1 SNS topic
- 1 IAM role for Lambda

**Option B: Manual Setup**

See AWS_DEPLOYMENT_GUIDE.md for detailed manual commands.

#### Step 5: Configure Application

Create `.env` file:

```bash
# Copy from setup script output
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# DynamoDB
DYNAMODB_FORECASTS_TABLE=forecasts
DYNAMODB_INVENTORY_TABLE=inventory
DYNAMODB_ANOMALIES_TABLE=anomalies
DYNAMODB_PURCHASE_ORDERS_TABLE=purchase_orders
DYNAMODB_SUPPLIERS_TABLE=suppliers

# S3 (from setup output)
S3_BUCKET=supply-chain-reports-1234567890
S3_REGION=us-east-1

# SNS (from setup output)
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:supply-chain-alerts

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Testing

### Individual Service Tests

#### Test DynamoDB

```bash
python test_aws_dynamodb.py
```

Tests:
- Connection to DynamoDB
- Write/read operations
- Scan operations
- All table accessibility

#### Test S3

```bash
python test_aws_s3.py
```

Tests:
- Connection to S3
- List buckets
- Write/read operations
- List objects
- Bucket versioning status

#### Test SNS

```bash
python test_aws_sns.py
```

Tests:
- Connection to SNS
- List topics
- Publish messages
- Topic attributes
- List subscriptions

#### Test RDS (Optional)

```bash
python test_aws_rds.py
```

Tests:
- Connection to RDS
- Query execution
- Table existence
- Write/read operations

### Integration Tests

Run complete workflow tests:

```bash
# Run all integration tests
pytest test_aws_integration.py -v

# Run specific test class
pytest test_aws_integration.py::TestDemandForecastingWithAWS -v

# Run with detailed output
pytest test_aws_integration.py -v -s

# Run specific test
pytest test_aws_integration.py::TestEndToEndWorkflow::test_complete_daily_optimization -v -s
```

Test classes:
- `TestDemandForecastingWithAWS` - Forecast generation
- `TestInventoryOptimizationWithAWS` - EOQ and reorder point calculation
- `TestSupplierCoordinationWithAWS` - Purchase order management
- `TestAnomalyDetectionWithAWS` - Anomaly detection
- `TestReportGenerationWithAWS` - Report and KPI generation
- `TestEndToEndWorkflow` - Complete daily optimization workflow

### Run Demo with AWS

```bash
python demo.py
```

This demonstrates all 5 agents working with AWS services.

## Troubleshooting

### Issue: "Unable to locate credentials"

**Cause**: AWS credentials not configured

**Solution**:
```bash
aws configure
# or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Issue: "ResourceNotFoundException" for DynamoDB

**Cause**: Tables not created

**Solution**:
```bash
# Run setup script again
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux

# Or create tables manually
aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### Issue: "AccessDenied" errors

**Cause**: IAM permissions insufficient

**Solution**:
1. Check IAM user has these policies:
   - AmazonDynamoDBFullAccess
   - AmazonS3FullAccess
   - AmazonSNSFullAccess
   - CloudWatchLogsFullAccess

2. Regenerate credentials if needed

### Issue: "Connection timeout" for RDS

**Cause**: Security group not allowing inbound traffic

**Solution**:
```bash
# Allow inbound on port 5432
aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXX \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

### Issue: S3 bucket already exists

**Cause**: Bucket name not unique

**Solution**:
```bash
# Use a different bucket name
aws s3 mb s3://supply-chain-reports-$(date +%s) --region us-east-1
```

### Issue: Tests pass locally but fail on AWS

**Cause**: Environment variables not set correctly

**Solution**:
1. Verify `.env` file exists in project root
2. Check all required variables are set
3. Verify AWS credentials have correct permissions
4. Check AWS resources exist in correct region

## Monitoring

### View CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/supply-chain-optimizer --follow

# View specific log stream
aws logs get-log-events \
  --log-group-name /aws/lambda/supply-chain-optimizer \
  --log-stream-name 'STREAM_NAME'
```

### Check AWS Resources

```bash
# List DynamoDB tables
aws dynamodb list-tables --region us-east-1

# List S3 buckets
aws s3 ls

# List SNS topics
aws sns list-topics --region us-east-1

# List RDS instances
aws rds describe-db-instances --region us-east-1
```

## Cost Management

### Estimated Monthly Costs

- DynamoDB: ~$0.25 (on-demand pricing)
- S3: ~$2.30 (100GB storage)
- SNS: ~$0.50 (1000 notifications)
- RDS: ~$10 (t3.micro, optional)
- Lambda: ~$0.20 (1M invocations, optional)
- CloudWatch: ~$5 (logs and metrics)
- **Total: ~$18/month**

### Cost Optimization Tips

1. Use DynamoDB on-demand pricing for variable workloads
2. Enable S3 Intelligent-Tiering for automatic cost optimization
3. Set CloudWatch Logs retention to 30 days
4. Use Lambda memory sizing appropriately (512MB is good)
5. Delete unused resources (old S3 objects, unused tables)

### Delete Resources (to stop costs)

```bash
# Delete DynamoDB tables
aws dynamodb delete-table --table-name forecasts --region us-east-1
aws dynamodb delete-table --table-name inventory --region us-east-1
aws dynamodb delete-table --table-name anomalies --region us-east-1
aws dynamodb delete-table --table-name purchase_orders --region us-east-1
aws dynamodb delete-table --table-name suppliers --region us-east-1

# Delete S3 bucket
aws s3 rb s3://supply-chain-reports-XXXXX --force

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts

# Delete IAM role
aws iam detach-role-policy --role-name supply-chain-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam delete-role --role-name supply-chain-lambda-role
```

## Next Steps

### For Testing
1. Run individual service tests
2. Run integration tests
3. Run demo with AWS services
4. Monitor CloudWatch logs

### For Production Deployment
1. Set up RDS database
2. Deploy Lambda functions
3. Configure EventBridge scheduling
4. Set up CloudWatch dashboards
5. Enable encryption and backups

See AWS_DEPLOYMENT_GUIDE.md for detailed production setup.

### For Development
1. Use local DynamoDB for faster iteration
2. Use S3 local stack for testing
3. Use SNS local stack for testing
4. Deploy to AWS only when ready

## Support

For issues or questions:

1. Check AWS_DEPLOYMENT_GUIDE.md for detailed setup
2. Review CloudWatch logs for error details
3. Verify AWS credentials and permissions
4. Check that all required resources exist
5. Ensure .env file is configured correctly

## Quick Reference Commands

```bash
# Setup
aws configure
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux

# Test individual services
python test_aws_dynamodb.py
python test_aws_s3.py
python test_aws_sns.py
python test_aws_rds.py

# Test integration
pytest test_aws_integration.py -v

# Run demo
python demo.py

# Monitor
aws logs tail /aws/lambda/supply-chain-optimizer --follow

# List resources
aws dynamodb list-tables --region us-east-1
aws s3 ls
aws sns list-topics --region us-east-1

# Cleanup
aws dynamodb delete-table --table-name forecasts --region us-east-1
aws s3 rb s3://supply-chain-reports-XXXXX --force
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
```

## Files Included

- `test_aws_dynamodb.py` - DynamoDB connection tests
- `test_aws_s3.py` - S3 connection tests
- `test_aws_sns.py` - SNS connection tests
- `test_aws_rds.py` - RDS connection tests
- `test_aws_integration.py` - Complete integration tests
- `setup_aws_resources.sh` - Automated setup (macOS/Linux)
- `setup_aws_resources.bat` - Automated setup (Windows)
- `AWS_TESTING_QUICK_START.md` - Quick start guide
- `AWS_DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- `AWS_TESTING_README.md` - This file

## Summary

You now have everything needed to:
✓ Set up AWS resources
✓ Configure the application
✓ Test each AWS service
✓ Run integration tests
✓ Deploy to production

Start with the Quick Start section above, then follow the detailed setup guide as needed.
