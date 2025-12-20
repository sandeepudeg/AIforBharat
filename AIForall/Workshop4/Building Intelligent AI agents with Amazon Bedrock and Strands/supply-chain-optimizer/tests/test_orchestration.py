"""Tests for event-driven orchestration."""

import json
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.orchestration.orchestrator import Orchestrator
from src.orchestration.event_handler import EventHandler
from src.orchestration.setup import EventDrivenSetup


class TestOrchestrator:
    """Tests for the Orchestrator class."""

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_setup_inventory_update_rule(self, mock_get_client):
        """Test setting up inventory update rule."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_rule.return_value = {"RuleArn": "arn:aws:events:us-east-1:123456789:rule/inventory-update-rule"}

        orchestrator = Orchestrator()
        result = orchestrator.setup_inventory_update_rule()

        assert result == "arn:aws:events:us-east-1:123456789:rule/inventory-update-rule"
        mock_client.put_rule.assert_called_once()
        call_args = mock_client.put_rule.call_args
        assert call_args[1]["Name"] == "inventory-update-rule"
        assert call_args[1]["State"] == "ENABLED"

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_setup_scheduled_forecasting_job(self, mock_get_client):
        """Test setting up scheduled forecasting job."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_rule.return_value = {"RuleArn": "arn:aws:events:us-east-1:123456789:rule/daily-forecasting-job"}

        orchestrator = Orchestrator()
        result = orchestrator.setup_scheduled_forecasting_job()

        assert result == "arn:aws:events:us-east-1:123456789:rule/daily-forecasting-job"
        mock_client.put_rule.assert_called_once()
        call_args = mock_client.put_rule.call_args
        assert call_args[1]["Name"] == "daily-forecasting-job"
        assert "ScheduleExpression" in call_args[1]

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_setup_scheduled_optimization_job(self, mock_get_client):
        """Test setting up scheduled optimization job."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_rule.return_value = {"RuleArn": "arn:aws:events:us-east-1:123456789:rule/daily-optimization-job"}

        orchestrator = Orchestrator()
        result = orchestrator.setup_scheduled_optimization_job()

        assert result == "arn:aws:events:us-east-1:123456789:rule/daily-optimization-job"
        mock_client.put_rule.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_setup_scheduled_anomaly_detection_job(self, mock_get_client):
        """Test setting up scheduled anomaly detection job."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_rule.return_value = {"RuleArn": "arn:aws:events:us-east-1:123456789:rule/hourly-anomaly-detection-job"}

        orchestrator = Orchestrator()
        result = orchestrator.setup_scheduled_anomaly_detection_job()

        assert result == "arn:aws:events:us-east-1:123456789:rule/hourly-anomaly-detection-job"
        mock_client.put_rule.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_setup_scheduled_report_generation_job(self, mock_get_client):
        """Test setting up scheduled report generation job."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_rule.return_value = {"RuleArn": "arn:aws:events:us-east-1:123456789:rule/weekly-report-generation-job"}

        orchestrator = Orchestrator()
        result = orchestrator.setup_scheduled_report_generation_job()

        assert result == "arn:aws:events:us-east-1:123456789:rule/weekly-report-generation-job"
        mock_client.put_rule.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_add_lambda_target(self, mock_get_client):
        """Test adding Lambda target to rule."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_targets.return_value = {"FailedEntryCount": 0}

        orchestrator = Orchestrator()
        result = orchestrator.add_lambda_target(
            "test-rule",
            "arn:aws:lambda:us-east-1:123456789:function:test-function"
        )

        assert result is True
        mock_client.put_targets.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_trigger_agent_workflow(self, mock_get_client):
        """Test triggering agent workflow."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.put_events.return_value = {
            "FailedEntryCount": 0,
            "Entries": [{"EventId": "event-123"}]
        }

        orchestrator = Orchestrator()
        result = orchestrator.trigger_agent_workflow(
            "forecasting",
            {"sku": "SKU-001"}
        )

        assert result == "event-123"
        mock_client.put_events.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_list_rules(self, mock_get_client):
        """Test listing EventBridge rules."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.list_rules.return_value = {
            "Rules": [
                {"Name": "rule-1", "State": "ENABLED"},
                {"Name": "rule-2", "State": "DISABLED"}
            ]
        }

        orchestrator = Orchestrator()
        result = orchestrator.list_rules()

        assert len(result) == 2
        assert result[0]["Name"] == "rule-1"

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_delete_rule(self, mock_get_client):
        """Test deleting EventBridge rule."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        orchestrator = Orchestrator()
        orchestrator.delete_rule("test-rule")

        mock_client.remove_targets.assert_called_once()
        mock_client.delete_rule.assert_called_once()

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_enable_rule(self, mock_get_client):
        """Test enabling EventBridge rule."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        orchestrator = Orchestrator()
        orchestrator.enable_rule("test-rule")

        mock_client.enable_rule.assert_called_once_with(Name="test-rule")

    @patch("src.orchestration.orchestrator.get_eventbridge_client")
    def test_disable_rule(self, mock_get_client):
        """Test disabling EventBridge rule."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        orchestrator = Orchestrator()
        orchestrator.disable_rule("test-rule")

        mock_client.disable_rule.assert_called_once_with(Name="test-rule")


class TestEventHandler:
    """Tests for the EventHandler class."""

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    def test_handle_inventory_update_event(self, mock_anomaly, mock_optimizer, mock_forecaster):
        """Test handling inventory update event."""
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"optimization": "data"}

        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {"anomalies": []}

        handler = EventHandler()
        event = {
            "detail": {
                "sku": "SKU-001",
                "warehouse_id": "WH-001"
            }
        }

        result = handler.handle_inventory_update_event(event)

        assert result["status"] == "success"
        assert result["sku"] == "SKU-001"
        assert result["warehouse_id"] == "WH-001"

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_handle_forecasting_job_event(self, mock_forecaster):
        """Test handling forecasting job event."""
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001", "SKU-002"])

        event = {}
        result = handler.handle_forecasting_job_event(event)

        assert result["status"] == "success"
        assert result["job_type"] == "forecasting"
        assert result["skus_processed"] == 2

    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    def test_handle_optimization_job_event(self, mock_optimizer):
        """Test handling optimization job event."""
        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"optimization": "data"}

        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001"])

        event = {}
        result = handler.handle_optimization_job_event(event)

        assert result["status"] == "success"
        assert result["job_type"] == "optimization"

    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    def test_handle_anomaly_detection_job_event(self, mock_anomaly):
        """Test handling anomaly detection job event."""
        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {"anomalies": []}

        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001"])

        event = {}
        result = handler.handle_anomaly_detection_job_event(event)

        assert result["status"] == "success"
        assert result["job_type"] == "anomaly_detection"

    @patch("src.orchestration.event_handler.ReportGenerationAgent")
    def test_handle_report_generation_job_event(self, mock_report):
        """Test handling report generation job event."""
        mock_report_instance = Mock()
        mock_report.return_value = mock_report_instance
        mock_report_instance.generate_report.return_value = {"report": "data"}

        handler = EventHandler()
        event = {}
        result = handler.handle_report_generation_job_event(event)

        assert result["status"] == "success"
        assert result["job_type"] == "report_generation"

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_handle_event_routing(self, mock_forecaster):
        """Test event routing to appropriate handlers."""
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=[])

        event = {
            "detail-type": "Agent Workflow: Forecasting",
            "source": "supply-chain.orchestrator"
        }

        result = handler.handle_event(event)

        assert result["status"] == "success"
        assert result["job_type"] == "forecasting"

    def test_handle_unknown_event(self):
        """Test handling unknown event type."""
        handler = EventHandler()
        event = {
            "detail-type": "Unknown Event",
            "source": "unknown.source"
        }

        result = handler.handle_event(event)

        assert result["status"] == "unknown"


class TestEventDrivenSetup:
    """Tests for the EventDrivenSetup class."""

    @patch("src.orchestration.setup.Orchestrator")
    def test_setup_all_rules(self, mock_orchestrator_class):
        """Test setting up all EventBridge rules."""
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        mock_orchestrator.setup_inventory_update_rule.return_value = "arn:inventory"
        mock_orchestrator.setup_scheduled_forecasting_job.return_value = "arn:forecasting"
        mock_orchestrator.setup_scheduled_optimization_job.return_value = "arn:optimization"
        mock_orchestrator.setup_scheduled_anomaly_detection_job.return_value = "arn:anomaly"
        mock_orchestrator.setup_scheduled_report_generation_job.return_value = "arn:report"

        setup = EventDrivenSetup()
        result = setup.setup_all_rules()

        assert result["status"] == "success"
        assert result["inventory_update_rule"]["status"] == "success"
        assert result["forecasting_rule"]["status"] == "success"
        assert result["optimization_rule"]["status"] == "success"
        assert result["anomaly_detection_rule"]["status"] == "success"
        assert result["report_generation_rule"]["status"] == "success"

    @patch("src.orchestration.setup.Orchestrator")
    def test_cleanup_all_rules(self, mock_orchestrator_class):
        """Test cleaning up all EventBridge rules."""
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        setup = EventDrivenSetup()
        result = setup.cleanup_all_rules()

        assert result["status"] == "success"
        assert len(result["deleted_rules"]) == 5
        mock_orchestrator.delete_rule.assert_called()
