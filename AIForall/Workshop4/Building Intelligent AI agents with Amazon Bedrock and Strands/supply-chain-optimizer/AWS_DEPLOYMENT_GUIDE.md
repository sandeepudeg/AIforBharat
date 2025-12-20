# AWS Deployment & Testing Guide

## Overview
This guide walks you through deploying and testing the Supply Chain Optimizer system on AWS using real services instead of local mocks.

## Prerequisites

### AWS Account Setup
1. **AWS Account**: Create an AWS account at https://aws.amazon.com
2. **AWS CLI**: Install AWS CLI v2
   ```bash
   # Windows
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
   
   # Or use pip
   pip install awscli
   ```
3. **AWS Credentials**: Configure AWS credentials
   ```bash
   aws configure
   # Enter: Access Key ID, Secret Access Key, Default region (us-east-1), Output format (json)
   ```

### Required AWS Services
- **DynamoDB** - NoSQL database for inventory, forecasts, anomalies
- **RDS (PostgreSQL)** - Relational database for reports and metadata
- **S3** - Object storage for reports and archives
- **Lambda** - Serverless compute for agents
- **EventBridge** - Event scheduling and routing
- **SNS** - Notifications and alerts
- **CloudWatch** - Monitoring and logging
- **IAM** - Access management

## Step 1: Create AWS Resources

### 1.1 Create DynamoDB Tables

```bash
# Create Forecasts table
aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create Inventory table
aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=inventory_id,AttributeType=S \
  --key-schema AttributeName=inventory_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create Anomalies table
aws dynamodb create-table \
  --table-name anomalies \
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S \
  --key-schema AttributeName=anomaly_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create Purchase Orders table
aws dynamodb create-table \
  --table-name purchase_orders \
  --attribute-definitions AttributeName=po_id,AttributeType=S \
  --key-schema AttributeName=po_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create Suppliers table
aws dynamodb create-table \
  --table-name suppliers \
  --attribute-definitions AttributeName=supplier_id,AttributeType=S \
  --key-schema AttributeName=supplier_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 1.2 Create RDS PostgreSQL Database

```bash
# Create RDS instance (takes 5-10 minutes)
aws rds create-db-instance \
  --db-instance-identifier supply-chain-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 20 \
  --publicly-accessible true \
  --region us-east-1

# Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier supply-chain-db \
  --region us-east-1

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier supply-chain-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --region us-east-1
```

### 1.3 Create S3 Bucket

```bash
# Create S3 bucket for reports
aws s3 mb s3://supply-chain-reports-$(date +%s) \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket supply-chain-reports-XXXXX \
  --versioning-configuration Status=Enabled
```

### 1.4 Create SNS Topic for Alerts

```bash
# Create SNS topic
aws sns create-topic \
  --name supply-chain-alerts \
  --region us-east-1

# Subscribe email to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

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

# RDS Configuration
RDS_HOST=supply-chain-db.XXXXX.us-east-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=supply_chain
RDS_USER=admin
RDS_PASSWORD=YourSecurePassword123!

# S3 Configuration
S3_BUCKET=supply-chain-reports-XXXXX
S3_REGION=us-east-1

# SNS Configuration
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Step 3: Update Application Configuration

### 3.1 Modify `src/config/environment.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# DynamoDB Configuration
DYNAMODB_TABLES = {
    'forecasts': os.getenv('DYNAMODB_FORECASTS_TABLE', 'forecasts'),
    'inventory': os.getenv('DYNAMODB_INVENTORY_TABLE', 'inventory'),
    'anomalies': os.getenv('DYNAMODB_ANOMALIES_TABLE', 'anomalies'),
    'purchase_orders': os.getenv('DYNAMODB_PURCHASE_ORDERS_TABLE', 'purchase_orders'),
    'suppliers': os.getenv('DYNAMODB_SUPPLIERS_TABLE', 'suppliers'),
}

# RDS Configuration
RDS_CONFIG = {
    'host': os.getenv('RDS_HOST'),
    'port': int(os.getenv('RDS_PORT', 5432)),
    'database': os.getenv('RDS_DATABASE', 'supply_chain'),
    'user': os.getenv('RDS_USER', 'admin'),
    'password': os.getenv('RDS_PASSWORD'),
}

# S3 Configuration
S3_CONFIG = {
    'bucket': os.getenv('S3_BUCKET'),
    'region': os.getenv('S3_REGION', 'us-east-1'),
}

