"""Integration tests for event-driven orchestration workflows."""

import json
from unittest.mock import Mock, patch, MagicMock, call
import pytest

from src.orchestration.orchestrator import Orchestrator
from src.orchestration.event_handler import EventHandler
from src.orchestration.lambda_handlers import (
    lambda_handler,
    forecasting_handler,
    optimization_handler,
    anomaly_detection_handler,
    report_generation_handler,
    inventory_update_handler
)


class TestInventoryUpdateWorkflow:
    """Integration tests for inventory update workflow."""

    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_end_to_end_inventory_update_workflow(self, mock_forecaster, mock_optimizer, mock_anomaly):
        """Test complete inventory update workflow from event to results."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {
            "sku": "SKU-001",
            "forecast": 100,
            "confidence_80": 80,
            "confidence_95": 95
        }

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {
            "sku": "SKU-001",
            "eoq": 50,
            "reorder_point": 25
        }

        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {
            "sku": "SKU-001",
            "anomalies": []
        }

        # Create event
        event = {
            "source": "supply-chain.inventory",
            "detail-type": "Inventory Update",
            "detail": {
                "event_type": "inventory_changed",
                "sku": "SKU-001",
                "warehouse_id": "WH-001",
                "quantity_change": 100
            }
        }

        # Execute workflow
        handler = EventHandler()
        result = handler.handle_inventory_update_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["sku"] == "SKU-001"
        assert result["warehouse_id"] == "WH-001"
        assert "forecast" in result
        assert "optimization" in result
        assert "anomalies" in result

        # Verify all agents were called
        mock_forecaster_instance.generate_forecast.assert_called_once_with("SKU-001")
        mock_optimizer_instance.optimize_inventory.assert_called_once_with("SKU-001")
        mock_anomaly_instance.detect_anomalies.assert_called_once_with("SKU-001")

    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_inventory_update_lambda_handler(self, mock_forecaster, mock_optimizer, mock_anomaly):
        """Test Lambda handler for inventory update events."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"optimization": "data"}

        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {"anomalies": []}

        # Create event
        event = {
            "source": "supply-chain.inventory",
            "detail-type": "Inventory Update",
            "detail": {
                "sku": "SKU-001",
                "warehouse_id": "WH-001"
            }
        }

        # Execute Lambda handler
        response = inventory_update_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"


class TestForecastingJobWorkflow:
    """Integration tests for forecasting job workflow."""

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_end_to_end_forecasting_job_workflow(self, mock_forecaster):
        """Test complete forecasting job workflow."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {
            "sku": "SKU-001",
            "forecast": 100
        }

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001", "SKU-002", "SKU-003"])
        result = handler.handle_forecasting_job_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["job_type"] == "forecasting"
        assert result["skus_processed"] == 3
        assert len(result["results"]) == 3

        # Verify all SKUs were processed
        assert mock_forecaster_instance.generate_forecast.call_count == 3

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_forecasting_job_lambda_handler(self, mock_forecaster):
        """Test Lambda handler for forecasting jobs."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        # Create event
        event = {}

        # Execute Lambda handler
        response = forecasting_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["job_type"] == "forecasting"

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_forecasting_job_partial_failure(self, mock_forecaster):
        """Test forecasting job with partial failures."""
        # Setup mock to fail on second call
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.side_effect = [
            {"forecast": "data"},
            Exception("Forecast failed"),
            {"forecast": "data"}
        ]

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001", "SKU-002", "SKU-003"])
        result = handler.handle_forecasting_job_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["skus_processed"] == 3
        assert len(result["results"]) == 3
        
        # Verify partial failure
        success_count = sum(1 for r in result["results"] if r["status"] == "success")
        error_count = sum(1 for r in result["results"] if r["status"] == "error")
        assert success_count == 2
        assert error_count == 1


class TestOptimizationJobWorkflow:
    """Integration tests for optimization job workflow."""

    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    def test_end_to_end_optimization_job_workflow(self, mock_optimizer):
        """Test complete optimization job workflow."""
        # Setup mock
        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {
            "sku": "SKU-001",
            "eoq": 50
        }

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001", "SKU-002"])
        result = handler.handle_optimization_job_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["job_type"] == "optimization"
        assert result["skus_processed"] == 2

    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    def test_optimization_job_lambda_handler(self, mock_optimizer):
        """Test Lambda handler for optimization jobs."""
        # Setup mock
        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"optimization": "data"}

        # Create event
        event = {}

        # Execute Lambda handler
        response = optimization_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["job_type"] == "optimization"


