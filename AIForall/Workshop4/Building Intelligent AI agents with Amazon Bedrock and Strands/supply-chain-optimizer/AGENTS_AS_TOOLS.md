# Using Agents as Tools

Your supply chain agents are now available as **tools** that can be called by a Strands Agent orchestrator.

## What You Have

### 6 Agent Tools

1. **forecast_demand** - Generate demand forecasts
2. **optimize_inventory** - Calculate optimal order quantities
3. **create_purchase_order** - Place orders with suppliers
4. **detect_anomalies** - Identify supply chain issues
5. **generate_report** - Create analytics reports
6. **get_inventory_status** - Check current inventory

### Master Orchestrator Agent

A Strands Agent that can use all 6 tools to perform complex supply chain operations.

## How to Use

### Option 1: Interactive Mode

```bash
python supply_chain_orchestrator.py
```

Then ask questions like:
- "Forecast demand for PROD-001"
- "Optimize inventory for PROD-001"
- "Create a purchase order for 1500 units"
- "Check for anomalies in PROD-001"
- "Generate a report"

### Option 2: Example Workflow

```bash
python supply_chain_orchestrator.py --example
```

This runs a complete example showing all tools in action.

## Tool Definitions

### 1. forecast_demand

**Purpose**: Generate demand forecasts with confidence intervals

**Parameters**:
- `sku` (string): Product SKU (e.g., 'PROD-001')
- `sales_data` (list): Historical sales records
- `forecast_days` (int): Days to forecast (default: 30)

**Returns**:
```json
{
  "status": "success",
  "forecast_id": "FCST-1703084800.456",
  "sku": "PROD-001",
  "forecasted_demand": 3000,
  "confidence_80": 2700,
  "confidence_95": 2400,
  "message": "Forecast generated for PROD-001: 3000 units"
}
```

**Example**:
```python
forecast_demand(
    sku='PROD-001',
    sales_data=[
        {'date': '2024-01-01', 'quantity': 100},
        {'date': '2024-01-02', 'quantity': 105},
        {'date': '2024-01-03', 'quantity': 98},
    ],
    forecast_days=30
)
```

---

### 2. optimize_inventory

**Purpose**: Calculate optimal order quantities and reorder points

**Parameters**:
- `sku` (string): Product SKU
- `annual_demand` (float): Annual demand in units
- `ordering_cost` (float): Cost per order
- `holding_cost_per_unit` (float): Annual holding cost per unit

**Returns**:
```json
{
  "status": "success",
  "sku": "PROD-001",
  "eoq": 1500.0,
  "reorder_point": 1000.0,
  "message": "Optimal order quantity: 1500 units, Reorder at: 1000 units"
}
```

**Example**:
```python
optimize_inventory(
    sku='PROD-001',
    annual_demand=36000,
    ordering_cost=50,
    holding_cost_per_unit=2
)
```

---

### 3. create_purchase_order

**Purpose**: Create purchase orders with suppliers

**Parameters**:
- `sku` (string): Product SKU
- `supplier_id` (string): Supplier ID
- `quantity` (int): Order quantity
- `unit_price` (float): Price per unit
- `delivery_days` (int): Expected delivery days (default: 7)

**Returns**:
```json
{
  "status": "success",
  "po_id": "PO-1703084800.789",
  "sku": "PROD-001",
  "supplier_id": "SUPP-001",
  "quantity": 1500,
  "unit_price": 10.5,
  "total_price": 15750.0,
  "delivery_date": "2025-12-27T10:30:00",
  "message": "Purchase order created: PO-1703084800.789 for 1500 units"
}
```

**Example**:
```python
create_purchase_order(
    sku='PROD-001',
    supplier_id='SUPP-001',
    quantity=1500,
    unit_price=10.50,
    delivery_days=7
)
```

---

### 4. detect_anomalies

**Purpose**: Detect inventory and supply chain anomalies

**Parameters**:
- `sku` (string): Product SKU
- `current_inventory` (float): Current inventory level
- `forecasted_inventory` (float): Forecasted inventory level
- `confidence_80` (float): 80% confidence interval
- `confidence_95` (float): 95% confidence interval

**Returns**:
```json
{
  "status": "success",
  "anomaly_id": "ANM-1703084800.012",
  "sku": "PROD-001",
  "is_anomaly": true,
  "severity": "medium",
  "description": "Inventory below reorder point",
  "message": "Anomaly detection complete for PROD-001: Inventory below reorder point"
}
```

**Example**:
```python
detect_anomalies(
    sku='PROD-001',
    current_inventory=500,
    forecasted_inventory=1000,
    confidence_80=950,
    confidence_95=900
)
```

---

### 5. generate_report

**Purpose**: Generate analytics reports with KPIs

