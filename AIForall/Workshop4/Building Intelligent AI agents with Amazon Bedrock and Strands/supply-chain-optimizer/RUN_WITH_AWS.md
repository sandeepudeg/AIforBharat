# Run Supply Chain Optimizer with AWS Services

This guide shows how to run the complete system using real AWS services.

## Prerequisites

1. **AWS Account** - Create at https://aws.amazon.com
2. **AWS CLI** - Install and configure: `aws configure`
3. **Python 3.9+** - Already installed
4. **Dependencies** - `pip install -r requirements.txt`

## Step 1: Create AWS Resources (5 minutes)

### Windows
```bash
setup_aws_resources.bat
```

### macOS/Linux
```bash
chmod +x setup_aws_resources.sh
./setup_aws_resources.sh
```

This creates:
- 5 DynamoDB tables (forecasts, inventory, anomalies, purchase_orders, suppliers)
- 1 S3 bucket (for reports)
- 1 SNS topic (for alerts)
- 1 IAM role (for Lambda)

## Step 2: Configure Environment (2 minutes)

Create `.env` file in project root with output from setup script:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Tables
DYNAMODB_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=supply-chain-reports-XXXXX
S3_REGION=us-east-1

# SNS Configuration
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts

# Application
LOG_LEVEL=INFO
NODE_ENV=production
```

## Step 3: Run the Workflow (2 minutes)

```bash
python run_with_aws_services.py
```

## What Happens

The script performs a complete supply chain optimization workflow:

### 1. **Inventory Data** → DynamoDB
   - Creates inventory record for product PROD-001
   - Stores: quantity, reorder point, safety stock

### 2. **Demand Forecast** → DynamoDB
   - Analyzes 12 months of sales history
   - Generates 30-day forecast with confidence intervals
   - Stores forecast in DynamoDB

### 3. **Inventory Optimization** → DynamoDB
   - Calculates Economic Order Quantity (EOQ)
   - Determines reorder point
   - Creates purchase order

### 4. **Anomaly Detection** → DynamoDB
   - Detects inventory deviations
   - Checks for anomalies
   - Stores anomaly records

### 5. **Report Generation** → S3
   - Calculates KPIs (inventory turnover, forecast accuracy, supplier reliability)
   - Generates analytics report
   - Saves report to S3 bucket

### 6. **Notifications** → SNS
   - Sends alert if anomaly detected
   - Email notification to subscribers

## Expected Output

```
================================================================================
SUPPLY CHAIN OPTIMIZER - AWS SERVICES WORKFLOW
================================================================================

[VERIFICATION] Checking AWS services...
✓ DynamoDB: 5 tables found
✓ S3: 1 buckets found
✓ SNS: 1 topics found

[STEP 1] Creating inventory data in DynamoDB...
  Saved to DynamoDB table 'inventory': INV-1703084800.123

[STEP 2] Generating demand forecast...
  Forecast: 3000 units
  80% CI: 2700 units
  95% CI: 2400 units

[STEP 3] Optimizing inventory levels...
  EOQ: 1500 units
  Reorder Point: 1000 units
  Current Inventory: 500 units
  ACTION: Reorder needed! Current < Reorder Point

[STEP 4] Creating purchase order...
  PO ID: PO-1703084800.456
  Quantity: 1500 units
  Total Price: $15750.00
  Expected Delivery: 2025-12-27T10:30:00

[STEP 5] Detecting anomalies...
  ALERT: Anomaly detected!
  Severity: medium
  Description: Inventory below reorder point

[STEP 6] Generating analytics report...
  Report ID: RPT-1703084800.789
  Inventory Turnover: 2.45
  Forecast Accuracy: 92.50%
  Supplier Reliability: 95.00%
  Report saved to S3: reports/2025/12/20/report-1703084800.789.json

================================================================================
WORKFLOW SUMMARY
================================================================================
✓ Inventory data saved to DynamoDB
✓ Forecast generated and saved to DynamoDB
✓ Purchase order created and saved to DynamoDB
✓ Anomalies detected and saved to DynamoDB
✓ Report generated and saved to S3
✓ Alert notification sent via SNS

================================================================================
```

## Verify Data in AWS

### Check DynamoDB
```bash
# List items in inventory table
aws dynamodb scan --table-name inventory --region us-east-1

# List items in forecasts table
aws dynamodb scan --table-name forecasts --region us-east-1

# List items in purchase_orders table
aws dynamodb scan --table-name purchase_orders --region us-east-1

# List items in anomalies table
aws dynamodb scan --table-name anomalies --region us-east-1
```

### Check S3
```bash
# List reports
aws s3 ls s3://supply-chain-reports-XXXXX/reports/ --recursive

# Download a report
aws s3 cp s3://supply-chain-reports-XXXXX/reports/2025/12/20/report-*.json ./
```

### Check SNS
```bash
# List topics
aws sns list-topics --region us-east-1

# List subscriptions
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
```

## Troubleshooting

### Error: "Unable to locate credentials"
```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

### Error: "ResourceNotFoundException" for DynamoDB
```bash
# Run setup script again
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux
```

### Error: "AccessDenied"
Check IAM user has these permissions:
- AmazonDynamoDBFullAccess
- AmazonS3FullAccess
- AmazonSNSFullAccess

### Error: "NoCredentialsError"
Verify `.env` file has:
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Run Multiple Times

You can run the script multiple times to generate different data:

```bash
# Run 1
python run_with_aws_services.py

# Run 2 (creates new records with different timestamps)
python run_with_aws_services.py

# Run 3
python run_with_aws_services.py
```

Each run creates new records with unique IDs and timestamps.

## View All Data

```bash
# View all inventory records
aws dynamodb scan --table-name inventory --region us-east-1 --output table

# View all forecasts
aws dynamodb scan --table-name forecasts --region us-east-1 --output table

# View all reports in S3
aws s3 ls s3://supply-chain-reports-XXXXX/reports/ --recursive --human-readable
```

## Next Steps

1. **Run the script** - `python run_with_aws_services.py`
2. **Check AWS Console** - View data in DynamoDB, S3, SNS
3. **Modify the script** - Change product SKUs, quantities, dates
4. **Integrate with API** - Use the REST API endpoints
5. **Deploy to Lambda** - Run on schedule with EventBridge

## Cost

Running this script once costs approximately:
- DynamoDB: $0.0001 (5 writes)
- S3: $0.00001 (1 report)
- SNS: $0.00001 (1 notification)
- **Total: ~$0.00012 per run**

## Support

For issues:
1. Check `.env` file is configured
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Verify AWS resources exist: `aws dynamodb list-tables`
4. Check logs: `python run_with_aws_services.py 2>&1 | tee output.log`