class TestAnomalyDetectionWorkflow:
    """Integration tests for anomaly detection workflow."""

    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    def test_end_to_end_anomaly_detection_workflow(self, mock_anomaly):
        """Test complete anomaly detection workflow."""
        # Setup mock
        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {
            "sku": "SKU-001",
            "anomalies": [
                {
                    "type": "inventory_deviation",
                    "severity": "high",
                    "confidence": 0.95
                }
            ]
        }

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001"])
        result = handler.handle_anomaly_detection_job_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["job_type"] == "anomaly_detection"
        assert result["skus_processed"] == 1

    @patch("src.orchestration.event_handler.AnomalyDetectionAgent")
    def test_anomaly_detection_lambda_handler(self, mock_anomaly):
        """Test Lambda handler for anomaly detection jobs."""
        # Setup mock
        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {"anomalies": []}

        # Create event
        event = {}

        # Execute Lambda handler
        response = anomaly_detection_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["job_type"] == "anomaly_detection"


class TestReportGenerationWorkflow:
    """Integration tests for report generation workflow."""

    @patch("src.orchestration.event_handler.ReportGenerationAgent")
    def test_end_to_end_report_generation_workflow(self, mock_report):
        """Test complete report generation workflow."""
        # Setup mock
        mock_report_instance = Mock()
        mock_report.return_value = mock_report_instance
        mock_report_instance.generate_report.return_value = {
            "report_id": "RPT-001",
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 0.95
        }

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        result = handler.handle_report_generation_job_event(event)

        # Verify results
        assert result["status"] == "success"
        assert result["job_type"] == "report_generation"
        assert "report" in result

    @patch("src.orchestration.event_handler.ReportGenerationAgent")
    def test_report_generation_lambda_handler(self, mock_report):
        """Test Lambda handler for report generation jobs."""
        # Setup mock
        mock_report_instance = Mock()
        mock_report.return_value = mock_report_instance
        mock_report_instance.generate_report.return_value = {"report": "data"}

        # Create event
        event = {}

        # Execute Lambda handler
        response = report_generation_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["job_type"] == "report_generation"


class TestEventRouting:
    """Integration tests for event routing."""

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_main_lambda_handler_routes_to_forecasting(self, mock_forecaster):
        """Test main Lambda handler routes forecasting events correctly."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": "data"}

        # Create event
        event = {
            "detail-type": "Agent Workflow: Forecasting",
            "source": "supply-chain.orchestrator"
        }

        # Execute Lambda handler
        response = lambda_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"

    @patch("src.orchestration.event_handler.InventoryOptimizerAgent")
    def test_main_lambda_handler_routes_to_optimization(self, mock_optimizer):
        """Test main Lambda handler routes optimization events correctly."""
        # Setup mock
        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"optimization": "data"}

        # Create event
        event = {
            "detail-type": "Agent Workflow: Optimization",
            "source": "supply-chain.orchestrator"
        }

        # Execute Lambda handler
        response = lambda_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"

    def test_main_lambda_handler_handles_unknown_event(self):
        """Test main Lambda handler handles unknown events gracefully."""
        # Create event
        event = {
            "detail-type": "Unknown Event Type",
            "source": "unknown.source"
        }

        # Execute Lambda handler
        response = lambda_handler(event, None)

        # Verify response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "unknown"


class TestErrorHandling:
    """Integration tests for error handling in workflows."""

    @patch("src.orchestration.event_handler.DemandForecastingAgent")
    def test_forecasting_workflow_error_handling(self, mock_forecaster):
        """Test forecasting workflow handles errors gracefully."""
        # Setup mock to raise exception
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.side_effect = Exception("Database error")

        # Create event
        event = {}

        # Execute workflow
        handler = EventHandler()
        handler._get_all_skus = Mock(return_value=["SKU-001"])
        result = handler.handle_forecasting_job_event(event)

        # Verify error handling
        assert result["status"] == "success"
        assert result["results"][0]["status"] == "error"
        assert "error" in result["results"][0]

    def test_lambda_handler_error_handling(self):
        """Test Lambda handler error handling."""
        # Create invalid event
        event = None

        # Execute Lambda handler
        response = lambda_handler(event, None)

        # Verify error response
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "error"
