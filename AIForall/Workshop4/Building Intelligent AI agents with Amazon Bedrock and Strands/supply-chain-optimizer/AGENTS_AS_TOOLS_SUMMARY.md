# Agents as Tools - Complete Summary

## What Changed

Your supply chain agents are now **tools** that can be called by a Strands Agent orchestrator, instead of standalone scripts.

## Files Created

### 1. `src/agents/agent_tools.py`
Wraps all agents as Strands tools:
- `@tool forecast_demand()` - Generate demand forecasts
- `@tool optimize_inventory()` - Calculate optimal quantities
- `@tool create_purchase_order()` - Place orders
- `@tool detect_anomalies()` - Identify issues
- `@tool generate_report()` - Create analytics
- `@tool get_inventory_status()` - Check inventory

### 2. `supply_chain_orchestrator.py`
Master Strands Agent that:
- Uses all 6 tools
- Runs in interactive mode
- Includes example workflows
- Automatically calls appropriate tools based on user queries

### 3. `AGENTS_AS_TOOLS.md`
Complete documentation with:
- Tool definitions
- Parameter descriptions
- Return value examples
- Usage examples
- Example workflows

### 4. `AGENTS_AS_TOOLS_QUICK_START.txt`
Quick reference with:
- How to run
- Available tools
- Example queries
- Troubleshooting

## How It Works

```
User Query
    ↓
Strands Agent (supply_chain_orchestrator.py)
    ↓
Agent analyzes query and decides which tools to use
    ↓
Agent calls tools (forecast_demand, optimize_inventory, etc.)
    ↓
Tools execute and store data in AWS
    ↓
Agent returns results to user
```

## Running the Orchestrator

### Interactive Mode
```bash
python supply_chain_orchestrator.py
```

Ask questions like:
- "Forecast demand for PROD-001"
- "Optimize inventory for PROD-001"
- "Create a purchase order for 1500 units"
- "Check for anomalies"
- "Generate a report"

### Example Mode
```bash
python supply_chain_orchestrator.py --example
```

Runs a complete example showing all tools in action.

## The 6 Tools

### 1. forecast_demand
**Input**: SKU, sales history, forecast days
**Output**: Forecast with confidence intervals
**Storage**: DynamoDB (forecasts table)

### 2. optimize_inventory
**Input**: SKU, annual demand, costs
**Output**: EOQ, reorder point
**Storage**: None (returns calculations)

### 3. create_purchase_order
**Input**: SKU, supplier, quantity, price
**Output**: Purchase order details
**Storage**: DynamoDB (purchase_orders table)

### 4. detect_anomalies
**Input**: SKU, inventory levels, confidence intervals
**Output**: Anomaly detection results
**Storage**: DynamoDB (anomalies table) + SNS (alerts)

### 5. generate_report
**Input**: Inventory, forecast, supplier data
**Output**: Report with KPIs
**Storage**: S3 (reports bucket)

### 6. get_inventory_status
**Input**: SKU
**Output**: Current inventory details
**Storage**: Reads from DynamoDB

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

## Using Tools in Your Own Agent

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

## Prerequisites

1. **AWS Account** - Create at https://aws.amazon.com
2. **AWS CLI** - Install and configure: `aws configure`
3. **AWS Resources** - Create with: `setup_aws_resources.bat` or `./setup_aws_resources.sh`
4. **Environment** - Create `.env` file with AWS credentials
5. **Dependencies** - Install with: `pip install -r requirements.txt`

## Quick Start (5 minutes)

1. **Configure AWS**
   ```bash
   aws configure
   ```

2. **Create Resources**
   ```bash
   # Windows
   setup_aws_resources.bat
   
   # macOS/Linux
   chmod +x setup_aws_resources.sh
   ./setup_aws_resources.sh
   ```

3. **Create .env File**
   ```bash
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   S3_BUCKET_NAME=supply-chain-reports-XXXXX
   SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
   LOG_LEVEL=INFO
   NODE_ENV=production
   ```

4. **Run Orchestrator**
   ```bash
   python supply_chain_orchestrator.py
   ```

## Example Queries

Try these in interactive mode:

**Forecasting**
- "Forecast demand for PROD-001 using last 12 months of data"
- "What's the expected demand for next 30 days?"

**Optimization**
- "Optimize inventory for PROD-001 with annual demand of 36000"
- "Calculate the optimal order quantity"

**Purchase Orders**
- "Create a purchase order for 1500 units of PROD-001 from SUPP-001"
- "Place an order at $10.50 per unit"

**Anomalies**
- "Check for anomalies in PROD-001 inventory"
- "Is there anything unusual with the current inventory?"

**Reports**
- "Generate a report for all products"
- "Create an analytics report"

**Status**
- "What's the current inventory for PROD-001?"
- "Check inventory status"

## Data Storage

All tool calls automatically store data in AWS:

| Tool | Storage | Location |
|------|---------|----------|
| forecast_demand | DynamoDB | forecasts table |
| optimize_inventory | None | Returns calculations |
| create_purchase_order | DynamoDB | purchase_orders table |
| detect_anomalies | DynamoDB + SNS | anomalies table + alerts |
| generate_report | S3 | reports/YYYY/MM/DD/ |
| get_inventory_status | DynamoDB | Reads from inventory table |

## Comparison: Before vs After

### Before (Standalone Scripts)
```bash
python run_with_aws_services.py
# Creates dummy data and runs workflow
```

### After (Tools for Agent)
```bash
python supply_chain_orchestrator.py
# Interactive agent that calls tools based on user queries
```

## Benefits of Tools Approach

✓ **Flexible** - Agent decides which tools to use
✓ **Intelligent** - Agent can combine multiple tools
✓ **Interactive** - Ask questions in natural language
✓ **Scalable** - Easy to add more tools
✓ **Reusable** - Tools can be used in any agent
✓ **Maintainable** - Clear separation of concerns

## Troubleshooting

### Error: "Unable to locate credentials"
```bash
aws configure
```

### Error: "ResourceNotFoundException"
```bash
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux
```

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "No module named 'strands'"
```bash
pip install strands-agents
```

## Summary

You now have:

✓ **6 Agent Tools** - Ready to use in any Strands Agent
✓ **Master Orchestrator** - Interactive agent using all tools
✓ **AWS Integration** - Automatic data storage
✓ **Example Workflows** - Complete examples included
✓ **Documentation** - Complete guides and examples

**Start with**: `python supply_chain_orchestrator.py`

Then ask questions and watch the agent use the right tools!

---

**Next Steps**:
1. Run `python supply_chain_orchestrator.py`
2. Ask questions like "Forecast demand for PROD-001"
3. Watch the agent call the appropriate tools
4. Check AWS Console to see stored data
5. Integrate tools into your own agents
