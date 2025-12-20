# Monitoring and Observability

This module provides comprehensive monitoring and observability capabilities for the Supply Chain Optimizer system using AWS CloudWatch, X-Ray, and custom metrics.

## Components

### 1. X-Ray Distributed Tracing (`xray.py`)

Provides distributed tracing capabilities for tracking requests across the system.

**Features:**
- Automatic patching of AWS SDK calls
- Service name configuration
- Production/development mode support

**Usage:**
```python
from src.observability import setup_xray_tracing

setup_xray_tracing()
```

### 2. CloudWatch Metrics (`cloudwatch.py`)

Records custom metrics for monitoring system performance and behavior.

**Key Metrics:**
- `AgentExecutionTime` - Time taken by agents to execute
- `AgentSuccess` - Count of successful agent executions
- `AgentFailure` - Count of failed agent executions
- `ReportGenerationTime` - Time taken to generate reports
- `InventoryUpdatesCount` - Number of inventory items updated
- `AnomaliesDetected` - Count of detected anomalies
- `PurchaseOrderCount` - Count of purchase orders by status
- `ForecastAccuracy` - Forecast accuracy percentage
- `SupplierPerformanceScore` - Supplier performance score (0-100)

**Usage:**
```python
from src.observability import CloudWatchMetrics

metrics = CloudWatchMetrics()

# Record agent execution time
metrics.record_agent_execution_time("DemandForecastingAgent", 45.5)

# Record agent success
metrics.record_agent_success("InventoryOptimizerAgent")

# Record report generation time
metrics.record_report_generation_time("standard", 120.5)

# Record forecast accuracy
metrics.record_forecast_accuracy(85.5)
```

**Decorators:**

Track agent performance automatically:
```python
from src.observability import track_agent_performance

@track_agent_performance("MyAgent")
def my_agent_function():
    # Agent logic here
    pass
```

Track report generation performance:
```python
from src.observability import track_report_generation

@track_report_generation("standard")
def generate_report():
    # Report generation logic
    pass
```

### 3. CloudWatch Alarms (`alarms.py`)

Creates and manages CloudWatch alarms for SLA violations and critical events.

**Alarm Types:**

1. **Report Generation SLA Alarms**
   - Standard reports: 5 minutes (300 seconds)
   - Comprehensive reports: 15 minutes (900 seconds)

2. **Agent Failure Alarms**
   - Triggers when an agent fails
   - Supports all agent types

3. **Agent Performance Alarms**
   - Triggers when agent execution time exceeds threshold
   - Default threshold: 60 seconds

4. **Forecast Accuracy Alarms**
   - Triggers when forecast accuracy drops below threshold
   - Default threshold: 80%

5. **Supplier Performance Alarms**
   - Triggers when supplier performance score drops below threshold
   - Default threshold: 70

**Usage:**
```python
from src.observability import CloudWatchAlarms

alarms = CloudWatchAlarms()

# Create report generation SLA alarm
alarms.create_report_generation_sla_alarm(
    alarm_name="StandardReportSLA",
    threshold_seconds=300,
    report_type="standard"
)

# Create agent failure alarm
alarms.create_agent_failure_alarm("DemandForecastingAgent")

# Create agent performance alarm
alarms.create_agent_performance_alarm(
    "InventoryOptimizerAgent",
    threshold_seconds=60
)

# Create forecast accuracy alarm
alarms.create_forecast_accuracy_alarm(threshold_percentage=80)

# Create supplier performance alarm
alarms.create_supplier_performance_alarm(
    "supplier-123",
    threshold_score=70
)

# Delete an alarm
alarms.delete_alarm("StandardReportSLA")

# List all alarms
alarms_list = alarms.list_alarms()
```

### 4. CloudWatch Dashboards (`dashboards.py`)

Creates and manages CloudWatch dashboards for visualization.

**Dashboard Types:**

1. **Main Dashboard** (`SupplyChainOptimizer`)
   - Agent performance metrics
   - Report generation and forecast accuracy
   - Supply chain activity
   - Supplier performance

2. **Agent Dashboard** (`AgentMetrics`)
   - Agent execution times
   - Agent success counts
   - Agent failure counts
   - Per-agent metrics

3. **SLA Dashboard** (`SLAMetrics`)
   - Report generation time (with SLA thresholds)
   - Forecast accuracy
   - Supplier performance score

**Usage:**
```python
from src.observability import CloudWatchDashboards

dashboards = CloudWatchDashboards()

# Create main dashboard
dashboards.create_main_dashboard()

# Create agent dashboard
dashboards.create_agent_dashboard()

# Create SLA dashboard
dashboards.create_sla_dashboard()

# Delete a dashboard
dashboards.delete_dashboard("SupplyChainOptimizer")

# List all dashboards
dashboards_list = dashboards.list_dashboards()
```

### 5. Monitoring Setup (`setup.py`)

