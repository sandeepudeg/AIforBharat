# Supply Chain Agents as Tools - Updated Documentation

## Overview

All supply chain agents have been converted to Strands tools that read from and write to DynamoDB. This allows the orchestrator agent to use them intelligently based on user queries.

## Updated Tool Signatures

### 1. forecast_demand

**Purpose**: Generate demand forecast for a product using sales history from DynamoDB.

**Signature**:
```python
forecast_demand(sku: str, forecast_days: int = 30) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str): Product SKU (e.g., 'PROD-001')
- `forecast_days` (int, optional): Number of days to forecast (default: 30)

**Returns**:
```json
{
  "status": "success",
  "forecast_id": "FCST-1234567890.123",
  "sku": "PROD-001",
  "forecasted_demand": 1000,
  "confidence_80": 950,
  "confidence_95": 900,
  "message": "Forecast generated for PROD-001: 1000 units"
}
```

**Data Source**: Reads from DynamoDB `sales_history` table
**Data Saved**: Saves forecast to DynamoDB `forecasts` table

**Example**:
```python
result = forecast_demand(sku='PROD-001', forecast_days=30)
```

---

### 2. optimize_inventory

**Purpose**: Optimize inventory levels for a product using data from DynamoDB.

**Signature**:
```python
optimize_inventory(sku: str) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str): Product SKU

**Returns**:
```json
{
  "status": "success",
  "sku": "PROD-001",
  "eoq": 500.0,
  "reorder_point": 200.0,
  "annual_demand": 6000.0,
  "current_inventory": 1500,
  "ordering_cost": 50,
  "holding_cost_per_unit": 2,
  "message": "Optimal order quantity: 500 units, Reorder at: 200 units"
}
```

**Data Source**: Reads from DynamoDB `inventory` and `sales_history` tables
**Calculation**: 
- Annual demand calculated from sales history
- EOQ (Economic Order Quantity) calculated using Wilson's formula
- Reorder point calculated based on lead time and safety stock

**Example**:
```python
result = optimize_inventory(sku='PROD-001')
```

---

### 3. create_purchase_order

**Purpose**: Create a purchase order with a supplier using data from DynamoDB.

**Signature**:
```python
create_purchase_order(
    sku: str,
    supplier_id: str,
    quantity: int,
    delivery_days: int = 7
) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str): Product SKU
- `supplier_id` (str): Supplier ID
- `quantity` (int): Order quantity
- `delivery_days` (int, optional): Expected delivery in days (default: 7)

**Returns**:
```json
{
  "status": "success",
  "po_id": "PO-1234567890.123",
  "sku": "PROD-001",
  "supplier_id": "SUPP-001",
  "supplier_name": "Supplier Name",
  "quantity": 1500,
  "unit_price": 10.50,
  "total_price": 15750.0,
  "delivery_date": "2025-12-27T10:30:00.123456",
  "message": "Purchase order created: PO-1234567890.123 for 1500 units"
}
```

**Data Source**: Reads from DynamoDB `suppliers` table
**Data Saved**: Saves purchase order to DynamoDB `purchase_orders` table

**Example**:
```python
result = create_purchase_order(
    sku='PROD-001',
    supplier_id='SUPP-001',
    quantity=1500,
    delivery_days=7
)
```

---

### 4. detect_anomalies

**Purpose**: Detect anomalies in inventory or supply chain using data from DynamoDB.

**Signature**:
```python
detect_anomalies(sku: str) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str): Product SKU

**Returns**:
```json
{
  "status": "success",
  "anomaly_id": "ANM-1234567890.123",
  "sku": "PROD-001",
  "is_anomaly": false,
  "severity": "low",
  "description": "No anomaly detected",
  "message": "Anomaly detection complete for PROD-001: No anomaly"
}
```

**Data Source**: Reads from DynamoDB `inventory` and `forecasts` tables
**Data Saved**: Saves anomaly detection result to DynamoDB `anomalies` table
**Notifications**: Sends SNS alert if anomaly detected (if SNS topic configured)

**Example**:
```python
result = detect_anomalies(sku='PROD-001')
```

---

### 5. generate_report

**Purpose**: Generate analytics report with KPIs using data from DynamoDB.

**Signature**:
```python
generate_report(sku: Optional[str] = None) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str, optional): Product SKU. If provided, generates report for that product. If not provided, generates report for all products.

**Returns**:
```json
{
  "status": "success",
  "report_id": "RPT-1234567890.123",
  "kpis": {
    "inventory_turnover": 4.5,
    "forecast_accuracy": 0.92,
    "supplier_reliability": 0.98
  },
  "inventory_turnover": 4.5,
  "forecast_accuracy": 0.92,
  "supplier_reliability": 0.98,
  "report_location": "s3://bucket-name/reports/2025/12/20/report-1234567890.123.json",
  "message": "Report generated: RPT-1234567890.123"
}
```

**Data Source**: Reads from DynamoDB `inventory`, `forecasts`, and `suppliers` tables
**Data Saved**: Saves report to S3 bucket

**Example**:
```python
# Report for specific product
result = generate_report(sku='PROD-001')

