# START HERE - Quick Guide

You're in the supply-chain-optimizer directory. Here's what to do:

## Option 1: Run with AWS Services (Real Data)

```bash
python run_with_aws_services.py
```

This will:
- Create inventory data in DynamoDB
- Generate demand forecasts
- Optimize inventory levels
- Detect anomalies
- Generate reports and save to S3
- Send alerts via SNS

**Prerequisites:**
1. AWS account configured: `aws configure`
2. AWS resources created: `setup_aws_resources.bat` (Windows) or `./setup_aws_resources.sh` (macOS/Linux)
3. `.env` file configured with AWS credentials

See `WHAT_YOU_NEED_TO_DO.md` for detailed setup.

---

## Option 2: Run Demo (Dummy Data)

```bash
python demo.py
```

This demonstrates all agents with sample data (no AWS required).

---

## Option 3: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_demand_forecasting_agent.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

See `RUN_TESTS.md` for more test options.

---

## Option 4: Test AWS Services

```bash
# Test DynamoDB
python test_aws_dynamodb.py

# Test S3
python test_aws_s3.py

# Test SNS
python test_aws_sns.py

# Test RDS (optional)
python test_aws_rds.py
```

---

## Quick Setup for AWS (9 minutes)

### 1. Configure AWS
```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

### 2. Create Resources
```bash
# Windows
setup_aws_resources.bat

# macOS/Linux
chmod +x setup_aws_resources.sh
./setup_aws_resources.sh
```

### 3. Create .env File
```bash
# Copy values from setup script output
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=supply-chain-reports-XXXXX
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
LOG_LEVEL=INFO
NODE_ENV=production
```

### 4. Run Workflow
```bash
python run_with_aws_services.py
```

---

## What You Have

### 5 Agents
1. **Demand Forecasting Agent** - Generates 30-day forecasts
2. **Inventory Optimizer Agent** - Calculates EOQ and reorder points
3. **Supplier Coordination Agent** - Manages purchase orders
4. **Anomaly Detection Agent** - Detects inventory issues
5. **Report Generation Agent** - Creates analytics reports

### 8 Services
1. Orchestration Service
2. Notification Service
3. Archival Service
4. Data Integrity Service
5. Warehouse Manager
6. Observability/Monitoring
7. API Layer
8. Database Layer

### AWS Integration
- **DynamoDB** - Real-time data storage
- **S3** - Report storage
- **SNS** - Alert notifications
- **RDS** - Relational data (optional)

---

## Files to Read

| File | Purpose |
|------|---------|
| `WHAT_YOU_NEED_TO_DO.md` | 3-step quick start |
| `QUICK_START_COMMANDS.txt` | Copy-paste commands |
| `RUN_WITH_AWS.md` | Detailed AWS setup |
| `RUN_TESTS.md` | How to run tests |
| `SYSTEM_FLOW_DIAGRAM.txt` | Visual system flow |
| `DELIVERY_SUMMARY.md` | Complete overview |

---

## Troubleshooting

### Error: "Unable to locate credentials"
```bash
aws configure
```

### Error: "ResourceNotFoundException"
```bash
# Run setup again
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux
```

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "NameError: name 'null' is not defined"
Don't run `python -m src.test` - that file doesn't exist.
Use the commands above instead.

---

## Next Steps

1. **Choose an option above** (AWS, Demo, or Tests)
2. **Follow the setup steps** if needed
3. **Run the command**
4. **Check the output**

---

**Ready to go!** Pick an option and run it.
