"""Integration tests for agent orchestration and communication."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from src.orchestration.agent_orchestrator import (
    AgentOrchestrator,
    AgentTask,
    ExecutionPattern,
    ExecutionResult,
)


class TestSequentialExecution:
    """Tests for sequential agent execution."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_sequential_execution_with_dependencies(self, mock_optimizer, mock_forecaster):
        """Test sequential execution where tasks depend on previous outputs."""
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

        # Create tasks with dependency
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            dependencies=["forecast_task"]
        )

        # Execute sequentially
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify results
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"
        assert results["forecast_task"].output["forecast"] == 100
        assert results["optimize_task"].output["eoq"] == 50

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_sequential_execution_stops_on_error(self, mock_forecaster):
        """Test that sequential execution stops when a task fails."""
        # Setup mock to fail
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.side_effect = Exception("Forecast failed")

        # Create tasks
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            dependencies=["forecast_task"]
        )

        # Execute sequentially
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify first task failed
        assert results["forecast_task"].status == "error"
        # Verify second task also failed due to dependency
        assert results["optimize_task"].status == "error"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_sequential_execution_passes_output_to_next_task(self, mock_optimizer, mock_forecaster):
        """Test that output from one task is passed to the next."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {
            "forecast": 100,
            "confidence": 0.95
        }

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {
            "eoq": 50
        }

        # Create tasks
        task1 = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            dependencies=["task1"]
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify both succeeded
        assert results["task1"].status == "success"
        assert results["task2"].status == "success"


class TestParallelExecution:
    """Tests for parallel agent execution."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    @patch("src.orchestration.agent_orchestrator.AnomalyDetectionAgent")
    def test_parallel_execution_of_independent_tasks(self, mock_anomaly, mock_optimizer, mock_forecaster):
        """Test parallel execution of independent tasks."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {"anomalies": []}

        # Create independent tasks
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"}
        )
        
        task3 = AgentTask(
            task_id="anomaly_task",
            agent_type="anomaly_detection",
            operation="detect_anomalies",
            inputs={"sku": "SKU-001"}
        )

        # Execute in parallel
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_parallel([task1, task2, task3])

        # Verify all succeeded
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"
        assert results["anomaly_task"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_parallel_execution_handles_partial_failures(self, mock_optimizer, mock_forecaster):
        """Test parallel execution with some tasks failing."""
        # Setup mocks - one fails, one succeeds
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.side_effect = Exception("Forecast failed")

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"}
        )

        # Execute in parallel
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_parallel([task1, task2])

        # Verify one failed and one succeeded
        assert results["forecast_task"].status == "error"
        assert results["optimize_task"].status == "success"


class TestConditionalExecution:
    """Tests for conditional agent execution."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_conditional_execution_skips_when_condition_false(self, mock_optimizer, mock_forecaster):
        """Test that tasks are skipped when condition is false."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 50}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance

        # Create tasks with condition
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        # This task should be skipped because forecast < 100
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: ctx.get("forecast_task", {}).get("output", {}).get("forecast", 0) > 100
        )

        # Execute conditionally
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_conditional([task1, task2])

        # Verify first task succeeded
        assert results["forecast_task"].status == "success"
        # Verify second task was skipped
        assert results["optimize_task"].status == "skipped"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_conditional_execution_executes_when_condition_true(self, mock_optimizer, mock_forecaster):
        """Test that tasks execute when condition is true."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 150}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 75}

        # Create tasks with condition
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        # This task should execute because forecast > 100
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: ctx.get("forecast_task", {}).get("forecast", 0) > 100
        )

        # Execute conditionally
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_conditional([task1, task2])

        # Verify both succeeded
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"
        assert results["optimize_task"].output["eoq"] == 75


