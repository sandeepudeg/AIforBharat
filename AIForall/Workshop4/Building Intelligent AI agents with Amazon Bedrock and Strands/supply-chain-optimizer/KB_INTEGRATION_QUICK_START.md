# Knowledge Base Integration - Quick Start Guide

## Overview

The system now supports complete Knowledge Base integration with DynamoDB persistence. You can:
- Upload custom data files to S3
- Sync data with Bedrock Knowledge Base
- Retrieve data from KB and store in DynamoDB
- Use agent tools with KB-sourced data

## Quick Start (5 minutes)

### Step 1: Prepare Your Data

Create three JSON files with your supply chain data:

**inventory.json**
```json
[
  {
    "sku": "PROD-001",
    "product_name": "Widget A",
    "current_quantity": 1500,
    "reorder_point": 200,
    "safety_stock": 300,
    "warehouse": "WH-001",
    "lead_time_days": 7,
    "ordering_cost": 50,
    "holding_cost_per_unit": 2,
    "unit_price": 10.50
  }
]
```

**sales_history.json**
```json
[
  {
    "sku": "PROD-001",
    "date": "2024-12-20",
    "quantity": 150,
    "revenue": 1575.00
  }
]
```

**suppliers.json**
```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Supplies Inc",
    "unit_price": 10.50,
    "reliability_score": 0.95,
    "lead_time_days": 7
  }
]
```

### Step 2: Upload Data

```bash
# Run the upload wizard
python upload_custom_kb_data.py

# Follow the prompts:
# 1. Enter S3 bucket name (e.g., my-kb-data-bucket)
# 2. Enter Knowledge Base ID (from AWS console)
# 3. Enter directory with your JSON files
# 4. Choose to sync KB when prompted
```

### Step 3: Configure Environment

```bash
# Set your Knowledge Base ID
export BEDROCK_KB_ID=<your-kb-id>

# Verify AWS credentials are set
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1
```

### Step 4: Test the Integration

```bash
# Run the complete test suite
python test_kb_integration_complete.py

# This tests:
# ✓ S3 bucket creation (with region handling)
# ✓ File upload to S3
# ✓ DynamoDB data ingestion
# ✓ Agent tools execution
# ✓ KB integration (if configured)
```

### Step 5: Use the Orchestrator

```bash
# Start the supply chain orchestrator
python supply_chain_orchestrator.py

# Example queries:
# "Forecast demand for PROD-001"
# "Optimize inventory for PROD-001"
# "Create purchase order for PROD-001 from SUPP-001"
# "Detect anomalies for PROD-001"
# "Generate report"
# "Sync data from knowledge base"
```

## What's Fixed

### S3 Bucket Creation
- ✅ Handles `us-east-1` without LocationConstraint
- ✅ Handles other regions with proper LocationConstraint
- ✅ Checks if bucket exists before creating
- ✅ Proper error handling and logging

### File Upload
- ✅ Validates JSON format
- ✅ Validates data structure (required fields)
- ✅ Uploads to S3 with proper content type
- ✅ Supports inventory, sales history, and supplier files

### KB Sync
- ✅ Starts ingestion job
- ✅ Returns job ID for tracking
- ✅ Handles KB not configured gracefully

### Data Ingestion
- ✅ Reads from S3
- ✅ Stores in DynamoDB tables
- ✅ Adds metadata (ingestion date, source)
- ✅ Handles missing data gracefully

## File Structure

```
supply-chain-optimizer/
├── upload_custom_kb_data.py          # Upload wizard (FIXED)
├── test_kb_integration_complete.py   # Complete test suite (NEW)
├── src/agents/
│   ├── agent_tools.py                # 8 tools (6 + 2 KB tools)
│   ├── knowledge_base_manager.py     # KB operations
│   └── ...
├── ingest_sample_data.py             # Sample data ingestion
└── supply_chain_orchestrator.py      # Main orchestrator
```

## Tools Available

### Core Supply Chain Tools
1. **forecast_demand(sku, forecast_days=30)** - Forecast demand using sales history
2. **optimize_inventory(sku)** - Calculate EOQ and reorder points
3. **create_purchase_order(sku, supplier_id, quantity, delivery_days=7)** - Create PO
4. **detect_anomalies(sku)** - Detect supply chain anomalies
5. **generate_report(sku=None)** - Generate analytics report
6. **get_inventory_status(sku)** - Get current inventory

### Knowledge Base Tools
7. **sync_data_from_knowledge_base()** - Sync all KB data to DynamoDB
8. **retrieve_from_knowledge_base(query, data_type)** - Retrieve specific KB data

## Troubleshooting

### "BEDROCK_KB_ID not set"
```bash
# Set the environment variable
export BEDROCK_KB_ID=<your-kb-id>

# Verify it's set
echo $BEDROCK_KB_ID
```

### "S3 bucket creation failed"
- Check AWS credentials
- Verify IAM permissions for S3
- Ensure bucket name is globally unique
- Check region configuration

### "No data found in DynamoDB"
- Run `python ingest_sample_data.py` to populate with sample data
- Or use `python upload_custom_kb_data.py` to upload your own data
- Verify DynamoDB tables exist: inventory, sales_history, suppliers

### "KB sync failed"
- Verify BEDROCK_KB_ID is correct
- Check KB is properly configured in AWS console
- Ensure data source is connected to KB
- Wait a few minutes for KB to process documents

## Next Steps

1. **Customize Data**: Replace sample data with your actual supply chain data
2. **Set Up Alerts**: Configure SNS topic for anomaly alerts
3. **Schedule Reports**: Set up CloudWatch Events to trigger reports
4. **Monitor Performance**: Check CloudWatch logs for agent execution
5. **Integrate with Systems**: Connect to your ERP/inventory systems

## Support

For issues or questions:
1. Check the logs: `tail -f logs/supply_chain_optimizer.log`
2. Run tests: `python test_kb_integration_complete.py`
3. Review documentation: See `BEDROCK_KB_SETUP_GUIDE.md`
4. Check AWS console for KB and DynamoDB status

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Data Files                          │
│              (inventory.json, sales.json, etc)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   S3 Bucket                                 │
│            (supply-chain-data/ prefix)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Bedrock Knowledge Base                           │
│         (Processes & indexes documents)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              DynamoDB Tables                                │
│  (inventory, sales_history, suppliers, forecasts, etc)     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Tools                                    │
│  (forecast, optimize, create_po, detect_anomalies, etc)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Strands Agent Orchestrator                          │
│         (Intelligent decision making)                       │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated**: December 20, 2024
**Status**: ✅ Complete and Tested
