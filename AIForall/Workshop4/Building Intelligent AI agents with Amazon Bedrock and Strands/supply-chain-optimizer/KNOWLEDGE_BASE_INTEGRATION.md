# Knowledge Base Integration Guide

## Overview

The supply chain optimizer now integrates with AWS Bedrock Knowledge Base for data ingestion and retrieval. This allows you to:

1. **Ingest data** from knowledge base documents into DynamoDB
2. **Retrieve data** from knowledge base for specific queries
3. **Sync all data** from knowledge base to DynamoDB
4. **Use knowledge base data** with all agent tools

---

## Setup

### Step 1: Create Bedrock Knowledge Base

1. Go to AWS Console → Bedrock → Knowledge Bases
2. Click "Create Knowledge Base"
3. Configure:
   - Name: `supply-chain-optimizer-kb`
   - Model: Claude 3 Sonnet
   - Storage: S3 bucket
4. Note the Knowledge Base ID (e.g., `XXXXXXXXXX`)

### Step 2: Upload Documents

Upload your supply chain data as documents:

**Example: inventory.json**
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

**Example: sales_history.json**
```json
[
  {
    "sku": "PROD-001",
    "date": "2025-12-01",
    "quantity": 100,
    "revenue": 1050
  }
]
```

**Example: suppliers.json**
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

### Step 3: Configure Environment

Add to `.env`:
```bash
BEDROCK_KB_ID=your_knowledge_base_id
```

---

## Usage

### Option 1: Sync All Data from Knowledge Base

```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"Sync data from knowledge base"
```

This will:
1. Retrieve all inventory data from KB
2. Retrieve all sales history from KB
3. Retrieve all supplier data from KB
4. Store everything in DynamoDB

### Option 2: Retrieve Specific Data

```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"Retrieve inventory data for PROD-001 from knowledge base"
"Retrieve sales history from knowledge base"
"Retrieve supplier information from knowledge base"
```

### Option 3: Use Knowledge Base Manager Directly

```python
from src.agents.knowledge_base_manager import KnowledgeBaseManager

# Initialize
kb_manager = KnowledgeBaseManager(knowledge_base_id="your_kb_id")

# Sync all data
results = kb_manager.sync_all_data()
print(results)

# Retrieve specific data
inventory = kb_manager.retrieve_and_store_inventory()
sales = kb_manager.retrieve_and_store_sales_history()
suppliers = kb_manager.retrieve_and_store_suppliers()

# Get specific item
item = kb_manager.get_inventory_from_kb("PROD-001")
print(item)
```

---

## New Tools

### 1. sync_data_from_knowledge_base

Syncs all data from knowledge base to DynamoDB.

**Usage**:
```python
from src.agents.agent_tools import sync_data_from_knowledge_base

result = sync_data_from_knowledge_base()
print(result)
```

**Response**:
```json
{
  "status": "success",
  "inventory_synced": true,
  "sales_history_synced": true,
  "suppliers_synced": true,
  "message": "Data sync complete: {...}"
}
```

### 2. retrieve_from_knowledge_base

Retrieves specific data from knowledge base and stores in DynamoDB.

**Usage**:
```python
from src.agents.agent_tools import retrieve_from_knowledge_base

result = retrieve_from_knowledge_base(
    query="PROD-001",
    data_type="inventory"
)
print(result)
```

**Parameters**:
- `query`: Search query
- `data_type`: Type of data (inventory, sales_history, suppliers)

**Response**:
```json
{
  "status": "success",
  "query": "PROD-001",
  "data_type": "inventory",
  "results_found": 1,
  "results_stored": 1,
  "message": "Retrieved and stored 1 inventory records"
}
```

---

## Data Flow

```
Knowledge Base Documents
        ↓
Bedrock Retrieval API
        ↓
Knowledge Base Manager
        ↓
Parse & Validate
        ↓
DynamoDB Tables
        ↓
Agent Tools
        ↓
Orchestrator Agent
        ↓
User Response
```

---

## Sample Data Ingestion

If you don't have a knowledge base yet, use the sample data ingestion script:

```bash
python ingest_sample_data.py
```

This will:
1. Create sample inventory data
2. Create sample sales history
3. Create sample supplier data
4. Store everything in DynamoDB

Then you can use all agent tools immediately.

---

## Knowledge Base Manager API

### Methods

#### retrieve_from_knowledge_base(query, max_results=10)
Retrieve documents from knowledge base.

#### ingest_inventory_data(inventory_data)
Ingest inventory items into DynamoDB.

#### ingest_sales_history(sales_data)
Ingest sales records into DynamoDB.