# SNS Configuration
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
```

## Step 4: Initialize RDS Database

### 4.1 Create Database Schema

```bash
# Connect to RDS and run schema
psql -h supply-chain-db.XXXXX.us-east-1.rds.amazonaws.com \
     -U admin \
     -d supply_chain \
     -f src/database/schema.sql
```

### 4.2 Verify Tables Created

```bash
psql -h supply-chain-db.XXXXX.us-east-1.rds.amazonaws.com \
     -U admin \
     -d supply_chain \
     -c "\dt"
```

## Step 5: Deploy Lambda Functions

### 5.1 Create Lambda Execution Role

```bash
# Create IAM role for Lambda
aws iam create-role \
  --role-name supply-chain-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name supply-chain-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name supply-chain-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name supply-chain-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

aws iam attach-role-policy \
  --role-name supply-chain-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

### 5.2 Package and Deploy Lambda Functions

```bash
# Install dependencies
pip install -r requirements.txt -t package/

# Copy source code
cp -r src/ package/

# Create deployment package
cd package
zip -r ../lambda-deployment.zip .
cd ..

# Deploy Lambda function
aws lambda create-function \
  --function-name supply-chain-optimizer \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/supply-chain-lambda-role \
  --handler src.orchestration.lambda_handlers.main \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1,RDS_HOST=supply-chain-db.XXXXX.us-east-1.rds.amazonaws.com}"
```

## Step 6: Set Up EventBridge Scheduling

### 6.1 Create EventBridge Rule

```bash
# Create rule for daily execution at 6:00 AM UTC
aws events put-rule \
  --name supply-chain-daily-optimization \
  --schedule-expression "cron(0 6 * * ? *)" \
  --state ENABLED

# Add Lambda as target
aws events put-targets \
  --rule supply-chain-daily-optimization \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:supply-chain-optimizer","RoleArn"="arn:aws:iam::ACCOUNT_ID:role/service-role/EventBridgeRole"
```

## Step 7: Test with AWS Services

### 7.1 Test DynamoDB Connection

```python
# test_aws_dynamodb.py
import boto3
from src.aws.clients import get_dynamodb_resource

def test_dynamodb():
    dynamodb = get_dynamodb_resource()
    
    # Test write
    table = dynamodb.Table('forecasts')
    table.put_item(Item={
        'forecast_id': 'TEST-001',
        'sku': 'PROD-001',
        'forecasted_demand': 1000,
        'confidence_95': 100,
    })
    
    # Test read
    response = table.get_item(Key={'forecast_id': 'TEST-001'})
    print("DynamoDB Test:", response['Item'])

if __name__ == '__main__':
    test_dynamodb()
```

Run test:
```bash
python test_aws_dynamodb.py
```

### 7.2 Test RDS Connection

```python
# test_aws_rds.py
from src.database.connection import get_rds_session

def test_rds():
    session = get_rds_session()
    
    # Test query
    result = session.execute("SELECT version();")
    print("RDS Test:", result.fetchone())
    
    session.close()

if __name__ == '__main__':
    test_rds()
```

Run test:
```bash
python test_aws_rds.py
```

### 7.3 Test S3 Connection

```python
# test_aws_s3.py
from src.aws.clients import get_s3_client
import json

def test_s3():
    s3 = get_s3_client()
    
    # Test write
    test_data = {'test': 'data', 'timestamp': '2025-12-20'}
    s3.put_object(
        Bucket='supply-chain-reports-XXXXX',
        Key='test/test-file.json',
        Body=json.dumps(test_data),
        ContentType='application/json'
    )
    
    # Test read
    response = s3.get_object(
        Bucket='supply-chain-reports-XXXXX',
        Key='test/test-file.json'
    )
    print("S3 Test:", response['Body'].read().decode())

if __name__ == '__main__':
    test_s3()
```

Run test:
```bash
python test_aws_s3.py
```

### 7.4 Test SNS Notifications

```python
# test_aws_sns.py
from src.aws.clients import get_sns_client
import os

def test_sns():
    sns = get_sns_client()
    
    # Publish test message
    response = sns.publish(
        TopicArn=os.getenv('SNS_TOPIC_ARN'),
        Subject='Supply Chain Optimizer - Test Alert',
        Message='This is a test alert from the Supply Chain Optimizer system.'
    )
    
    print("SNS Test - Message ID:", response['MessageId'])

if __name__ == '__main__':
    test_sns()
```

Run test:
```bash
python test_aws_sns.py
```

## Step 8: Run Full Integration Tests

### 8.1 Create Integration Test Suite

