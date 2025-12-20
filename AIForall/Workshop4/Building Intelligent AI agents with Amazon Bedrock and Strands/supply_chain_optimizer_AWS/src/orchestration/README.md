# Event-Driven Orchestration Module

## Overview

The orchestration module implements event-driven workflows for the Supply Chain Optimizer using AWS EventBridge and Lambda. It coordinates the execution of multiple agents based on scheduled events and real-time inventory updates.

## Components

### 1. Orchestrator (`orchestrator.py`)

The `Orchestrator` class manages EventBridge rules and Lambda targets.

**Key Methods:**

- `setup_inventory_update_rule()` - Creates EventBridge rule for real-time inventory updates
- `setup_scheduled_forecasting_job()` - Creates daily forecasting job (2 AM UTC)
- `setup_scheduled_optimization_job()` - Creates daily optimization job (3 AM UTC)
- `setup_scheduled_anomaly_detection_job()` - Creates hourly anomaly detection job
- `setup_scheduled_report_generation_job()` - Creates weekly report generation job (Monday 4 AM UTC)
- `add_lambda_target()` - Adds Lambda function as target for a rule
- `trigger_agent_workflow()` - Manually triggers an agent workflow
- `list_rules()` - Lists all EventBridge rules
- `delete_rule()` - Deletes an EventBridge rule
- `enable_rule()` / `disable_rule()` - Controls rule state

**Example Usage:**

```python
from src.orchestration.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Set up forecasting rule
rule_arn = orchestrator.setup_scheduled_forecasting_job()

# Add Lambda target
orchestrator.add_lambda_target(
    "daily-forecasting-job",
    "arn:aws:lambda:us-east-1:123456789:function:forecasting-handler"
)

# Trigger workflow manually
event_id = orchestrator.trigger_agent_workflow(
    "forecasting",
    {"sku": "SKU-001"}
)
```

### 2. Event Handler (`event_handler.py`)

The `EventHandler` class processes EventBridge events and orchestrates agent execution.

**Key Methods:**

- `handle_inventory_update_event()` - Processes inventory update events
- `handle_forecasting_job_event()` - Processes scheduled forecasting jobs
- `handle_optimization_job_event()` - Processes scheduled optimization jobs
- `handle_anomaly_detection_job_event()` - Processes scheduled anomaly detection jobs
- `handle_report_generation_job_event()` - Processes scheduled report generation jobs
- `handle_event()` - Routes events to appropriate handlers

**Event Flow:**

```
EventBridge Event
    ↓
EventHandler.handle_event()
    ↓
Route to specific handler based on detail-type
    ↓
Execute agent workflows
    ↓
Return results
```

### 3. Lambda Handlers (`lambda_handlers.py`)

Lambda handler functions that serve as entry points for EventBridge events.

**Available Handlers:**

- `lambda_handler()` - Main handler for all EventBridge events
- `forecasting_handler()` - Dedicated handler for forecasting jobs
- `optimization_handler()` - Dedicated handler for optimization jobs
- `anomaly_detection_handler()` - Dedicated handler for anomaly detection jobs
- `report_generation_handler()` - Dedicated handler for report generation jobs
- `inventory_update_handler()` - Dedicated handler for inventory updates

### 4. Setup Module (`setup.py`)

The `EventDrivenSetup` class initializes all EventBridge rules and Lambda targets.

**Key Methods:**

- `setup_all_rules()` - Sets up all EventBridge rules and Lambda targets
- `cleanup_all_rules()` - Removes all EventBridge rules

**Example Usage:**

```python
from src.orchestration.setup import EventDrivenSetup

setup = EventDrivenSetup()

# Set up all rules
result = setup.setup_all_rules(
    lambda_arns={
        "forecasting": "arn:aws:lambda:us-east-1:123456789:function:forecasting",
        "optimization": "arn:aws:lambda:us-east-1:123456789:function:optimization",
        "anomaly_detection": "arn:aws:lambda:us-east-1:123456789:function:anomaly",
        "report_generation": "arn:aws:lambda:us-east-1:123456789:function:report",
        "inventory_update": "arn:aws:lambda:us-east-1:123456789:function:inventory"
    }
)

# Clean up rules
cleanup_result = setup.cleanup_all_rules()
```

## Event Patterns

### Inventory Update Event

```json
{
  "source": "supply-chain.inventory",
  "detail-type": "Inventory Update",
  "detail": {
    "event_type": "inventory_changed",
    "sku": "SKU-001",
    "warehouse_id": "WH-001",
    "quantity_change": 100
  }
}
```

### Scheduled Job Events

EventBridge automatically sends scheduled events with minimal payload. The handler extracts the job type from the rule name.

## Workflow Execution

### Daily Forecasting Workflow

**Schedule:** 2 AM UTC daily

**Steps:**
1. EventBridge triggers forecasting Lambda
2. Lambda invokes EventHandler
3. EventHandler retrieves all SKUs
4. For each SKU:
   - DemandForecastingAgent generates forecast
   - Forecast stored in DynamoDB
5. Results returned to EventBridge

### Daily Optimization Workflow

**Schedule:** 3 AM UTC daily

**Steps:**
1. EventBridge triggers optimization Lambda
2. Lambda invokes EventHandler
3. EventHandler retrieves all SKUs
4. For each SKU:
   - InventoryOptimizerAgent calculates EOQ and reorder points
   - Results stored in database
