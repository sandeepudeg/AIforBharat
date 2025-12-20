# Monitoring and Observability - Quick Start Guide

## Overview

The Supply Chain Optimizer now includes comprehensive monitoring and observability capabilities using AWS CloudWatch, X-Ray, and custom metrics.

## Quick Setup

### 1. Initialize Monitoring on Application Startup

```python
from src.main import initialize_application
from src.observability import setup_monitoring

# Initialize application
clients = initialize_application()

# Setup monitoring (creates dashboards and alarms)
monitoring_results = setup_monitoring()
```

### 2. Track Agent Performance Automatically

```python
from src.observability import track_agent_performance

class MyAgent:
    @track_agent_performance("MyAgent")
    def execute(self):
        # Your agent logic here
        pass
```

### 3. Track Report Generation Performance

```python
from src.observability import track_report_generation

class ReportGenerator:
    @track_report_generation("standard")
    def generate_report(self):
        # Your report generation logic here
        pass
```

### 4. Record Custom Metrics

```python
from src.observability import CloudWatchMetrics

metrics = CloudWatchMetrics()

# Record forecast accuracy
metrics.record_forecast_accuracy(85.5)

# Record supplier performance
metrics.record_supplier_performance("supplier-123", 92.0)

# Record inventory updates
metrics.record_inventory_update_count(50)

# Record anomalies detected
metrics.record_anomaly_detection_count("inventory_deviation", 3)
```

## Key Metrics

| Metric | Unit | Purpose |
|--------|------|---------|
| AgentExecutionTime | Seconds | Track agent performance |
| AgentSuccess | Count | Count successful executions |
| AgentFailure | Count | Count failed executions |
| ReportGenerationTime | Seconds | Track report generation (SLA: 5min standard, 15min comprehensive) |
| ForecastAccuracy | Percent | Track forecast accuracy (Alarm: < 80%) |
| SupplierPerformanceScore | Score | Track supplier performance (Alarm: < 70) |
| InventoryUpdatesCount | Count | Track inventory operations |
| AnomaliesDetected | Count | Track anomaly detection |

## Dashboards

Three dashboards are automatically created:

1. **SupplyChainOptimizer** - Main dashboard with overall system health
2. **AgentMetrics** - Per-agent performance metrics
3. **SLAMetrics** - SLA compliance and performance targets

Access them in AWS CloudWatch Console → Dashboards

## Alarms

Alarms are automatically created for:

- Report Generation SLA violations (5 min for standard, 15 min for comprehensive)
- Agent failures (all agents)
- Agent performance degradation (> 60 seconds)
- Low forecast accuracy (< 80%)
- Supplier performance degradation (< 70)

Alarms send notifications to SNS topic configured in `SNS_TOPIC_ARN_ALERTS`

## Environment Configuration

```bash
# Required for CloudWatch
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Required for alarm notifications
SNS_TOPIC_ARN_ALERTS=arn:aws:sns:us-east-1:123456789:supply-chain-alerts

# Application environment
NODE_ENV=production
```

## Testing

Run monitoring tests:

```bash
# All monitoring tests
pytest tests/test_monitoring_observability.py tests/test_monitoring_setup.py -v

# Specific test class
pytest tests/test_monitoring_observability.py::TestCloudWatchMetrics -v

# Specific test
pytest tests/test_monitoring_observability.py::TestCloudWatchMetrics::test_put_metric_success -v
```

## Common Tasks

### View Metrics in CloudWatch

1. Go to AWS CloudWatch Console
2. Select Metrics
3. Find namespace: `SupplyChainOptimizer`
4. Browse metrics by dimension (AgentName, ReportType, etc.)

### View Dashboards

1. Go to AWS CloudWatch Console
2. Select Dashboards
3. Choose: SupplyChainOptimizer, AgentMetrics, or SLAMetrics

### View Alarms

1. Go to AWS CloudWatch Console
2. Select Alarms
3. Filter by state (OK, ALARM, INSUFFICIENT_DATA)

### Create Custom Alarm

```python
from src.observability import CloudWatchAlarms

alarms = CloudWatchAlarms()

# Create custom alarm
alarms.create_agent_performance_alarm(
    agent_name="MyAgent",
    threshold_seconds=120,
    alarm_name="MyAgentPerformanceAlarm"
)
```

### Delete Dashboards/Alarms

```python
from src.observability import MonitoringSetup

setup = MonitoringSetup()

# Cleanup dashboards
setup.cleanup_dashboards()

# Cleanup alarms
setup.cleanup_alarms()
```

## SLA Compliance

### Report Generation SLA (Requirement 5.4)

- **Standard Reports**: Must complete within 5 minutes (300 seconds)
- **Comprehensive Reports**: Must complete within 15 minutes (900 seconds)

**Monitoring**: 
- Metrics track actual generation time
- Alarms trigger when SLA is violated
- SLA Dashboard shows compliance status

**Example**:
```python
from src.observability import track_report_generation

@track_report_generation("standard")
def generate_standard_report():
    # Must complete within 5 minutes
    pass

@track_report_generation("comprehensive")
def generate_comprehensive_report():
    # Must complete within 15 minutes
    pass
```

## Troubleshooting

### Metrics Not Appearing

1. Check AWS credentials are configured
2. Verify CloudWatch namespace: `SupplyChainOptimizer`
3. Check AWS region is correct
4. Wait a few minutes for metrics to appear

### Alarms Not Triggering

1. Verify SNS topic ARN is correct
2. Check alarm thresholds are appropriate
3. Verify metrics are being recorded
4. Check CloudWatch Alarms history

### Dashboard Not Showing Data

1. Ensure metrics have been recorded
2. Check time range on dashboard
3. Verify metric names and dimensions match
4. Wait for sufficient data points

## Documentation

For detailed documentation, see:
- `src/observability/README.md` - Comprehensive guide
- `MONITORING_IMPLEMENTATION.md` - Implementation details

## Support

For issues or questions:
1. Check the README in `src/observability/`
2. Review test files for usage examples
3. Check CloudWatch Logs for error messages
