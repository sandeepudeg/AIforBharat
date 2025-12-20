"""Tests for monitoring and observability functionality."""

import time
from unittest.mock import MagicMock, patch, call
import pytest

from src.observability.cloudwatch import (
    CloudWatchMetrics,
    track_agent_performance,
    track_report_generation,
)
from src.observability.alarms import CloudWatchAlarms
from src.observability.dashboards import CloudWatchDashboards


class TestCloudWatchMetrics:
    """Tests for CloudWatchMetrics class."""

    @patch("src.observability.cloudwatch.boto3.client")
    def test_put_metric_success(self, mock_boto3_client):
        """Test successful metric recording."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.put_metric("TestMetric", 42.0, unit="Count")

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["Namespace"] == "SupplyChainOptimizer"
        assert call_args[1]["MetricData"][0]["MetricName"] == "TestMetric"
        assert call_args[1]["MetricData"][0]["Value"] == 42.0

    @patch("src.observability.cloudwatch.boto3.client")
    def test_put_metric_with_dimensions(self, mock_boto3_client):
        """Test metric recording with dimensions."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.put_metric(
            "AgentMetric",
            100.0,
            unit="Seconds",
            dimensions={"AgentName": "TestAgent"},
        )

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert dimensions[0]["Name"] == "AgentName"
        assert dimensions[0]["Value"] == "TestAgent"

    @patch("src.observability.cloudwatch.boto3.client")
    def test_put_metric_with_multiple_dimensions(self, mock_boto3_client):
        """Test metric recording with multiple dimensions."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.put_metric(
            "ComplexMetric",
            50.0,
            unit="Count",
            dimensions={"AgentName": "TestAgent", "Status": "Success"},
        )

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert len(dimensions) == 2

    @patch("src.observability.cloudwatch.boto3.client")
    def test_put_metric_error_handling(self, mock_boto3_client):
        """Test error handling when metric recording fails."""
        mock_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {"Error": {"Code": "InvalidParameterValue", "Message": "Test error"}}
        mock_client.put_metric_data.side_effect = ClientError(error_response, "PutMetricData")
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        # Should not raise exception, just log error
        metrics.put_metric("TestMetric", 42.0)

        mock_client.put_metric_data.assert_called_once()

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_agent_execution_time(self, mock_boto3_client):
        """Test recording agent execution time."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_agent_execution_time("DemandForecastingAgent", 45.5)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "AgentExecutionTime"
        assert call_args[1]["MetricData"][0]["Value"] == 45.5
        assert call_args[1]["MetricData"][0]["Unit"] == "Seconds"

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_agent_execution_time_with_dimension(self, mock_boto3_client):
        """Test agent execution time includes agent name dimension."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_agent_execution_time("InventoryOptimizerAgent", 30.0)

        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert any(d["Name"] == "AgentName" and d["Value"] == "InventoryOptimizerAgent" for d in dimensions)

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_agent_success(self, mock_boto3_client):
        """Test recording agent success."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_agent_success("InventoryOptimizerAgent")

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "AgentSuccess"
        assert call_args[1]["MetricData"][0]["Value"] == 1

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_agent_failure(self, mock_boto3_client):
        """Test recording agent failure."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_agent_failure("SupplierCoordinationAgent")

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "AgentFailure"
        assert call_args[1]["MetricData"][0]["Value"] == 1

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_report_generation_time(self, mock_boto3_client):
        """Test recording report generation time."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_report_generation_time("standard", 120.5)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "ReportGenerationTime"
        assert call_args[1]["MetricData"][0]["Value"] == 120.5

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_report_generation_time_comprehensive(self, mock_boto3_client):
        """Test recording comprehensive report generation time."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_report_generation_time("comprehensive", 600.0)

        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert any(d["Name"] == "ReportType" and d["Value"] == "comprehensive" for d in dimensions)

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_inventory_update_count(self, mock_boto3_client):
        """Test recording inventory update count."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_inventory_update_count(50)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "InventoryUpdatesCount"
        assert call_args[1]["MetricData"][0]["Value"] == 50

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_anomaly_detection_count(self, mock_boto3_client):
        """Test recording anomaly detection count."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_anomaly_detection_count("inventory_deviation", 3)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "AnomaliesDetected"
        assert call_args[1]["MetricData"][0]["Value"] == 3

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_anomaly_detection_count_with_type(self, mock_boto3_client):
        """Test anomaly detection count includes anomaly type dimension."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_anomaly_detection_count("supplier_delay", 2)

        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert any(d["Name"] == "AnomalyType" and d["Value"] == "supplier_delay" for d in dimensions)

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_purchase_order_count(self, mock_boto3_client):
        """Test recording purchase order count."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_purchase_order_count("pending", 10)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "PurchaseOrderCount"
        assert call_args[1]["MetricData"][0]["Value"] == 10

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_purchase_order_count_by_status(self, mock_boto3_client):
        """Test purchase order count includes status dimension."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_purchase_order_count("delivered", 25)

        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert any(d["Name"] == "Status" and d["Value"] == "delivered" for d in dimensions)

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_forecast_accuracy(self, mock_boto3_client):
        """Test recording forecast accuracy."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_forecast_accuracy(85.5)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "ForecastAccuracy"
        assert call_args[1]["MetricData"][0]["Value"] == 85.5
        assert call_args[1]["MetricData"][0]["Unit"] == "Percent"

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_supplier_performance(self, mock_boto3_client):
        """Test recording supplier performance."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_supplier_performance("supplier-123", 92.0)

        mock_client.put_metric_data.assert_called_once()
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]["MetricData"][0]["MetricName"] == "SupplierPerformanceScore"
        assert call_args[1]["MetricData"][0]["Value"] == 92.0

    @patch("src.observability.cloudwatch.boto3.client")
    def test_record_supplier_performance_with_id(self, mock_boto3_client):
        """Test supplier performance includes supplier ID dimension."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_supplier_performance("supplier-456", 78.5)

        call_args = mock_client.put_metric_data.call_args
        dimensions = call_args[1]["MetricData"][0]["Dimensions"]
        assert any(d["Name"] == "SupplierId" and d["Value"] == "supplier-456" for d in dimensions)


class TestTrackAgentPerformanceDecorator:
    """Tests for track_agent_performance decorator."""

    @patch("src.observability.cloudwatch.CloudWatchMetrics")
    def test_decorator_records_success(self, mock_metrics_class):
        """Test decorator records successful execution."""
        mock_metrics = MagicMock()
        mock_metrics_class.return_value = mock_metrics

        @track_agent_performance("TestAgent")
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"
        mock_metrics.record_agent_execution_time.assert_called_once()
        mock_metrics.record_agent_success.assert_called_once()

    @patch("src.observability.cloudwatch.CloudWatchMetrics")
    def test_decorator_records_failure(self, mock_metrics_class):
        """Test decorator records failed execution."""
        mock_metrics = MagicMock()
        mock_metrics_class.return_value = mock_metrics

        @track_agent_performance("TestAgent")
        def test_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_function()

        mock_metrics.record_agent_execution_time.assert_called_once()
        mock_metrics.record_agent_failure.assert_called_once()

    @patch("src.observability.cloudwatch.CloudWatchMetrics")
    def test_decorator_execution_time_recorded(self, mock_metrics_class):
        """Test decorator records execution time."""
        mock_metrics = MagicMock()
        mock_metrics_class.return_value = mock_metrics

        @track_agent_performance("TestAgent")
        def test_function():
            time.sleep(0.1)
            return "done"

        test_function()

        # Check that execution time was recorded and is reasonable
        call_args = mock_metrics.record_agent_execution_time.call_args
        execution_time = call_args[0][1]
        assert execution_time >= 0.1


class TestTrackReportGenerationDecorator:
    """Tests for track_report_generation decorator."""

    @patch("src.observability.cloudwatch.CloudWatchMetrics")
    def test_decorator_records_report_time(self, mock_metrics_class):
        """Test decorator records report generation time."""
        mock_metrics = MagicMock()
        mock_metrics_class.return_value = mock_metrics

        @track_report_generation("standard")
        def generate_report():
            return {"report": "data"}

        result = generate_report()

        assert result == {"report": "data"}
        mock_metrics.record_report_generation_time.assert_called_once()
        call_args = mock_metrics.record_report_generation_time.call_args
        assert call_args[0][0] == "standard"


class TestCloudWatchAlarms:
    """Tests for CloudWatchAlarms class."""

    @patch("src.observability.alarms.boto3.client")
    def test_create_report_generation_sla_alarm(self, mock_boto3_client):
        """Test creating report generation SLA alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_report_generation_sla_alarm(
            alarm_name="TestAlarm", threshold_seconds=300, report_type="standard"
        )

        assert result is True
        mock_client.put_metric_alarm.assert_called_once()
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["AlarmName"] == "TestAlarm"
        assert call_args[1]["Threshold"] == 300

    @patch("src.observability.alarms.boto3.client")
    def test_create_report_generation_sla_alarm_comprehensive(self, mock_boto3_client):
        """Test creating comprehensive report SLA alarm with 15 minute threshold."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_report_generation_sla_alarm(
            alarm_name="ComprehensiveReportAlarm",
            threshold_seconds=900,  # 15 minutes
            report_type="comprehensive",
        )

        assert result is True
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["Threshold"] == 900
        assert "comprehensive" in call_args[1]["AlarmDescription"].lower()

    @patch("src.observability.alarms.boto3.client")
    def test_create_agent_failure_alarm(self, mock_boto3_client):
        """Test creating agent failure alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_agent_failure_alarm("TestAgent")

        assert result is True
        mock_client.put_metric_alarm.assert_called_once()
        call_args = mock_client.put_metric_alarm.call_args
        assert "TestAgent" in call_args[1]["AlarmName"]

    @patch("src.observability.alarms.boto3.client")
    def test_create_agent_failure_alarm_triggers_on_failure(self, mock_boto3_client):
        """Test agent failure alarm configuration triggers on failure count >= 1."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_agent_failure_alarm("DemandForecastingAgent")

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "GreaterThanOrEqualToThreshold"
        assert call_args[1]["Threshold"] == 1
        assert call_args[1]["MetricName"] == "AgentFailure"

    @patch("src.observability.alarms.boto3.client")
    def test_create_agent_performance_alarm(self, mock_boto3_client):
        """Test creating agent performance alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_agent_performance_alarm("TestAgent", threshold_seconds=60)

        assert result is True
        mock_client.put_metric_alarm.assert_called_once()

    @patch("src.observability.alarms.boto3.client")
    def test_create_agent_performance_alarm_configuration(self, mock_boto3_client):
        """Test agent performance alarm triggers when execution time exceeds threshold."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_agent_performance_alarm("TestAgent", threshold_seconds=60)

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "GreaterThanThreshold"
        assert call_args[1]["Threshold"] == 60
        assert call_args[1]["MetricName"] == "AgentExecutionTime"
        assert call_args[1]["EvaluationPeriods"] == 2

    @patch("src.observability.alarms.boto3.client")
    def test_create_forecast_accuracy_alarm(self, mock_boto3_client):
        """Test creating forecast accuracy alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_forecast_accuracy_alarm(threshold_percentage=80)

        assert result is True
        mock_client.put_metric_alarm.assert_called_once()

    @patch("src.observability.alarms.boto3.client")
    def test_create_forecast_accuracy_alarm_triggers_on_low_accuracy(self, mock_boto3_client):
        """Test forecast accuracy alarm triggers when accuracy drops below threshold."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_forecast_accuracy_alarm(threshold_percentage=80)

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "LessThanThreshold"
        assert call_args[1]["Threshold"] == 80
        assert call_args[1]["MetricName"] == "ForecastAccuracy"

    @patch("src.observability.alarms.boto3.client")
    def test_create_supplier_performance_alarm(self, mock_boto3_client):
        """Test creating supplier performance alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_supplier_performance_alarm("supplier-123", threshold_score=70)

        assert result is True
        mock_client.put_metric_alarm.assert_called_once()

    @patch("src.observability.alarms.boto3.client")
    def test_create_supplier_performance_alarm_triggers_on_degradation(self, mock_boto3_client):
        """Test supplier performance alarm triggers when score drops below threshold."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_supplier_performance_alarm("supplier-123", threshold_score=70)

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "LessThanThreshold"
        assert call_args[1]["Threshold"] == 70
        assert call_args[1]["MetricName"] == "SupplierPerformanceScore"

    @patch("src.observability.alarms.boto3.client")
    def test_delete_alarm(self, mock_boto3_client):
        """Test deleting an alarm."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.delete_alarm("TestAlarm")

        assert result is True
        mock_client.delete_alarms.assert_called_once_with(AlarmNames=["TestAlarm"])

    @patch("src.observability.alarms.boto3.client")
    def test_list_alarms(self, mock_boto3_client):
        """Test listing alarms."""
        mock_client = MagicMock()
        mock_client.describe_alarms.return_value = {
            "MetricAlarms": [
                {"AlarmName": "Alarm1"},
                {"AlarmName": "Alarm2"},
            ]
        }
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.list_alarms()

        assert len(result) == 2
        assert "Alarm1" in result
        assert "Alarm2" in result

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_creation_error_handling(self, mock_boto3_client):
        """Test error handling when alarm creation fails."""
        mock_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {"Error": {"Code": "InvalidParameterValue", "Message": "Test error"}}
        mock_client.put_metric_alarm.side_effect = ClientError(error_response, "PutMetricAlarm")
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.create_report_generation_sla_alarm()

        assert result is False

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_deletion_error_handling(self, mock_boto3_client):
        """Test error handling when alarm deletion fails."""
        mock_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {"Error": {"Code": "InvalidParameterValue", "Message": "Test error"}}
        mock_client.delete_alarms.side_effect = ClientError(error_response, "DeleteAlarms")
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.delete_alarm("TestAlarm")

        assert result is False

    @patch("src.observability.alarms.boto3.client")
    def test_list_alarms_empty(self, mock_boto3_client):
        """Test listing alarms when none exist."""
        mock_client = MagicMock()
        mock_client.describe_alarms.return_value = {"MetricAlarms": []}
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        result = alarms.list_alarms()

        assert len(result) == 0
        assert result == []

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_sns_notification_enabled(self, mock_boto3_client):
        """Test that alarms have SNS notifications enabled."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_report_generation_sla_alarm()

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ActionsEnabled"] is True
        # AlarmActions should contain SNS topic if configured
        assert "AlarmActions" in call_args[1]


class TestCloudWatchDashboards:
    """Tests for CloudWatchDashboards class."""

    @patch("src.observability.dashboards.boto3.client")
    def test_create_main_dashboard(self, mock_boto3_client):
        """Test creating main dashboard."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.create_main_dashboard()

        assert result is True
        mock_client.put_dashboard.assert_called_once()
        call_args = mock_client.put_dashboard.call_args
        assert call_args[1]["DashboardName"] == "SupplyChainOptimizer"

    @patch("src.observability.dashboards.boto3.client")
    def test_create_main_dashboard_contains_required_metrics(self, mock_boto3_client):
        """Test main dashboard contains all required metrics."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_main_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = call_args[1]["DashboardBody"]
        
        # Verify dashboard body contains required metrics
        assert "AgentExecutionTime" in dashboard_body
        assert "AgentSuccess" in dashboard_body
        assert "AgentFailure" in dashboard_body
        assert "ReportGenerationTime" in dashboard_body
        assert "ForecastAccuracy" in dashboard_body
        assert "InventoryUpdatesCount" in dashboard_body
        assert "AnomaliesDetected" in dashboard_body
        assert "PurchaseOrderCount" in dashboard_body
        assert "SupplierPerformanceScore" in dashboard_body

    @patch("src.observability.dashboards.boto3.client")
    def test_create_agent_dashboard(self, mock_boto3_client):
        """Test creating agent dashboard."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.create_agent_dashboard()

        assert result is True
        mock_client.put_dashboard.assert_called_once()
        call_args = mock_client.put_dashboard.call_args
        assert call_args[1]["DashboardName"] == "AgentMetrics"

    @patch("src.observability.dashboards.boto3.client")
    def test_create_agent_dashboard_contains_all_agents(self, mock_boto3_client):
        """Test agent dashboard contains metrics for all agents."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_agent_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = call_args[1]["DashboardBody"]
        
        # Verify all agents are included
        assert "DemandForecastingAgent" in dashboard_body
        assert "InventoryOptimizerAgent" in dashboard_body
        assert "SupplierCoordinationAgent" in dashboard_body
        assert "AnomalyDetectionAgent" in dashboard_body
        assert "ReportGenerationAgent" in dashboard_body

    @patch("src.observability.dashboards.boto3.client")
    def test_create_sla_dashboard(self, mock_boto3_client):
        """Test creating SLA dashboard."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.create_sla_dashboard()

        assert result is True
        mock_client.put_dashboard.assert_called_once()
        call_args = mock_client.put_dashboard.call_args
        assert call_args[1]["DashboardName"] == "SLAMetrics"

    @patch("src.observability.dashboards.boto3.client")
    def test_create_sla_dashboard_contains_sla_metrics(self, mock_boto3_client):
        """Test SLA dashboard contains SLA-related metrics."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_sla_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = call_args[1]["DashboardBody"]
        
        # Verify SLA metrics are included
        assert "ReportGenerationTime" in dashboard_body
        assert "ForecastAccuracy" in dashboard_body
        assert "SupplierPerformanceScore" in dashboard_body

    @patch("src.observability.dashboards.boto3.client")
    def test_delete_dashboard(self, mock_boto3_client):
        """Test deleting a dashboard."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.delete_dashboard("TestDashboard")

        assert result is True
        mock_client.delete_dashboards.assert_called_once_with(
            DashboardNames=["TestDashboard"]
        )

    @patch("src.observability.dashboards.boto3.client")
    def test_list_dashboards(self, mock_boto3_client):
        """Test listing dashboards."""
        mock_client = MagicMock()
        mock_client.list_dashboards.return_value = {
            "DashboardEntries": [
                {"DashboardName": "Dashboard1"},
                {"DashboardName": "Dashboard2"},
            ]
        }
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.list_dashboards()

        assert len(result) == 2
        assert "Dashboard1" in result
        assert "Dashboard2" in result

    @patch("src.observability.dashboards.boto3.client")
    def test_create_dashboard_error_handling(self, mock_boto3_client):
        """Test error handling when dashboard creation fails."""
        mock_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {"Error": {"Code": "InvalidParameterValue", "Message": "Test error"}}
        mock_client.put_dashboard.side_effect = ClientError(error_response, "PutDashboard")
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.create_main_dashboard()

        assert result is False

    @patch("src.observability.dashboards.boto3.client")
    def test_delete_dashboard_error_handling(self, mock_boto3_client):
        """Test error handling when dashboard deletion fails."""
        mock_client = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {"Error": {"Code": "InvalidParameterValue", "Message": "Test error"}}
        mock_client.delete_dashboards.side_effect = ClientError(error_response, "DeleteDashboards")
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.delete_dashboard("TestDashboard")

        assert result is False

    @patch("src.observability.dashboards.boto3.client")
    def test_list_dashboards_empty(self, mock_boto3_client):
        """Test listing dashboards when none exist."""
        mock_client = MagicMock()
        mock_client.list_dashboards.return_value = {"DashboardEntries": []}
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        result = dashboards.list_dashboards()

        assert len(result) == 0
        assert result == []