5. Results returned to EventBridge

### Hourly Anomaly Detection Workflow

**Schedule:** Every hour

**Steps:**
1. EventBridge triggers anomaly detection Lambda
2. Lambda invokes EventHandler
3. EventHandler retrieves all SKUs
4. For each SKU:
   - AnomalyDetectionAgent detects anomalies
   - Anomalies stored in DynamoDB
5. Results returned to EventBridge

### Weekly Report Generation Workflow

**Schedule:** Monday 4 AM UTC

**Steps:**
1. EventBridge triggers report generation Lambda
2. Lambda invokes EventHandler
3. ReportGenerationAgent generates comprehensive report
4. Report stored in S3
5. Results returned to EventBridge

### Real-Time Inventory Update Workflow

**Trigger:** Inventory update event

**Steps:**
1. Inventory update event sent to EventBridge
2. EventBridge triggers inventory update Lambda
3. Lambda invokes EventHandler
4. EventHandler executes:
   - DemandForecastingAgent.generate_forecast()
   - InventoryOptimizerAgent.optimize_inventory()
   - AnomalyDetectionAgent.detect_anomalies()
5. Results aggregated and returned

## Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>

# Lambda Configuration
LAMBDA_ROLE_ARN=arn:aws:iam::123456789:role/lambda-execution-role

# EventBridge Configuration
EVENTBRIDGE_RULE_NAME=supply-chain-events
```

### Schedule Expressions

The module uses AWS EventBridge cron expressions:

- **Daily Forecasting:** `cron(0 2 * * ? *)` - 2 AM UTC every day
- **Daily Optimization:** `cron(0 3 * * ? *)` - 3 AM UTC every day
- **Hourly Anomaly Detection:** `cron(0 * * * ? *)` - Every hour
- **Weekly Report Generation:** `cron(0 4 ? * MON *)` - Monday 4 AM UTC

## Error Handling

All handlers implement comprehensive error handling:

1. **Try-Catch Blocks:** All operations wrapped in try-catch
2. **Logging:** Errors logged with context
3. **Graceful Degradation:** Partial failures don't stop entire workflow
4. **Response Format:** Consistent error response format

**Error Response Example:**

```json
{
  "statusCode": 500,
  "body": {
    "status": "error",
    "error": "Failed to generate forecast: insufficient data"
  }
}
```

## Testing

The module includes comprehensive unit tests in `tests/test_orchestration.py`:

- **Orchestrator Tests:** 11 tests covering all rule setup and management operations
- **EventHandler Tests:** 7 tests covering event routing and handler execution
- **Setup Tests:** 2 tests covering initialization and cleanup

**Run Tests:**

```bash
pytest tests/test_orchestration.py -v
```

## Integration with Agents

The orchestration module integrates with all supply chain agents:

1. **DemandForecastingAgent** - Generates demand forecasts
2. **InventoryOptimizerAgent** - Calculates optimal inventory levels
3. **SupplierCoordinationAgent** - Manages supplier orders
4. **AnomalyDetectionAgent** - Detects supply chain anomalies
5. **ReportGenerationAgent** - Creates analytics reports
6. **WarehouseManager** - Manages multi-warehouse operations

## Deployment

### Lambda Function Deployment

1. Package orchestration module with dependencies
2. Create Lambda functions for each handler
3. Set appropriate timeout (300 seconds recommended)
4. Configure IAM role with EventBridge permissions
5. Deploy Lambda functions to AWS

### EventBridge Rule Deployment

1. Use `EventDrivenSetup.setup_all_rules()` to create rules
2. Verify rules are enabled in EventBridge console
3. Monitor rule execution in CloudWatch Logs

## Monitoring

### CloudWatch Metrics

- Rule invocation count
- Lambda execution duration
- Lambda error rate
- Failed event count

### CloudWatch Logs

- Event handler logs
- Agent execution logs
- Error traces

### X-Ray Tracing

- Distributed tracing of event flow
- Service map visualization
- Performance analysis

## Best Practices

1. **Idempotency:** Handlers should be idempotent (safe to retry)
2. **Timeouts:** Set appropriate Lambda timeouts for long-running operations
3. **Monitoring:** Enable CloudWatch monitoring for all rules
4. **Error Handling:** Implement comprehensive error handling
5. **Logging:** Log all significant events for debugging
6. **Testing:** Test handlers with various event payloads
7. **Documentation:** Keep documentation updated with changes

## Troubleshooting

### Rule Not Triggering

1. Verify rule is enabled: `orchestrator.list_rules()`
2. Check EventBridge console for rule status
3. Verify Lambda function ARN is correct
4. Check Lambda execution role permissions

### Lambda Execution Failures

1. Check CloudWatch Logs for error messages
2. Verify Lambda function code is correct
3. Check Lambda timeout settings
4. Verify IAM role has required permissions

### Event Not Processed

1. Verify event matches rule pattern
2. Check EventBridge rule event pattern
3. Verify Lambda target is configured
4. Check Lambda function logs

## Future Enhancements

1. **Dead Letter Queues:** Implement DLQ for failed events
2. **Retry Policies:** Add exponential backoff retry logic
3. **Event Filtering:** Add more granular event filtering
4. **Custom Metrics:** Implement custom CloudWatch metrics
5. **Alerting:** Add SNS alerts for critical failures
