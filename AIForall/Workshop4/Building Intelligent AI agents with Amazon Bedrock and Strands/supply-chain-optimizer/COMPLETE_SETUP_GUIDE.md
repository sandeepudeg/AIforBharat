# Complete Setup Guide - Knowledge Base + DynamoDB Integration

## 🎯 What You Now Have

✅ **Knowledge Base Integration** - Ingest data from Bedrock Knowledge Base
✅ **DynamoDB Storage** - Persist all data in DynamoDB tables
✅ **8 Agent Tools** - Including 2 new KB integration tools
✅ **Sample Data Script** - Populate DynamoDB with test data
✅ **Orchestrator Agent** - Intelligent tool selection and execution

---

## 📋 Quick Start (10 Minutes)

### Option A: Use Sample Data (Fastest)

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Create DynamoDB tables
aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=sku,AttributeType=S \
  --key-schema AttributeName=sku,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# (Repeat for other tables - see QUICK_START_UPDATED_TOOLS.md)

# 3. Ingest sample data
python ingest_sample_data.py

# 4. Run orchestrator
python supply_chain_orchestrator.py
```

### Option B: Use Knowledge Base (Recommended)

```bash
# 1. Create Bedrock Knowledge Base in AWS Console
# 2. Upload your supply chain documents
# 3. Set environment variable
export BEDROCK_KB_ID=your_kb_id

# 4. Run orchestrator
python supply_chain_orchestrator.py

# 5. Ask to sync data
"Sync data from knowledge base"
```

---

## 🔧 Detailed Setup

### Step 1: Environment Configuration

Create `.env` file:

```bash
# AWS Credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB
DYNAMODB_REGION=us-east-1
DYNAMODB_ENDPOINT=  # Leave empty for AWS

# S3 (for reports)
S3_BUCKET_NAME=supply-chain-optimizer-reports

# SNS (for alerts)
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:123456789:alerts

# Bedrock
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_REGION=us-east-1

# Knowledge Base (optional)
BEDROCK_KB_ID=your_knowledge_base_id
```

### Step 2: Create DynamoDB Tables

```bash
# Create all required tables
aws dynamodb create-table \
  --table-name inventory \
  --attribute-definitions AttributeName=sku,AttributeType=S \
  --key-schema AttributeName=sku,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name sales_history \
  --attribute-definitions \
    AttributeName=sku,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=sku,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name suppliers \
  --attribute-definitions AttributeName=supplier_id,AttributeType=S \
  --key-schema AttributeName=supplier_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name forecasts \
  --attribute-definitions AttributeName=forecast_id,AttributeType=S \
  --key-schema AttributeName=forecast_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name purchase_orders \
  --attribute-definitions AttributeName=po_id,AttributeType=S \
  --key-schema AttributeName=po_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name anomalies \
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S \
  --key-schema AttributeName=anomaly_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Step 3: Populate Data

**Option A: Use Sample Data Script**
```bash
python ingest_sample_data.py
```

**Option B: Use Knowledge Base**
```bash
python supply_chain_orchestrator.py
# Then ask: "Sync data from knowledge base"
```

**Option C: Manual Upload**
```python
from src.aws.clients import get_dynamodb_resource

dynamodb = get_dynamodb_resource()
table = dynamodb.Table('inventory')

table.put_item(Item={
    'sku': 'PROD-001',
    'current_quantity': 1500,
    'reorder_point': 200,
    # ... other fields
})
```

### Step 4: Verify Setup

```bash
# Test sample data ingestion
python ingest_sample_data.py

# Test agent tools
python test_agent_tools_standalone.py

# Run orchestrator
python supply_chain_orchestrator.py
```

---

## 🚀 Usage

### Interactive Mode

```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"Sync data from knowledge base"
"Forecast demand for PROD-001"
"Optimize inventory for PROD-001"
"Create a purchase order for 1500 units from SUPP-001"
"Check for anomalies"
"Generate a report"
```

### Programmatic Usage

