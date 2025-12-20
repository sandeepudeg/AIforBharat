# Quick Start - Updated Agent Tools with DynamoDB

## What Changed

The agent tools have been updated to:
- ✅ Read data from DynamoDB instead of accepting parameters
- ✅ Write results to DynamoDB for persistence
- ✅ Handle missing data gracefully with defaults
- ✅ Integrate with AWS services (S3, SNS)

## Setup

### 1. Environment Variables

Create a `.env` file with:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB
DYNAMODB_REGION=us-east-1
DYNAMODB_ENDPOINT=  # Leave empty for AWS, or set to http://localhost:8000 for local

# S3
S3_BUCKET_NAME=supply-chain-optimizer-reports

# SNS
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:123456789:supply-chain-alerts

# Bedrock
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_REGION=us-east-1
```

### 2. Create DynamoDB Tables

Use the AWS CLI or console to create these tables:

```bash
# inventory table
aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=sku,AttributeType=S \
  --key-schema AttributeName=sku,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# sales_history table
aws dynamodb create-table \
  --table-name sales_history \
  --attribute-definitions \
    AttributeName=sku,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=sku,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# suppliers table
aws dynamodb create-table \
  --table-name suppliers \
  --attribute-definitions AttributeName=supplier_id,AttributeType=S \
  --key-schema AttributeName=supplier_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# forecasts table
aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# purchase_orders table
aws dynamodb create-table \
  --table-name purchase_orders \
  --attribute-definitions AttributeName=po_id,AttributeType=S \
  --key-schema AttributeName=po_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# anomalies table
aws dynamodb create-table \
  --table-name anomalies \
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S \
  --key-schema AttributeName=anomaly_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 3. Seed Sample Data

Add sample data to DynamoDB:

```python
from src.aws.clients import get_dynamodb_resource
from datetime import datetime, timedelta

dynamodb = get_dynamodb_resource()

# Add inventory
inventory_table = dynamodb.Table('inventory')
inventory_table.put_item(Item={
    'sku': 'PROD-001',
    'current_quantity': 1500,
    'reorder_point': 200,
    'safety_stock': 300,
    'warehouse': 'WH-001',
    'lead_time_days': 7,
    'ordering_cost': 50,
    'holding_cost_per_unit': 2
})

# Add sales history
sales_table = dynamodb.Table('sales_history')
for i in range(12):
    date = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d')
    sales_table.put_item(Item={
        'sku': 'PROD-001',
        'date': date,
        'quantity': 100 + (i * 5),
        'revenue': (100 + (i * 5)) * 10.50
    })

# Add supplier
suppliers_table = dynamodb.Table('suppliers')
suppliers_table.put_item(Item={
    'supplier_id': 'SUPP-001',
    'name': 'Supplier A',
    'unit_price': 10.50,
    'reliability_score': 0.95,
    'lead_time_days': 7
})
```

## Usage

### Option 1: Use Orchestrator Agent (Interactive)

```bash
python supply_chain_orchestrator.py
```

Then ask questions like:
- "Forecast demand for PROD-001"
- "Optimize inventory for PROD-001"
- "Create a purchase order for 1500 units of PROD-001 from SUPP-001"
- "Check for anomalies in PROD-001"
- "Generate a report"

### Option 2: Use Tools Directly

```python
from src.agents.agent_tools import (
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status
)

# Forecast demand
result = forecast_demand(sku='PROD-001', forecast_days=30)
print(result)

# Optimize inventory
result = optimize_inventory(sku='PROD-001')
print(result)

# Create purchase order
result = create_purchase_order(
    sku='PROD-001',
    supplier_id='SUPP-001',
    quantity=1500,
    delivery_days=7
)
print(result)

# Detect anomalies
result = detect_anomalies(sku='PROD-001')
print(result)

# Generate report
result = generate_report(sku='PROD-001')
print(result)

# Get inventory status
result = get_inventory_status(sku='PROD-001')
print(result)
```

### Option 3: Run Tests

```bash
python test_agent_tools_standalone.py
```

## Tool Signatures (Updated)

All tools now have simplified signatures:

```python
# 1. Forecast demand (reads from sales_history)
forecast_demand(sku: str, forecast_days: int = 30)

# 2. Optimize inventory (reads from inventory + sales_history)
optimize_inventory(sku: str)

# 3. Create purchase order (reads from suppliers)
create_purchase_order(sku: str, supplier_id: str, quantity: int, delivery_days: int = 7)

# 4. Detect anomalies (reads from inventory + forecasts)
detect_anomalies(sku: str)

# 5. Generate report (reads from inventory + forecasts + suppliers)
generate_report(sku: Optional[str] = None)

# 6. Get inventory status (reads from inventory)
get_inventory_status(sku: str)
```

## Data Flow

```
User Query
    ↓
Orchestrator Agent
    ↓
Tool Selection
    ↓
Tool Execution
    ├─ Read from DynamoDB
    ├─ Process with Agent
    ├─ Write to DynamoDB
    └─ Send to AWS Services (S3, SNS)
    ↓
Response to User
```

## Troubleshooting

### "Table not found" Error
- Ensure all DynamoDB tables are created
- Check table names match exactly

### "No data found" Warning
- This is normal - tools use default values
- Add sample data to DynamoDB using the seed script

### AWS Credentials Error
- Check `.env` file has correct credentials
- Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### Bedrock Model Error
- Ensure you have access to Bedrock in your AWS region
- Check BEDROCK_MODEL_ID is correct

## Next Steps

1. ✅ Set up environment variables
2. ✅ Create DynamoDB tables
3. ✅ Seed sample data
4. ✅ Run tests: `python test_agent_tools_standalone.py`
5. ✅ Try orchestrator: `python supply_chain_orchestrator.py`
6. ✅ Integrate into your application

## Documentation

- Full tool documentation: `AGENTS_AS_TOOLS_UPDATED.md`
- Architecture overview: `AGENTS_AS_TOOLS_ARCHITECTURE.txt`
- System workflow: `SYSTEM_FLOW_DIAGRAM.txt`
