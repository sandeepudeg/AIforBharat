# Complete Workflow Guide - Knowledge Base Integration

## End-to-End Workflow

This guide walks you through the complete workflow from data preparation to using the agent orchestrator.

---

## Phase 1: Data Preparation (10 minutes)

### Step 1.1: Create Data Directory
```bash
mkdir my_supply_chain_data
cd my_supply_chain_data
```

### Step 1.2: Create inventory.json
```json
[
  {
    "sku": "PROD-001",
    "product_name": "Premium Widget",
    "current_quantity": 2500,
    "reorder_point": 300,
    "safety_stock": 500,
    "warehouse": "WH-MAIN",
    "lead_time_days": 7,
    "ordering_cost": 75,
    "holding_cost_per_unit": 2.5,
    "unit_price": 12.99,
    "category": "Electronics"
  },
  {
    "sku": "PROD-002",
    "product_name": "Standard Widget",
    "current_quantity": 1200,
    "reorder_point": 200,
    "safety_stock": 300,
    "warehouse": "WH-SECONDARY",
    "lead_time_days": 5,
    "ordering_cost": 50,
    "holding_cost_per_unit": 1.8,
    "unit_price": 8.99,
    "category": "Electronics"
  }
]
```

### Step 1.3: Create sales_history.json
```json
[
  {
    "sku": "PROD-001",
    "date": "2024-12-20",
    "quantity": 250,
    "revenue": 3247.50,
    "warehouse": "WH-MAIN"
  },
  {
    "sku": "PROD-001",
    "date": "2024-12-19",
    "quantity": 280,
    "revenue": 3637.20,
    "warehouse": "WH-MAIN"
  },
  {
    "sku": "PROD-001",
    "date": "2024-12-18",
    "quantity": 220,
    "revenue": 2857.80,
    "warehouse": "WH-MAIN"
  },
  {
    "sku": "PROD-002",
    "date": "2024-12-20",
    "quantity": 150,
    "revenue": 1348.50,
    "warehouse": "WH-SECONDARY"
  },
  {
    "sku": "PROD-002",
    "date": "2024-12-19",
    "quantity": 180,
    "revenue": 1618.20,
    "warehouse": "WH-SECONDARY"
  },
  {
    "sku": "PROD-002",
    "date": "2024-12-18",
    "quantity": 160,
    "revenue": 1438.40,
    "warehouse": "WH-SECONDARY"
  }
]
```

### Step 1.4: Create suppliers.json
```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Electronics Supply",
    "contact_email": "sales@globalsupply.com",
    "contact_phone": "+1-555-0101",
    "unit_price": 12.99,
    "reliability_score": 0.96,
    "lead_time_days": 7,
    "min_order_quantity": 100,
    "payment_terms": "Net 30",
    "location": "USA",
    "rating": 4.9
  },
  {
    "supplier_id": "SUPP-002",
    "name": "Asia Tech Distributors",
    "contact_email": "orders@asiatech.com",
    "contact_phone": "+86-10-1234-5678",
    "unit_price": 11.50,
    "reliability_score": 0.89,
    "lead_time_days": 14,
    "min_order_quantity": 500,
    "payment_terms": "Net 45",
    "location": "China",
    "rating": 4.6
  },
  {
    "supplier_id": "SUPP-003",
    "name": "European Components Ltd",
    "contact_email": "info@eucomponents.eu",
    "contact_phone": "+49-30-1234-5678",
    "unit_price": 13.50,
    "reliability_score": 0.94,
    "lead_time_days": 5,
    "min_order_quantity": 200,
    "payment_terms": "Net 30",
    "location": "Germany",
    "rating": 4.8
  }
]
```

---

## Phase 2: AWS Setup (15 minutes)

### Step 2.1: Verify AWS Credentials
```bash
# Check if credentials are configured
aws sts get-caller-identity

# If not, configure them
aws configure
# Enter: Access Key ID, Secret Access Key, Default region, Output format
```

### Step 2.2: Create S3 Bucket (Optional - Script Creates It)
```bash
# The upload script will create the bucket automatically
# But you can pre-create if you prefer:
aws s3 mb s3://my-kb-data-bucket --region us-east-1
```

### Step 2.3: Create Bedrock Knowledge Base
```bash
# 1. Go to AWS Console → Bedrock → Knowledge Bases
# 2. Click "Create Knowledge Base"
# 3. Enter name: "supply-chain-kb"
# 4. Create new S3 bucket or use existing
# 5. Create new IAM role or use existing
# 6. Click "Create Knowledge Base"
# 7. Copy the Knowledge Base ID (looks like: kb-XXXXXXXXXX)
```

### Step 2.4: Set Environment Variables
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Set Knowledge Base ID
export BEDROCK_KB_ID=kb-XXXXXXXXXX