# Report for all products
result = generate_report()
```

---

### 6. get_inventory_status

**Purpose**: Get current inventory status for a product.

**Signature**:
```python
get_inventory_status(sku: str) -> Dict[str, Any]
```

**Parameters**:
- `sku` (str): Product SKU

**Returns**:
```json
{
  "status": "success",
  "sku": "PROD-001",
  "current_quantity": 1500,
  "reorder_point": 200,
  "safety_stock": 300,
  "warehouse": "WH-001",
  "message": "Inventory for PROD-001: 1500 units"
}
```

**Data Source**: Reads from DynamoDB `inventory` table

**Example**:
```python
result = get_inventory_status(sku='PROD-001')
```

---

## DynamoDB Tables Required

The tools expect the following DynamoDB tables to exist:

### 1. inventory
- **Primary Key**: `sku` (String)
- **Attributes**:
  - `sku`: Product SKU
  - `current_quantity`: Current inventory level
  - `reorder_point`: Reorder point
  - `safety_stock`: Safety stock level
  - `warehouse`: Warehouse location
  - `lead_time_days`: Lead time from supplier
  - `ordering_cost`: Cost per order
  - `holding_cost_per_unit`: Cost to hold one unit per year

### 2. sales_history
- **Primary Key**: `sku` (String), `date` (String)
- **Attributes**:
  - `sku`: Product SKU
  - `date`: Date of sale
  - `quantity`: Quantity sold
  - `revenue`: Revenue from sale

### 3. suppliers
- **Primary Key**: `supplier_id` (String)
- **Attributes**:
  - `supplier_id`: Supplier ID
  - `name`: Supplier name
  - `unit_price`: Unit price for products
  - `reliability_score`: Supplier reliability (0-1)
  - `lead_time_days`: Average lead time

### 4. forecasts
- **Primary Key**: `forecast_id` (String)
- **Attributes**:
  - `forecast_id`: Unique forecast ID
  - `sku`: Product SKU
  - `forecasted_demand`: Forecasted demand
  - `confidence_80`: 80% confidence interval
  - `confidence_95`: 95% confidence interval
  - `forecast_date`: When forecast was generated
  - `forecast_period_days`: Forecast period

### 5. purchase_orders
- **Primary Key**: `po_id` (String)
- **Attributes**:
  - `po_id`: Purchase order ID
  - `sku`: Product SKU
  - `supplier_id`: Supplier ID
  - `quantity`: Order quantity
  - `unit_price`: Unit price
  - `total_price`: Total order price
  - `delivery_date`: Expected delivery date
  - `status`: Order status (pending, confirmed, delivered)
  - `created_date`: When PO was created

### 6. anomalies
- **Primary Key**: `anomaly_id` (String)
- **Attributes**:
  - `anomaly_id`: Unique anomaly ID
  - `sku`: Product SKU
  - `type`: Anomaly type
  - `is_anomaly`: Whether anomaly detected
  - `severity`: Severity level (low, medium, high)
  - `description`: Anomaly description
  - `detected_date`: When anomaly was detected

---

## Error Handling

All tools have built-in error handling:

- **Missing Data**: If required data is not found in DynamoDB, tools return default values or skip that operation
- **DynamoDB Errors**: Connection errors are logged as warnings, not errors
- **AWS Service Errors**: S3 and SNS errors are handled gracefully

**Example Response on Error**:
```json
{
  "status": "error",
  "message": "Error description"
}
```

---

## Usage with Orchestrator Agent

The tools are designed to be used with the Strands orchestrator agent:

```python
from supply_chain_orchestrator import create_orchestrator_agent

agent = create_orchestrator_agent()

# Ask the agent to perform supply chain operations
response = agent("Forecast demand for PROD-001 for the next 30 days")
response = agent("Optimize inventory for PROD-001")
response = agent("Create a purchase order for 1500 units of PROD-001 from SUPP-001")
response = agent("Check for anomalies in PROD-001")
response = agent("Generate a report for all products")
```

---

## Testing

Run the standalone test script to verify all tools work:

```bash
python test_agent_tools_standalone.py
```

This will test all 6 tools and report results.

---

## Configuration

Tools use configuration from environment variables:

- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `DYNAMODB_REGION`: DynamoDB region (default: us-east-1)
- `DYNAMODB_ENDPOINT`: DynamoDB endpoint (for local testing)
- `S3_BUCKET_NAME`: S3 bucket for reports
- `SNS_TOPIC_ARN_ALERTS`: SNS topic for alerts

---

## Key Changes from Previous Version

1. **Simplified Signatures**: Tools no longer require all data as parameters
2. **DynamoDB Integration**: All data is read from and written to DynamoDB
3. **Graceful Degradation**: Tools work even if some data is missing
4. **Better Error Handling**: Warnings instead of errors for missing data
5. **AWS Service Integration**: Reports saved to S3, alerts sent via SNS
