# What You Need to Do - Quick Start

You have all agents and services in place. Here's exactly what you need to do to use them:

## 3 Simple Steps

### Step 1: Set Up AWS (5 minutes)

**Windows:**
```bash
setup_aws_resources.bat
```

**macOS/Linux:**
```bash
chmod +x setup_aws_resources.sh
./setup_aws_resources.sh
```

This creates all AWS resources automatically.

### Step 2: Configure Environment (2 minutes)

Create `.env` file in project root:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DYNAMODB_REGION=us-east-1
S3_BUCKET_NAME=supply-chain-reports-XXXXX
S3_REGION=us-east-1
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
LOG_LEVEL=INFO
NODE_ENV=production
```

Get the values from the setup script output.

### Step 3: Run the Workflow (2 minutes)

```bash
python run_with_aws_services.py
```

## That's It!

The script will:
1. ✓ Create inventory data in DynamoDB
2. ✓ Generate demand forecast
3. ✓ Optimize inventory levels
4. ✓ Create purchase orders
5. ✓ Detect anomalies
6. ✓ Generate reports and save to S3
7. ✓ Send alerts via SNS

## What Gets Stored Where

| Data | Service | Location |
|------|---------|----------|
| Inventory | DynamoDB | `inventory` table |
| Forecasts | DynamoDB | `forecasts` table |
| Purchase Orders | DynamoDB | `purchase_orders` table |
| Anomalies | DynamoDB | `anomalies` table |
| Reports | S3 | `reports/YYYY/MM/DD/` folder |
| Alerts | SNS | Email notifications |

## Verify It Works

### Check DynamoDB
```bash
aws dynamodb scan --table-name inventory --region us-east-1
```

### Check S3
```bash
aws s3 ls s3://supply-chain-reports-XXXXX/reports/ --recursive
```

### Check SNS
```bash
aws sns list-topics --region us-east-1
```

## Run Multiple Times

Each run creates new data with different timestamps:

```bash
python run_with_aws_services.py  # Run 1
python run_with_aws_services.py  # Run 2
python run_with_aws_services.py  # Run 3
```

## Troubleshooting

### Problem: "Unable to locate credentials"
```bash
aws configure
```

### Problem: "ResourceNotFoundException"
```bash
# Run setup again
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux
```

### Problem: "AccessDenied"
Check IAM user has these permissions:
- AmazonDynamoDBFullAccess
- AmazonS3FullAccess
- AmazonSNSFullAccess

## Files You Need

- `run_with_aws_services.py` - Main script (NEW)
- `setup_aws_resources.bat` - Setup for Windows (EXISTING)
- `setup_aws_resources.sh` - Setup for macOS/Linux (EXISTING)
- `.env` - Configuration file (CREATE)

## Total Time

- Setup: 5 minutes
- Configuration: 2 minutes
- First run: 2 minutes
- **Total: 9 minutes**

## Cost

Running once costs approximately **$0.00012** (less than 1 cent)

## Next

1. Run `python run_with_aws_services.py`
2. Check AWS Console to see your data
3. Modify the script to use your own data
4. Deploy to Lambda for scheduled runs

---

**You're ready to go!** Just run the script and watch the agents work with real AWS services.