```python
from src.agents.agent_tools import (
    sync_data_from_knowledge_base,
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status,
    retrieve_from_knowledge_base,
)

# Sync data from knowledge base
result = sync_data_from_knowledge_base()
print(result)

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

# Retrieve from knowledge base
result = retrieve_from_knowledge_base(
    query='PROD-001',
    data_type='inventory'
)
print(result)
```

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  Bedrock Knowledge Base                      │
│              (Documents with supply chain data)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Knowledge Base Manager            │
        │  - Retrieve from KB                │
        │  - Parse documents                 │
        │  - Validate data                   │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │      DynamoDB Tables               │
        │  - inventory                       │
        │  - sales_history                   │
        │  - suppliers                       │
        │  - forecasts                       │
        │  - purchase_orders                 │
        │  - anomalies                       │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │      Agent Tools (8 total)         │
        │  - forecast_demand                 │
        │  - optimize_inventory              │
        │  - create_purchase_order           │
        │  - detect_anomalies                │
        │  - generate_report                 │
        │  - get_inventory_status            │
        │  - sync_data_from_knowledge_base   │
        │  - retrieve_from_knowledge_base    │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │    Orchestrator Agent              │
        │  (Strands with Claude)             │
        └────────────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │      AWS Services                  │
        │  - S3 (reports)                    │
        │  - SNS (alerts)                    │
        │  - CloudWatch (logs)               │
        └────────────────────────────────────┘
```

---

## 🔑 Key Features

### 1. Knowledge Base Integration
- Retrieve data from Bedrock Knowledge Base
- Parse and validate documents
- Store in DynamoDB automatically

### 2. DynamoDB Persistence
- All data stored in DynamoDB
- Automatic metadata tracking
- Source tracking (KB vs manual)

### 3. 8 Agent Tools
- 6 original supply chain tools
- 2 new knowledge base tools
- All integrated with orchestrator

### 4. Intelligent Orchestration
- Natural language understanding
- Automatic tool selection
- Multi-step workflows

### 5. AWS Service Integration
- S3 for report storage
- SNS for alerts
- CloudWatch for logging

---

## 📁 File Structure

```
supply-chain-optimizer/
├── src/
│   ├── agents/
│   │   ├── agent_tools.py                    ← 8 tools (UPDATED)
│   │   ├── knowledge_base_manager.py         ← KB integration (NEW)
│   │   ├── demand_forecasting_agent.py
│   │   ├── inventory_optimizer_agent.py
│   │   ├── supplier_coordination_agent.py
│   │   ├── anomaly_detection_agent.py
│   │   └── report_generation_agent.py
│   ├── aws/
│   │   └── clients.py
│   ├── config/
│   │   ├── environment.py
│   │   └── logger.py
│   └── models/
├── supply_chain_orchestrator.py              ← Orchestrator (UPDATED)
├── ingest_sample_data.py                     ← Data ingestion (NEW)
├── test_agent_tools_standalone.py            ← Tests
├── KNOWLEDGE_BASE_INTEGRATION.md             ← KB guide (NEW)
├── COMPLETE_SETUP_GUIDE.md                   ← This file (NEW)
└── ... (other documentation)
```

---

## 🧪 Testing

### Test 1: Sample Data Ingestion
```bash
python ingest_sample_data.py
```

### Test 2: Agent Tools
```bash
python test_agent_tools_standalone.py
```

### Test 3: Orchestrator
```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"What is the current inventory status for PROD-001?"
```

### Test 4: Knowledge Base Integration
```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"Sync data from knowledge base"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Table not found" | Create DynamoDB tables using AWS CLI |
| "No data found" | Run `python ingest_sample_data.py` |
| "KB not configured" | Set `BEDROCK_KB_ID` environment variable |
| "AWS credentials error" | Check `.env` file has correct credentials |
| "Bedrock model error" | Ensure you have access to Bedrock in your region |

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `KNOWLEDGE_BASE_INTEGRATION.md` | KB setup and usage |
| `AGENTS_AS_TOOLS_UPDATED.md` | Tool documentation |
| `QUICK_START_UPDATED_TOOLS.md` | Quick start guide |
| `IMPLEMENTATION_COMPLETE.md` | System overview |
| `COMPLETE_SETUP_GUIDE.md` | This file |

---

## ✅ Checklist

- [ ] AWS credentials configured
- [ ] `.env` file created
- [ ] DynamoDB tables created
- [ ] Sample data ingested (or KB configured)
- [ ] Tests passing
- [ ] Orchestrator running
- [ ] Tools working with data

---

## 🎉 You're Ready!

Your supply chain optimizer is now fully set up with:
- ✅ Knowledge Base integration
- ✅ DynamoDB persistence
- ✅ 8 intelligent tools
- ✅ Orchestrator agent
- ✅ AWS service integration

Start optimizing your supply chain!

```bash
python supply_chain_orchestrator.py
```

---

## 📞 Support

For issues:
1. Check the troubleshooting section
2. Review the documentation files
3. Check AWS credentials and configuration
4. Verify DynamoDB tables exist
5. Check logs for error messages

---

## 🚀 Next Steps

1. Explore the orchestrator capabilities
2. Create custom supply chain workflows
3. Integrate with your existing systems
4. Monitor and optimize performance
5. Scale to production

Happy optimizing! 🎯