class TestMetricCollectionAccuracy:
    """Tests for metric collection accuracy."""

    @patch("src.observability.cloudwatch.boto3.client")
    def test_metric_collection_preserves_exact_values(self, mock_boto3_client):
        """Test that metric collection preserves exact numeric values."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        test_values = [0.0, 1.5, 42.0, 100.0, 999.99]

        for value in test_values:
            metrics.put_metric("TestMetric", value, unit="Count")

        # Verify all values were recorded correctly
        assert mock_client.put_metric_data.call_count == len(test_values)
        for i, value in enumerate(test_values):
            call_args = mock_client.put_metric_data.call_args_list[i]
            assert call_args[1]["MetricData"][0]["Value"] == value

    @patch("src.observability.cloudwatch.boto3.client")
    def test_metric_collection_with_all_unit_types(self, mock_boto3_client):
        """Test metric collection with various unit types."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        unit_types = ["Count", "Seconds", "Bytes", "Percent", "None"]

        for unit in unit_types:
            metrics.put_metric("TestMetric", 10.0, unit=unit)

        # Verify all units were recorded correctly
        assert mock_client.put_metric_data.call_count == len(unit_types)
        for i, unit in enumerate(unit_types):
            call_args = mock_client.put_metric_data.call_args_list[i]
            assert call_args[1]["MetricData"][0]["Unit"] == unit

    @patch("src.observability.cloudwatch.boto3.client")
    def test_metric_collection_timestamp_included(self, mock_boto3_client):
        """Test that metrics include timestamp."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.put_metric("TestMetric", 42.0)

        call_args = mock_client.put_metric_data.call_args
        metric_data = call_args[1]["MetricData"][0]
        assert "Timestamp" in metric_data
        assert metric_data["Timestamp"] is not None

    @patch("src.observability.cloudwatch.boto3.client")
    def test_multiple_metrics_collected_independently(self, mock_boto3_client):
        """Test that multiple metrics are collected independently."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        metrics.record_agent_execution_time("Agent1", 10.0)
        metrics.record_agent_execution_time("Agent2", 20.0)
        metrics.record_forecast_accuracy(85.5)

        assert mock_client.put_metric_data.call_count == 3

        # Verify each metric has correct value
        calls = mock_client.put_metric_data.call_args_list
        assert calls[0][1]["MetricData"][0]["Value"] == 10.0
        assert calls[1][1]["MetricData"][0]["Value"] == 20.0
        assert calls[2][1]["MetricData"][0]["Value"] == 85.5

    @patch("src.observability.cloudwatch.boto3.client")
    def test_metric_dimensions_preserved_accurately(self, mock_boto3_client):
        """Test that metric dimensions are preserved accurately."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        metrics = CloudWatchMetrics()
        dimensions = {
            "AgentName": "TestAgent",
            "Status": "Success",
            "Environment": "Production",
        }
        metrics.put_metric("TestMetric", 42.0, dimensions=dimensions)

        call_args = mock_client.put_metric_data.call_args
        recorded_dimensions = call_args[1]["MetricData"][0]["Dimensions"]

        # Verify all dimensions are present
        assert len(recorded_dimensions) == 3
        dimension_dict = {d["Name"]: d["Value"] for d in recorded_dimensions}
        assert dimension_dict == dimensions


class TestDashboardDataAccuracy:
    """Tests for dashboard data accuracy."""

    @patch("src.observability.dashboards.boto3.client")
    def test_dashboard_body_is_valid_json(self, mock_boto3_client):
        """Test that dashboard body is valid JSON."""
        import json
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_main_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = call_args[1]["DashboardBody"]

        # Verify it's valid JSON
        parsed = json.loads(dashboard_body)
        assert "widgets" in parsed
        assert isinstance(parsed["widgets"], list)

    @patch("src.observability.dashboards.boto3.client")
    def test_dashboard_contains_correct_namespace(self, mock_boto3_client):
        """Test that dashboard metrics use correct namespace."""
        import json
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_main_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]["DashboardBody"])

        # Verify namespace is correct in all widgets
        # CloudWatch uses "." as shorthand for the namespace in subsequent metrics
        for widget in dashboard_body["widgets"]:
            if widget["type"] == "metric":
                metrics = widget["properties"]["metrics"]
                for i, metric in enumerate(metrics):
                    # First metric should have full namespace, others use "."
                    if i == 0:
                        assert metric[0] == "SupplyChainOptimizer"
                    else:
                        assert metric[0] == "."

    @patch("src.observability.dashboards.boto3.client")
    def test_dashboard_metric_statistics_configured(self, mock_boto3_client):
        """Test that dashboard metrics have statistics configured."""
        import json
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_main_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]["DashboardBody"])

        # Verify statistics are configured
        for widget in dashboard_body["widgets"]:
            if widget["type"] == "metric":
                assert "stat" in widget["properties"]
                assert widget["properties"]["stat"] in ["Average", "Sum", "Maximum", "Minimum"]

    @patch("src.observability.dashboards.boto3.client")
    def test_agent_dashboard_includes_all_agent_metrics(self, mock_boto3_client):
        """Test that agent dashboard includes metrics for all agents."""
        import json
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_agent_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]["DashboardBody"])

        # Collect all agent names from dashboard
        agent_names = set()
        for widget in dashboard_body["widgets"]:
            if widget["type"] == "metric":
                metrics = widget["properties"]["metrics"]
                for metric in metrics:
                    if len(metric) > 2 and "dimensions" in metric[2]:
                        if "AgentName" in metric[2]["dimensions"]:
                            agent_names.add(metric[2]["dimensions"]["AgentName"])

        # Verify all expected agents are present
        expected_agents = {
            "DemandForecastingAgent",
            "InventoryOptimizerAgent",
            "SupplierCoordinationAgent",
            "AnomalyDetectionAgent",
            "ReportGenerationAgent",
        }
        assert agent_names == expected_agents

    @patch("src.observability.dashboards.boto3.client")
    def test_sla_dashboard_has_correct_thresholds(self, mock_boto3_client):
        """Test that SLA dashboard has correct thresholds configured."""
        import json
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        dashboards = CloudWatchDashboards()
        dashboards.create_sla_dashboard()

        call_args = mock_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]["DashboardBody"])

        # Verify SLA thresholds are configured
        dashboard_str = json.dumps(dashboard_body)
        assert "5min" in dashboard_str or "300" in dashboard_str  # 5 minutes
        assert "15min" in dashboard_str or "900" in dashboard_str  # 15 minutes


class TestAlarmTriggering:
    """Tests for alarm triggering behavior."""

    @patch("src.observability.alarms.boto3.client")
    def test_report_sla_alarm_triggers_on_threshold_exceeded(self, mock_boto3_client):
        """Test that report SLA alarm triggers when threshold is exceeded."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_report_generation_sla_alarm(
            threshold_seconds=300, report_type="standard"
        )

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "GreaterThanThreshold"
        assert call_args[1]["Threshold"] == 300
        assert call_args[1]["MetricName"] == "ReportGenerationTime"

    @patch("src.observability.alarms.boto3.client")
    def test_agent_failure_alarm_triggers_immediately(self, mock_boto3_client):
        """Test that agent failure alarm triggers on first failure."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_agent_failure_alarm("TestAgent")

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "GreaterThanOrEqualToThreshold"
        assert call_args[1]["Threshold"] == 1
        assert call_args[1]["EvaluationPeriods"] == 1

    @patch("src.observability.alarms.boto3.client")
    def test_agent_performance_alarm_requires_sustained_degradation(self, mock_boto3_client):
        """Test that agent performance alarm requires sustained degradation."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_agent_performance_alarm("TestAgent", threshold_seconds=60)

        call_args = mock_client.put_metric_alarm.call_args
        # Should require 2 evaluation periods to avoid false positives
        assert call_args[1]["EvaluationPeriods"] == 2

    @patch("src.observability.alarms.boto3.client")
    def test_forecast_accuracy_alarm_triggers_on_low_accuracy(self, mock_boto3_client):
        """Test that forecast accuracy alarm triggers when accuracy drops."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_forecast_accuracy_alarm(threshold_percentage=80)

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "LessThanThreshold"
        assert call_args[1]["Threshold"] == 80

    @patch("src.observability.alarms.boto3.client")
    def test_supplier_performance_alarm_triggers_on_degradation(self, mock_boto3_client):
        """Test that supplier performance alarm triggers on degradation."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_supplier_performance_alarm("supplier-123", threshold_score=70)

        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["ComparisonOperator"] == "LessThanThreshold"
        assert call_args[1]["Threshold"] == 70
        assert call_args[1]["MetricName"] == "SupplierPerformanceScore"

    @patch("src.observability.alarms.boto3.client")
    def test_all_alarms_have_sns_notifications(self, mock_boto3_client):
        """Test that all alarms have SNS notifications configured."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarm_methods = [
            lambda: alarms.create_report_generation_sla_alarm(),
            lambda: alarms.create_agent_failure_alarm("TestAgent"),
            lambda: alarms.create_agent_performance_alarm("TestAgent"),
            lambda: alarms.create_forecast_accuracy_alarm(),
            lambda: alarms.create_supplier_performance_alarm("supplier-123"),
        ]

        for alarm_method in alarm_methods:
            mock_client.reset_mock()
            alarm_method()
            call_args = mock_client.put_metric_alarm.call_args
            assert call_args[1]["ActionsEnabled"] is True
            assert "AlarmActions" in call_args[1]

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_evaluation_periods_appropriate(self, mock_boto3_client):
        """Test that alarm evaluation periods are appropriate for each alarm type."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()

        # Report SLA alarm should evaluate quickly
        alarms.create_report_generation_sla_alarm()
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["EvaluationPeriods"] == 1

        # Agent failure should evaluate quickly
        mock_client.reset_mock()
        alarms.create_agent_failure_alarm("TestAgent")
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["EvaluationPeriods"] == 1

        # Agent performance should require sustained degradation
        mock_client.reset_mock()
        alarms.create_agent_performance_alarm("TestAgent")
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["EvaluationPeriods"] == 2

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_period_configuration(self, mock_boto3_client):
        """Test that alarm periods are configured appropriately."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()
        alarms.create_report_generation_sla_alarm()

        call_args = mock_client.put_metric_alarm.call_args
        # Period should be reasonable (60 seconds)
        assert call_args[1]["Period"] == 60

    @patch("src.observability.alarms.boto3.client")
    def test_alarm_statistic_configuration(self, mock_boto3_client):
        """Test that alarms use appropriate statistics."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        alarms = CloudWatchAlarms()

        # Report generation should use Maximum
        alarms.create_report_generation_sla_alarm()
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["Statistic"] == "Maximum"

        # Agent failure should use Sum
        mock_client.reset_mock()
        alarms.create_agent_failure_alarm("TestAgent")
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["Statistic"] == "Sum"

        # Agent performance should use Average
        mock_client.reset_mock()
        alarms.create_agent_performance_alarm("TestAgent")
        call_args = mock_client.put_metric_alarm.call_args
        assert call_args[1]["Statistic"] == "Average"