Orchestrates the setup of all monitoring and observability components.

**Features:**
- Automatic dashboard creation
- Automatic alarm creation
- Error handling and logging
- Cleanup utilities

**Usage:**
```python
from src.observability import setup_monitoring, MonitoringSetup

# Quick setup
results = setup_monitoring()

# Or use MonitoringSetup class for more control
setup = MonitoringSetup()

# Setup all components
results = setup.setup_all()

# Setup only dashboards
dashboard_results = setup.setup_dashboards()

# Setup only alarms
alarm_results = setup.setup_alarms()

# Cleanup dashboards
setup.cleanup_dashboards()

# Cleanup alarms
setup.cleanup_alarms()
```

## Integration with Application

### Initialization

Add monitoring setup to your application initialization:

```python
from src.main import initialize_application
from src.observability import setup_monitoring

# Initialize application
clients = initialize_application()

# Setup monitoring
monitoring_results = setup_monitoring()
```

### Using Decorators

Apply decorators to agent functions:

```python
from src.observability import track_agent_performance, track_report_generation

class DemandForecastingAgent:
    @track_agent_performance("DemandForecastingAgent")
    def forecast_demand(self, product_id):
        # Forecasting logic
        pass

class ReportGenerationAgent:
    @track_report_generation("standard")
    def generate_report(self, period):
        # Report generation logic
        pass
```

### Recording Metrics

Record metrics at key points in your code:

```python
from src.observability import CloudWatchMetrics

metrics = CloudWatchMetrics()

# After inventory update
metrics.record_inventory_update_count(50)

# After anomaly detection
metrics.record_anomaly_detection_count("inventory_deviation", 3)

# After forecast generation
metrics.record_forecast_accuracy(85.5)
```

## Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# SNS Configuration (for alarm notifications)
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:123456789:supply-chain-alerts

# Application Environment
NODE_ENV=production  # or development
```

### CloudWatch Namespace

All metrics are recorded under the namespace: `SupplyChainOptimizer`

## SLA Compliance

### Report Generation SLA

- **Standard Reports**: Must complete within 5 minutes (300 seconds)
- **Comprehensive Reports**: Must complete within 15 minutes (900 seconds)

Alarms are automatically created to alert when these SLAs are violated.

### Agent Performance SLA

- **Default Threshold**: 60 seconds per execution
- **Evaluation Period**: 2 consecutive 5-minute periods

Alarms trigger when average execution time exceeds threshold.

## Metrics Retention

CloudWatch metrics are retained according to AWS default policies:
- 1-minute granularity: 15 days
- 5-minute granularity: 63 days
- 1-hour granularity: 455 days

For long-term retention, consider exporting metrics to S3 or using CloudWatch Logs Insights.

## Testing

Run the monitoring tests:

```bash
# Test CloudWatch metrics
pytest tests/test_monitoring_observability.py::TestCloudWatchMetrics -v

# Test alarms
pytest tests/test_monitoring_observability.py::TestCloudWatchAlarms -v

# Test dashboards
pytest tests/test_monitoring_observability.py::TestCloudWatchDashboards -v

# Test setup
pytest tests/test_monitoring_setup.py -v

# Run all monitoring tests
pytest tests/test_monitoring*.py -v
```

## Best Practices

1. **Use Decorators**: Apply `@track_agent_performance` and `@track_report_generation` decorators to automatically track execution times.

2. **Record Metrics at Key Points**: Record metrics after significant operations (inventory updates, anomaly detection, etc.).

3. **Monitor SLAs**: Regularly check SLA dashboards to ensure compliance with performance targets.

4. **Set Appropriate Thresholds**: Adjust alarm thresholds based on your system's baseline performance.

5. **Use Dimensions**: Include relevant dimensions (agent name, report type, etc.) when recording metrics for better filtering and analysis.

6. **Clean Up Resources**: Use cleanup methods to remove dashboards and alarms when they're no longer needed.

## Troubleshooting

### Metrics Not Appearing

1. Verify AWS credentials are configured correctly
2. Check that the CloudWatch namespace is correct: `SupplyChainOptimizer`
3. Ensure the AWS region is correct
4. Check CloudWatch Logs for any error messages

### Alarms Not Triggering

1. Verify SNS topic ARN is configured correctly
2. Check that alarm thresholds are appropriate for your system
3. Verify that metrics are being recorded with correct dimensions
4. Check CloudWatch Alarms history for alarm state changes

### Dashboard Not Displaying Data

1. Ensure metrics have been recorded (check CloudWatch Metrics page)
2. Verify dashboard is looking at correct time range
3. Check that metric names and dimensions match exactly
4. Ensure sufficient data points have been collected

## References

- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS X-Ray Documentation](https://docs.aws.amazon.com/xray/)
- [CloudWatch Metrics Best Practices](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Best_Practice_Recommended_Alarms_AWS_Services.html)