**Parameters**:
- `inventory_data` (list): Inventory records with sku, quantity, value
- `forecast_data` (list): Forecast records with sku, forecasted, actual
- `supplier_data` (list): Supplier records with supplier_id, reliability_score

**Returns**:
```json
{
  "status": "success",
  "report_id": "RPT-1703084800.345",
  "kpis": {
    "inventory_turnover": 2.45,
    "forecast_accuracy": 92.5,
    "supplier_reliability": 95.0
  },
  "report_location": "s3://supply-chain-reports-XXXXX/reports/2025/12/20/report-1703084800.345.json",
  "message": "Report generated: RPT-1703084800.345"
}
```

**Example**:
```python
generate_report(
    inventory_data=[
        {'sku': 'PROD-001', 'quantity': 1000, 'value': 50000}
    ],
    forecast_data=[
        {'sku': 'PROD-001', 'forecasted': 100, 'actual': 95}
    ],
    supplier_data=[
        {'supplier_id': 'SUPP-001', 'reliability_score': 95}
    ]
)
```

---

### 6. get_inventory_status

**Purpose**: Get current inventory status

**Parameters**:
- `sku` (string): Product SKU

**Returns**:
```json
{
  "status": "success",
  "sku": "PROD-001",
  "current_quantity": 500,
  "reorder_point": 300,
  "safety_stock": 200,
  "warehouse": "WH-001",
  "message": "Inventory for PROD-001: 500 units"
}
```

**Example**:
```python
get_inventory_status(sku='PROD-001')
```

---

## Using Tools in Your Own Agent

You can import and use these tools in your own Strands Agent:

```python
from strands import Agent
from strands.models import BedrockModel
from src.agents.agent_tools import (
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status,
)

# Create your agent
model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-20250514-v1:0")

agent = Agent(
    model=model,
    system_prompt="You are a supply chain expert...",
    tools=[
        forecast_demand,
        optimize_inventory,
        create_purchase_order,
        detect_anomalies,
        generate_report,
        get_inventory_status,
    ],
)

# Use the agent
response = agent("Forecast demand for PROD-001")
print(response)
```

## Example Workflows

### Workflow 1: Complete Optimization

```
User: "Optimize supply chain for PROD-001"
↓
Agent calls: forecast_demand()
↓
Agent calls: optimize_inventory()
↓
Agent calls: create_purchase_order()
↓
Agent calls: detect_anomalies()
↓
Agent calls: generate_report()
↓
Result: Complete optimization with recommendations
```

### Workflow 2: Anomaly Response

```
User: "Check PROD-001 for issues"
↓
Agent calls: get_inventory_status()
↓
Agent calls: detect_anomalies()
↓
Agent calls: generate_report()
↓
Result: Issues identified with recommendations
```

### Workflow 3: Demand Planning

```
User: "Plan for next quarter"
↓
Agent calls: forecast_demand()
↓
Agent calls: optimize_inventory()
↓
Agent calls: create_purchase_order()
↓
Result: Purchase orders created based on forecast
```

## Data Storage

All tool calls automatically store data in AWS:

- **DynamoDB**: Forecasts, inventory, purchase orders, anomalies
- **S3**: Reports
- **SNS**: Alerts (if anomalies detected)

## Prerequisites

1. AWS account configured: `aws configure`
2. AWS resources created: `setup_aws_resources.bat` or `./setup_aws_resources.sh`
3. `.env` file configured with AWS credentials
4. Dependencies installed: `pip install -r requirements.txt`

## Running the Orchestrator

### Interactive Mode
```bash
python supply_chain_orchestrator.py
```

### Example Mode
```bash
python supply_chain_orchestrator.py --example
```

## Example Queries

Try these in interactive mode:

1. **Forecast**
   - "Forecast demand for PROD-001 with 12 months of historical data"
   - "What's the expected demand for next 30 days?"

2. **Optimize**
   - "Optimize inventory for PROD-001 with annual demand of 36000"
   - "Calculate the optimal order quantity"

3. **Purchase Orders**
   - "Create a purchase order for 1500 units of PROD-001 from SUPP-001"
   - "Place an order at $10.50 per unit"

4. **Anomalies**
   - "Check for anomalies in PROD-001 inventory"
   - "Is there anything unusual with the current inventory?"

5. **Reports**
   - "Generate a report for all products"
   - "Create an analytics report"

6. **Status**
   - "What's the current inventory for PROD-001?"
   - "Check inventory status"

## Summary

You now have:
✓ 6 agent tools ready to use
✓ Master orchestrator agent
✓ Interactive mode for testing
✓ Example workflows
✓ AWS integration for data storage

**Start with**: `python supply_chain_orchestrator.py`