# Verify
echo $BEDROCK_KB_ID
```

---

## Phase 3: Data Upload (5 minutes)

### Step 3.1: Run Upload Wizard
```bash
cd /path/to/supply-chain-optimizer
python upload_custom_kb_data.py
```

### Step 3.2: Follow Prompts
```
Enter S3 bucket name: my-kb-data-bucket
Enter Knowledge Base ID: kb-XXXXXXXXXX
Enter directory containing your data files: /path/to/my_supply_chain_data
```

### Step 3.3: Confirm Upload
```
📦 Found inventory file: /path/to/my_supply_chain_data/inventory.json
✓ Valid inventory data: 2 items
✓ Uploaded to S3: s3://my-kb-data-bucket/supply-chain-data/inventory.json

📊 Found sales history file: /path/to/my_supply_chain_data/sales_history.json
✓ Valid sales history data: 6 records
✓ Uploaded to S3: s3://my-kb-data-bucket/supply-chain-data/sales_history.json

🏭 Found supplier file: /path/to/my_supply_chain_data/suppliers.json
✓ Valid supplier data: 3 suppliers
✓ Uploaded to S3: s3://my-kb-data-bucket/supply-chain-data/suppliers.json

Sync Knowledge Base now? (y/n): y
```

### Step 3.4: Wait for KB Processing
```
🔄 Syncing Knowledge Base: kb-XXXXXXXXXX
✓ Sync job started: ingestion-job-XXXXXXXXXX
ℹ️  This may take a few minutes...
```

---

## Phase 4: Testing (5 minutes)

### Step 4.1: Run Test Suite
```bash
python test_kb_integration_complete.py
```

### Step 4.2: Expected Output
```
======================================================================
  KNOWLEDGE BASE INTEGRATION - COMPLETE TEST SUITE
======================================================================

======================================================================
  CREATING TEST DATA FILES
======================================================================

✓ Created: test_data/inventory.json
✓ Created: test_data/sales_history.json
✓ Created: test_data/suppliers.json

======================================================================
  TEST 1: S3 BUCKET CREATION
======================================================================

Region: us-east-1
Bucket name: kbtest1734700000
Creating bucket without LocationConstraint (us-east-1)...
✓ Bucket created successfully: kbtest1734700000

======================================================================
  TEST 2: FILE UPLOAD TO S3
======================================================================

✓ Uploaded: s3://kbtest1734700000/supply-chain-data/inventory.json
✓ Uploaded: s3://kbtest1734700000/supply-chain-data/sales_history.json
✓ Uploaded: s3://kbtest1734700000/supply-chain-data/suppliers.json

✓ Successfully uploaded 3 files

======================================================================
  TEST 3: DYNAMODB DATA INGESTION
======================================================================

Ingesting inventory data...
✓ Inventory ingested
Ingesting sales history...
✓ Sales history ingested (12 records)
Ingesting supplier data...
✓ Supplier ingested

✓ All data ingested successfully

======================================================================
  TEST 4: AGENT TOOLS EXECUTION
======================================================================

Testing get_inventory_status...
  Result: Inventory for TEST-001: 1500 units
✓ get_inventory_status passed

Testing forecast_demand...
  Result: Forecast generated for TEST-001: 1200 units
✓ forecast_demand passed

Testing optimize_inventory...
  Result: Optimal order quantity: 450 units, Reorder at: 350 units
✓ optimize_inventory passed

Testing create_purchase_order...
  Result: Purchase order created: PO-1734700000 for 500 units
✓ create_purchase_order passed

Testing detect_anomalies...
  Result: Anomaly detection complete for TEST-001: No anomaly
✓ detect_anomalies passed

Testing generate_report...
  Result: Report generated: RPT-1734700000
✓ generate_report passed

✓ All agent tools executed successfully

======================================================================
  TEST 5: KNOWLEDGE BASE INTEGRATION
======================================================================

Knowledge Base ID: kb-XXXXXXXXXX

Testing sync_data_from_knowledge_base...
  Result: Data sync complete: {'inventory': True, 'sales_history': True, 'suppliers': True}
✓ sync_data_from_knowledge_base passed

Testing retrieve_from_knowledge_base...
  Result: Retrieved and stored 3 inventory records
✓ retrieve_from_knowledge_base passed

✓ Knowledge Base integration tests complete

======================================================================
  CLEANUP
======================================================================

✓ Deleted S3 bucket: kbtest1734700000
✓ Deleted test data directory: test_data

======================================================================
  TEST SUMMARY
======================================================================

✓ PASSED: S3 Bucket Creation
✓ PASSED: File Upload
✓ PASSED: DynamoDB Ingestion
✓ PASSED: Agent Tools
✓ PASSED: KB Integration

Total: 5/5 tests passed

