# AWS Testing Quick Start Guide

This guide helps you quickly test the Supply Chain Optimizer with real AWS services.

## Prerequisites

1. **AWS Account** - Create at https://aws.amazon.com
2. **AWS CLI** - Install from https://aws.amazon.com/cli/
3. **Python 3.9+** - Already installed
4. **boto3** - Install with: `pip install boto3`

## Step 1: Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# Enter:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

## Step 2: Create AWS Resources

### Option A: Quick Setup (Recommended for Testing)

Run the setup script to create all resources:

```bash
# Create DynamoDB tables
aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=inventory_id,AttributeType=S \
  --key-schema AttributeName=inventory_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name anomalies \
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S \
  --key-schema AttributeName=anomaly_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name purchase_orders \
  --attribute-definitions AttributeName=po_id,AttributeType=S \
  --key-schema AttributeName=po_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

aws dynamodb create-table \
  --table-name suppliers \
  --attribute-definitions AttributeName=supplier_id,AttributeType=S \
  --key-schema AttributeName=supplier_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### Option B: Full Setup (Production)

Follow the complete AWS_DEPLOYMENT_GUIDE.md for RDS, S3, SNS, and Lambda setup.

## Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# DynamoDB Tables
DYNAMODB_FORECASTS_TABLE=forecasts
DYNAMODB_INVENTORY_TABLE=inventory
DYNAMODB_ANOMALIES_TABLE=anomalies
DYNAMODB_PURCHASE_ORDERS_TABLE=purchase_orders
DYNAMODB_SUPPLIERS_TABLE=suppliers

# Optional: RDS Configuration (if using RDS)
RDS_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=supply_chain
RDS_USER=admin
RDS_PASSWORD=your_password

# Optional: S3 Configuration (if using S3)
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1

# Optional: SNS Configuration (if using SNS)
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Step 4: Run AWS Connection Tests

Test each AWS service individually:

### Test DynamoDB Connection

```bash
python test_aws_dynamodb.py
```

Expected output:
```
============================================================
DynamoDB Connection Tests
============================================================

[1/4] Testing DynamoDB connection...
PASS: DynamoDB connection successful

[2/4] Testing DynamoDB write/read operations...
PASS: DynamoDB write/read successful

[3/4] Testing DynamoDB scan operation...
PASS: DynamoDB scan successful

[4/4] Testing all DynamoDB tables...
Table Status:
  forecasts: OK
  inventory: OK
  anomalies: OK
  purchase_orders: OK
  suppliers: OK

PASS: All DynamoDB tables accessible

============================================================
All DynamoDB tests PASSED!
============================================================
```

### Test RDS Connection (Optional)

```bash
python test_aws_rds.py
```

### Test S3 Connection (Optional)

```bash
python test_aws_s3.py
```

### Test SNS Connection (Optional)

```bash
python test_aws_sns.py
```

## Step 5: Run Integration Tests

Test the complete workflow with AWS services:

```bash
# Run all integration tests
pytest test_aws_integration.py -v -s

# Run specific test class
pytest test_aws_integration.py::TestDemandForecastingWithAWS -v -s

# Run with detailed output
pytest test_aws_integration.py -v -s --tb=short
```

Expected output:
```
test_aws_integration.py::TestDemandForecastingWithAWS::test_forecast_generation PASSED
test_aws_integration.py::TestInventoryOptimizationWithAWS::test_eoq_calculation PASSED
test_aws_integration.py::TestSupplierCoordinationWithAWS::test_purchase_order_placement PASSED
test_aws_integration.py::TestAnomalyDetectionWithAWS::test_inventory_anomaly_detection PASSED
test_aws_integration.py::TestReportGenerationWithAWS::test_kpi_calculation PASSED
test_aws_integration.py::TestEndToEndWorkflow::test_complete_daily_optimization PASSED

======================== 6 passed in 2.34s ========================
```

## Step 6: Verify AWS Resources

Check that resources were created successfully:

```bash
# List DynamoDB tables
aws dynamodb list-tables --region us-east-1

# List S3 buckets (if created)
aws s3 ls

# List SNS topics (if created)
aws sns list-topics --region us-east-1

# List RDS instances (if created)
aws rds describe-db-instances --region us-east-1
```

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution**: Configure AWS credentials
```bash
aws configure
# or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Issue: "ResourceNotFoundException" for DynamoDB tables

**Solution**: Create the tables first
```bash
# Run the table creation commands from Step 2
```

### Issue: "AccessDenied" errors

**Solution**: Check IAM permissions
```bash
# Ensure your AWS user has these permissions:
# - dynamodb:*
# - s3:*
# - rds:*
# - sns:*
# - lambda:*
# - events:*
```

### Issue: "Connection timeout" for RDS

**Solution**: Check security group
```bash
# Allow inbound traffic on port 5432 from your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXX \
  --protocol tcp \
  --port 5432 \
  --cidr YOUR_IP/32
```

## Next Steps

1. **Run the demo** with AWS services:
   ```bash
   python demo.py
   ```

2. **Start the API server**:
   ```bash
   python -m uvicorn src.api.app:app --reload
   ```

3. **Monitor with CloudWatch**:
   ```bash
   aws logs tail /aws/lambda/supply-chain-optimizer --follow
   ```

4. **Deploy to Lambda** (see AWS_DEPLOYMENT_GUIDE.md):
   ```bash
   # Package and deploy Lambda function
   ```

## Cost Estimation

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 1M requests/month | ~$0.25 |
| S3 | 100GB storage | ~$2.30 |
| SNS | 1000 notifications | ~$0.50 |
| RDS (optional) | t3.micro 730 hours | ~$10 |
| **Total** | | **~$13/month** |

## Support

For issues or questions:
1. Check the AWS_DEPLOYMENT_GUIDE.md for detailed setup
2. Review CloudWatch logs for error details
3. Verify AWS credentials and permissions
4. Check that all required tables/resources exist

## Quick Reference

```bash
# Test all AWS services
python test_aws_dynamodb.py && \
python test_aws_rds.py && \
python test_aws_s3.py && \
python test_aws_sns.py

# Run integration tests
pytest test_aws_integration.py -v

# Run demo with AWS
python demo.py

# Start API server
python -m uvicorn src.api.app:app --reload

# View AWS resources
aws dynamodb list-tables --region us-east-1
aws s3 ls
aws sns list-topics --region us-east-1
```