#### ingest_supplier_data(supplier_data)
Ingest supplier records into DynamoDB.

#### retrieve_and_store_inventory(query="inventory")
Retrieve inventory from KB and store in DynamoDB.

#### retrieve_and_store_sales_history(query="sales history")
Retrieve sales history from KB and store in DynamoDB.

#### retrieve_and_store_suppliers(query="suppliers")
Retrieve suppliers from KB and store in DynamoDB.

#### sync_all_data()
Sync all data types from KB to DynamoDB.

#### get_inventory_from_kb(sku)
Get inventory for specific SKU from KB.

#### get_sales_history_from_kb(sku)
Get sales history for specific SKU from KB.

#### get_supplier_from_kb(supplier_id)
Get supplier data from KB.

---

## Document Format

### Inventory Documents

```json
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
  "unit_price": 10.50,
  "category": "Electronics"
}
```

### Sales History Documents

```json
{
  "sku": "PROD-001",
  "date": "2025-12-01",
  "quantity": 100,
  "revenue": 1050,
  "warehouse": "WH-001"
}
```

### Supplier Documents

```json
{
  "supplier_id": "SUPP-001",
  "name": "Global Supplies Inc",
  "contact_email": "contact@globalsupplies.com",
  "unit_price": 10.50,
  "reliability_score": 0.95,
  "lead_time_days": 7,
  "min_order_quantity": 100,
  "payment_terms": "Net 30",
  "location": "USA",
  "rating": 4.8
}
```

---

## Workflow Example

### Step 1: Sync Data from Knowledge Base
```
User: "Sync data from knowledge base"
Agent: Calls sync_data_from_knowledge_base()
Result: All data stored in DynamoDB
```

### Step 2: Forecast Demand
```
User: "Forecast demand for PROD-001"
Agent: Calls forecast_demand(sku='PROD-001')
Tool: Reads sales history from DynamoDB (synced from KB)
Result: Forecast generated
```

### Step 3: Optimize Inventory
```
User: "Optimize inventory for PROD-001"
Agent: Calls optimize_inventory(sku='PROD-001')
Tool: Reads inventory and sales from DynamoDB (synced from KB)
Result: EOQ and reorder point calculated
```

### Step 4: Create Purchase Order
```
User: "Create purchase order for 1500 units from SUPP-001"
Agent: Calls create_purchase_order(sku='PROD-001', supplier_id='SUPP-001', quantity=1500)
Tool: Reads supplier data from DynamoDB (synced from KB)
Result: Purchase order created
```

---

## Troubleshooting

### Issue: "Knowledge Base not configured"
**Solution**: Set `BEDROCK_KB_ID` environment variable

### Issue: "No results found in knowledge base"
**Solution**: 
1. Verify documents are uploaded to KB
2. Check document format is correct
3. Use sample data ingestion script

### Issue: "Could not parse JSON from knowledge base"
**Solution**: Ensure documents are valid JSON format

### Issue: "DynamoDB table not found"
**Solution**: Create DynamoDB tables first using AWS CLI

---

## Best Practices

1. **Upload documents in JSON format** - Easier to parse and store
2. **Include all required fields** - sku, date, supplier_id, etc.
3. **Sync regularly** - Keep DynamoDB updated with latest KB data
4. **Use descriptive queries** - Better retrieval results
5. **Validate data** - Check data quality before ingestion

---

## Integration with Orchestrator

The orchestrator automatically:
1. Detects if KB is configured
2. Offers sync and retrieve options
3. Uses KB data for all operations
4. Stores results in DynamoDB

Example conversation:
```
User: "Help me optimize my supply chain"
Agent: "I can help! First, let me sync data from your knowledge base."
Agent: Calls sync_data_from_knowledge_base()
Agent: "Data synced! Now I can forecast demand, optimize inventory, and create purchase orders."
```

---

## Files

- `src/agents/knowledge_base_manager.py` - Knowledge Base Manager class
- `src/agents/agent_tools.py` - Updated tools with KB integration
- `supply_chain_orchestrator.py` - Updated orchestrator
- `ingest_sample_data.py` - Sample data ingestion script
- `KNOWLEDGE_BASE_INTEGRATION.md` - This file

---

## Next Steps

1. ✅ Create Bedrock Knowledge Base
2. ✅ Upload supply chain documents
3. ✅ Set BEDROCK_KB_ID environment variable
4. ✅ Run orchestrator: `python supply_chain_orchestrator.py`
5. ✅ Ask to sync data from knowledge base
6. ✅ Use all agent tools with KB data