✅ ALL TESTS PASSED!
```

---

## Phase 5: Using the Orchestrator (Ongoing)

### Step 5.1: Start the Orchestrator
```bash
python supply_chain_orchestrator.py
```

### Step 5.2: Example Queries

#### Query 1: Forecast Demand
```
You: Forecast demand for PROD-001 for the next 30 days

Agent: I'll forecast the demand for PROD-001 using historical sales data.
Forecasted demand: 7,500 units
Confidence (80%): 7,125 units
Confidence (95%): 6,750 units
```

#### Query 2: Optimize Inventory
```
You: What's the optimal inventory level for PROD-001?

Agent: I'll calculate the optimal inventory parameters for PROD-001.
Economic Order Quantity (EOQ): 450 units
Reorder Point: 350 units
Annual Demand: 6,000 units
Current Inventory: 2,500 units
```

#### Query 3: Create Purchase Order
```
You: Create a purchase order for PROD-001 from SUPP-001 for 1000 units

Agent: I'll create a purchase order with the best supplier.
Purchase Order ID: PO-1734700000
Supplier: Global Electronics Supply
Quantity: 1,000 units
Unit Price: $12.99
Total: $12,990.00
Delivery Date: 2024-12-27
```

#### Query 4: Detect Anomalies
```
You: Check for any supply chain anomalies for PROD-001

Agent: I'll analyze the inventory and sales data for anomalies.
Status: No anomalies detected
Current Inventory: 2,500 units
Forecasted Demand: 7,500 units
Confidence Level: High
```

#### Query 5: Generate Report
```
You: Generate a supply chain report

Agent: I'll generate a comprehensive analytics report.
Report ID: RPT-1734700000
Inventory Turnover: 2.4x
Forecast Accuracy: 92%
Supplier Reliability: 93%
Report saved to: s3://my-bucket/reports/2024/12/20/report-1734700000.json
```

#### Query 6: Sync Knowledge Base
```
You: Sync data from the knowledge base

Agent: I'll sync all data from the knowledge base to DynamoDB.
Inventory synced: ✓
Sales history synced: ✓
Suppliers synced: ✓
Total records synced: 45
```

---

## Phase 6: Monitoring & Maintenance

### Step 6.1: Check Logs
```bash
# View recent logs
tail -f logs/supply_chain_optimizer.log

# Search for errors
grep ERROR logs/supply_chain_optimizer.log

# Search for specific SKU
grep PROD-001 logs/supply_chain_optimizer.log
```

### Step 6.2: Monitor DynamoDB
```bash
# Check inventory table
aws dynamodb scan --table-name inventory --region us-east-1

# Check sales history
aws dynamodb scan --table-name sales_history --region us-east-1

# Check suppliers
aws dynamodb scan --table-name suppliers --region us-east-1
```

### Step 6.3: Monitor S3
```bash
# List uploaded files
aws s3 ls s3://my-kb-data-bucket/supply-chain-data/ --recursive

# Check file sizes
aws s3 ls s3://my-kb-data-bucket/supply-chain-data/ --recursive --human-readable
```

### Step 6.4: Update Data
```bash
# To update data, simply:
# 1. Modify your JSON files
# 2. Run upload_custom_kb_data.py again
# 3. Choose to sync KB
# 4. Data will be updated in DynamoDB
```

---

## Troubleshooting

### Issue: "BEDROCK_KB_ID not set"
```bash
# Solution: Set the environment variable
export BEDROCK_KB_ID=kb-XXXXXXXXXX
echo $BEDROCK_KB_ID  # Verify it's set
```

### Issue: "S3 bucket creation failed"
```bash
# Solution: Check AWS credentials and permissions
aws sts get-caller-identity
aws s3 ls  # Test S3 access
```

### Issue: "No data found in DynamoDB"
```bash
# Solution: Ingest sample data first
python ingest_sample_data.py

# Or upload your own data
python upload_custom_kb_data.py
```

### Issue: "KB sync failed"
```bash
# Solution: Wait a few minutes and try again
# KB processing takes time. Check AWS console for status.
```

### Issue: "Agent tool returned error"
```bash
# Solution: Check logs for details
tail -f logs/supply_chain_optimizer.log

# Verify data exists in DynamoDB
aws dynamodb scan --table-name inventory --region us-east-1
```

---

## Quick Reference Commands

```bash
# Setup
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
export BEDROCK_KB_ID=kb-XXXXXXXXXX

# Data preparation
python ingest_sample_data.py
python upload_custom_kb_data.py

# Testing
python test_kb_integration_complete.py

# Usage
python supply_chain_orchestrator.py

# Monitoring
tail -f logs/supply_chain_optimizer.log
aws dynamodb scan --table-name inventory --region us-east-1
aws s3 ls s3://my-kb-data-bucket/ --recursive
```

---

**Last Updated**: December 20, 2024
**Status**: ✅ Complete