```python
# test_aws_integration.py
import pytest
from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent

@pytest.fixture
def agents():
    return {
        'forecasting': DemandForecastingAgent(),
        'inventory': InventoryOptimizerAgent(),
        'anomaly': AnomalyDetectionAgent(),
        'reporting': ReportGenerationAgent(),
    }

def test_end_to_end_workflow(agents):
    """Test complete workflow with AWS services"""
    
    # Step 1: Forecast demand
    sales_data = [
        {"date": "2025-12-01", "quantity": 100},
        {"date": "2025-12-02", "quantity": 105},
        {"date": "2025-12-03", "quantity": 98},
    ]
    
    analysis = agents['forecasting'].analyze_sales_history(
        sku="PROD-001",
        sales_data=sales_data
    )
    
    forecast = agents['forecasting'].generate_forecast(
        sku="PROD-001",
        sales_analysis=analysis,
        forecast_days=30
    )
    
    assert forecast['forecasted_demand'] > 0
    print("✓ Demand Forecasting: PASSED")
    
    # Step 2: Optimize inventory
    eoq = agents['inventory'].calculate_eoq(
        annual_demand=36000,
        ordering_cost=50,
        holding_cost_per_unit=2
    )
    
    assert eoq > 0
    print("✓ Inventory Optimization: PASSED")
    
    # Step 3: Detect anomalies
    anomaly = agents['anomaly'].detect_inventory_anomaly(
        sku="PROD-001",
        current_inventory=750,
        forecasted_inventory=1000,
        confidence_80=100,
        confidence_95=150
    )
    
    assert anomaly is not None
    print("✓ Anomaly Detection: PASSED")
    
    # Step 4: Generate report
    from datetime import date
    kpis = agents['reporting'].calculate_kpis(
        inventory_data=[{"quantity": 1000, "value": 50000}],
        forecast_data=[{"forecasted": 100, "actual": 95}],
        supplier_data=[{"reliability_score": 95}],
        period_start=date.today(),
        period_end=date.today()
    )
    
    assert 'inventory_turnover' in kpis
    print("✓ Report Generation: PASSED")
    
    print("\n✓ All integration tests PASSED!")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

Run integration tests:
```bash
pytest test_aws_integration.py -v
```

## Step 9: Monitor with CloudWatch

### 9.1 View Lambda Logs

```bash
# Get recent logs
aws logs tail /aws/lambda/supply-chain-optimizer --follow

# Get specific log stream
aws logs get-log-events \
  --log-group-name /aws/lambda/supply-chain-optimizer \
  --log-stream-name 'STREAM_NAME'
```

### 9.2 Create CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name supply-chain-optimizer \
  --dashboard-body file://dashboard-config.json
```

## Step 10: Cost Optimization

### 10.1 Estimated Monthly Costs

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 1M requests/month | ~$0.25 |
| RDS (t3.micro) | 730 hours/month | ~$10 |
| S3 | 100GB storage | ~$2.30 |
| Lambda | 1M invocations | ~$0.20 |
| SNS | 1000 notifications | ~$0.50 |
| CloudWatch | Logs & metrics | ~$5 |
| **Total** | | **~$18/month** |

### 10.2 Cost Reduction Tips

1. Use DynamoDB on-demand pricing for variable workloads
2. Use RDS Reserved Instances for predictable usage
3. Enable S3 Intelligent-Tiering for automatic cost optimization
4. Set Lambda memory to minimum required (512MB is good)
5. Use CloudWatch Logs retention policies (30 days)

## Troubleshooting

### Issue: Lambda timeout
**Solution**: Increase timeout in Lambda configuration
```bash
aws lambda update-function-configuration \
  --function-name supply-chain-optimizer \
  --timeout 300
```

### Issue: RDS connection refused
**Solution**: Check security group allows inbound on port 5432
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXX \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0
```

### Issue: DynamoDB throttling
**Solution**: Increase provisioned capacity or use on-demand
```bash
aws dynamodb update-table \
  --table-name forecasts \
  --billing-mode PAY_PER_REQUEST
```

## Next Steps

1. **Deploy to Production**: Use AWS CloudFormation or Terraform for IaC
2. **Set Up CI/CD**: Use AWS CodePipeline for automated deployments
3. **Enable Encryption**: Use AWS KMS for data encryption
4. **Implement Backup**: Set up automated RDS backups
5. **Scale Horizontally**: Use Lambda concurrency limits and DynamoDB auto-scaling

## References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [RDS User Guide](https://docs.aws.amazon.com/rds/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
- [EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)