class TestWorkflowExecution:
    """Tests for complete workflow execution."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_execute_workflow_sequential_pattern(self, mock_optimizer, mock_forecaster):
        """Test workflow execution with sequential pattern."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks
        task1 = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            dependencies=["task1"]
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow(
            [task1, task2],
            pattern=ExecutionPattern.SEQUENTIAL
        )

        # Verify results
        assert results["task1"].status == "success"
        assert results["task2"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_execute_workflow_parallel_pattern(self, mock_optimizer, mock_forecaster):
        """Test workflow execution with parallel pattern."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create independent tasks
        task1 = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"}
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow(
            [task1, task2],
            pattern=ExecutionPattern.PARALLEL
        )

        # Verify results
        assert results["task1"].status == "success"
        assert results["task2"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_execute_workflow_conditional_pattern(self, mock_optimizer, mock_forecaster):
        """Test workflow execution with conditional pattern."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 150}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 75}

        # Create tasks with condition
        task1 = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: ctx.get("task1", {}).get("forecast", 0) > 100
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow(
            [task1, task2],
            pattern=ExecutionPattern.CONDITIONAL
        )

        # Verify results
        assert results["task1"].status == "success"
        assert results["task2"].status == "success"


class TestAgentCommunication:
    """Tests for agent communication and data passing."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_agent_communication_passes_data_between_agents(self, mock_optimizer, mock_forecaster):
        """Test that data is correctly passed between agents."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {
            "sku": "SKU-001",
            "forecast": 100,
            "confidence": 0.95
        }

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        
        # Capture the inputs to optimize_inventory
        def capture_inputs(**kwargs):
            capture_inputs.last_inputs = kwargs
            return {"eoq": 50}
        
        mock_optimizer_instance.optimize_inventory.side_effect = capture_inputs

        # Create sequential tasks
        task1 = AgentTask(
            task_id="forecast",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )
        
        task2 = AgentTask(
            task_id="optimize",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            dependencies=["forecast"]
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify data was passed
        assert results["forecast"].status == "success"
        assert results["optimize"].status == "success"
        # Verify the forecast output was merged into optimize inputs
        assert capture_inputs.last_inputs["forecast"] == 100

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_execution_history_tracking(self, mock_forecaster):
        """Test that execution history is tracked."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        # Create task
        task = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task], pattern=ExecutionPattern.SEQUENTIAL)

        # Verify history is tracked
        history = orchestrator.get_execution_history()
        assert "task1" in history
        assert history["task1"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_clear_execution_history(self, mock_forecaster):
        """Test clearing execution history."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        # Create and execute task
        task = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        orchestrator = AgentOrchestrator()
        orchestrator.execute_workflow([task], pattern=ExecutionPattern.SEQUENTIAL)

        # Verify history exists
        assert len(orchestrator.get_execution_history()) > 0

        # Clear history
        orchestrator.clear_execution_history()

        # Verify history is empty
        assert len(orchestrator.get_execution_history()) == 0


class TestErrorHandling:
    """Tests for error handling in orchestration."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_error_handling_captures_exceptions(self, mock_forecaster):
        """Test that exceptions are captured and reported."""
        # Setup mock to raise exception
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.side_effect = Exception("Database error")

        # Create task
        task = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task], pattern=ExecutionPattern.SEQUENTIAL)

        # Verify error is captured
        assert results["task1"].status == "error"
        assert "Database error" in results["task1"].error

    def test_error_handling_invalid_agent_type(self):
        """Test error handling for invalid agent type."""
        # Create task with invalid agent type
        task = AgentTask(
            task_id="task1",
            agent_type="invalid_agent",
            operation="some_operation",
            inputs={}
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task], pattern=ExecutionPattern.SEQUENTIAL)

        # Verify error is captured
        assert results["task1"].status == "error"
        assert "Unknown agent type" in results["task1"].error

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_error_handling_invalid_operation(self, mock_forecaster):
        """Test error handling for invalid operation."""
        # Setup mock - don't add the invalid_operation method
        mock_forecaster_instance = Mock(spec=[])  # Empty spec means no methods
        mock_forecaster.return_value = mock_forecaster_instance

        # Create task with invalid operation
        task = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="invalid_operation",
            inputs={}
        )

        # Execute
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task], pattern=ExecutionPattern.SEQUENTIAL)

        # Verify error is captured
        assert results["task1"].status == "error"
        assert "does not have operation" in results["task1"].error
