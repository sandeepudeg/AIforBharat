"""Integration tests for AgentOrchestrator with communication patterns."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.orchestration.agent_orchestrator import (
    AgentOrchestrator,
    AgentTask,
    ExecutionResult,
    ExecutionPattern
)


class TestAgentOrchestratorSequential:
    """Tests for sequential agent communication pattern."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_sequential_execution_with_dependencies(self, mock_optimizer, mock_forecaster):
        """Test sequential execution where tasks depend on previous results."""
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

        # Create tasks with dependencies
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify results
        assert len(results) == 2
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"
        assert results["forecast_task"].output["forecast"] == 100
        assert results["optimize_task"].output["eoq"] == 50

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_sequential_execution_stops_on_failure(self, mock_forecaster):
        """Test sequential execution stops when a task fails."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2])

        # Verify failure handling
        assert results["forecast_task"].status == "error"
        assert results["optimize_task"].status == "error"
        assert "Dependency forecast_task failed" in results["optimize_task"].error

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    @patch("src.orchestration.agent_orchestrator.AnomalyDetectionAgent")
    def test_sequential_execution_passes_data_between_tasks(
        self, mock_anomaly, mock_optimizer, mock_forecaster
    ):
        """Test that sequential execution passes output from one task to the next."""
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

        mock_anomaly_instance = Mock()
        mock_anomaly.return_value = mock_anomaly_instance
        mock_anomaly_instance.detect_anomalies.return_value = {
            "anomalies": []
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

        task3 = AgentTask(
            task_id="task3",
            agent_type="anomaly_detection",
            operation="detect_anomalies",
            inputs={"sku": "SKU-001"},
            dependencies=["task2"]
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_sequential([task1, task2, task3])

        # Verify all tasks succeeded
        assert all(r.status == "success" for r in results.values())
        assert len(results) == 3


class TestAgentOrchestratorParallel:
    """Tests for parallel agent communication pattern."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    @patch("src.orchestration.agent_orchestrator.AnomalyDetectionAgent")
    def test_parallel_execution_runs_tasks_concurrently(
        self, mock_anomaly, mock_optimizer, mock_forecaster
    ):
        """Test parallel execution runs multiple tasks concurrently."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_parallel([task1, task2, task3])

        # Verify all tasks succeeded
        assert len(results) == 3
        assert all(r.status == "success" for r in results.values())

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_parallel_execution_handles_partial_failures(self, mock_optimizer, mock_forecaster):
        """Test parallel execution handles failures in some tasks."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_parallel([task1, task2])

        # Verify partial failure
        assert results["forecast_task"].status == "error"
        assert results["optimize_task"].status == "success"


class TestAgentOrchestratorConditional:
    """Tests for conditional agent communication pattern."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_conditional_execution_skips_tasks_when_condition_false(
        self, mock_optimizer, mock_forecaster
    ):
        """Test conditional execution skips tasks when condition is not met."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks with conditions
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        # Condition that evaluates to False
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: False  # This task should be skipped
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        context = {}
        results = orchestrator.execute_conditional([task1, task2], context)

        # Verify results
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "skipped"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_conditional_execution_executes_tasks_when_condition_true(
        self, mock_optimizer, mock_forecaster
    ):
        """Test conditional execution executes tasks when condition is met."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks with conditions
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        # Condition that evaluates to True
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: True  # This task should execute
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        context = {}
        results = orchestrator.execute_conditional([task1, task2], context)

        # Verify results
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_conditional_execution_with_context_based_conditions(
        self, mock_optimizer, mock_forecaster
    ):
        """Test conditional execution uses context to determine execution."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks with context-based conditions
        task1 = AgentTask(
            task_id="forecast_task",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        # Condition based on context
        task2 = AgentTask(
            task_id="optimize_task",
            agent_type="optimization",
            operation="optimize_inventory",
            inputs={"sku": "SKU-001"},
            condition=lambda ctx: ctx.get("execute_optimization", False)
        )

        # Execute workflow with context
        orchestrator = AgentOrchestrator()
        context = {"execute_optimization": True}
        results = orchestrator.execute_conditional([task1, task2], context)

        # Verify results
        assert results["forecast_task"].status == "success"
        assert results["optimize_task"].status == "success"


class TestAgentOrchestratorWorkflow:
    """Tests for complete workflow execution."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    @patch("src.orchestration.agent_orchestrator.AnomalyDetectionAgent")
    def test_execute_workflow_sequential_pattern(
        self, mock_anomaly, mock_optimizer, mock_forecaster
    ):
        """Test execute_workflow with sequential pattern."""
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

        # Create tasks
        tasks = [
            AgentTask(
                task_id="task1",
                agent_type="forecasting",
                operation="generate_forecast",
                inputs={"sku": "SKU-001"}
            ),
            AgentTask(
                task_id="task2",
                agent_type="optimization",
                operation="optimize_inventory",
                inputs={"sku": "SKU-001"},
                dependencies=["task1"]
            ),
            AgentTask(
                task_id="task3",
                agent_type="anomaly_detection",
                operation="detect_anomalies",
                inputs={"sku": "SKU-001"},
                dependencies=["task2"]
            )
        ]

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow(
            tasks,
            pattern=ExecutionPattern.SEQUENTIAL
        )

        # Verify results
        assert len(results) == 3
        assert all(r.status == "success" for r in results.values())

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    @patch("src.orchestration.agent_orchestrator.AnomalyDetectionAgent")
    def test_execute_workflow_parallel_pattern(
        self, mock_anomaly, mock_optimizer, mock_forecaster
    ):
        """Test execute_workflow with parallel pattern."""
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
        tasks = [
            AgentTask(
                task_id="task1",
                agent_type="forecasting",
                operation="generate_forecast",
                inputs={"sku": "SKU-001"}
            ),
            AgentTask(
                task_id="task2",
                agent_type="optimization",
                operation="optimize_inventory",
                inputs={"sku": "SKU-001"}
            ),
            AgentTask(
                task_id="task3",
                agent_type="anomaly_detection",
                operation="detect_anomalies",
                inputs={"sku": "SKU-001"}
            )
        ]

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow(
            tasks,
            pattern=ExecutionPattern.PARALLEL
        )

        # Verify results
        assert len(results) == 3
        assert all(r.status == "success" for r in results.values())

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    @patch("src.orchestration.agent_orchestrator.InventoryOptimizerAgent")
    def test_execute_workflow_conditional_pattern(self, mock_optimizer, mock_forecaster):
        """Test execute_workflow with conditional pattern."""
        # Setup mocks
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        mock_optimizer_instance = Mock()
        mock_optimizer.return_value = mock_optimizer_instance
        mock_optimizer_instance.optimize_inventory.return_value = {"eoq": 50}

        # Create tasks with conditions
        tasks = [
            AgentTask(
                task_id="task1",
                agent_type="forecasting",
                operation="generate_forecast",
                inputs={"sku": "SKU-001"}
            ),
            AgentTask(
                task_id="task2",
                agent_type="optimization",
                operation="optimize_inventory",
                inputs={"sku": "SKU-001"},
                condition=lambda ctx: ctx.get("optimize", True)
            )
        ]

        # Execute workflow
        orchestrator = AgentOrchestrator()
        context = {"optimize": True}
        results = orchestrator.execute_workflow(
            tasks,
            pattern=ExecutionPattern.CONDITIONAL,
            context=context
        )

        # Verify results
        assert results["task1"].status == "success"
        assert results["task2"].status == "success"


class TestAgentOrchestratorStateManagement:
    """Tests for agent state management."""

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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify history
        history = orchestrator.get_execution_history()
        assert len(history) == 1
        assert "task1" in history
        assert history["task1"].status == "success"

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_execution_history_accumulates(self, mock_forecaster):
        """Test that execution history accumulates across multiple workflows."""
        # Setup mock
        mock_forecaster_instance = Mock()
        mock_forecaster.return_value = mock_forecaster_instance
        mock_forecaster_instance.generate_forecast.return_value = {"forecast": 100}

        # Create tasks
        task1 = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-001"}
        )

        task2 = AgentTask(
            task_id="task2",
            agent_type="forecasting",
            operation="generate_forecast",
            inputs={"sku": "SKU-002"}
        )

        # Execute workflows
        orchestrator = AgentOrchestrator()
        orchestrator.execute_workflow([task1])
        orchestrator.execute_workflow([task2])

        # Verify history
        history = orchestrator.get_execution_history()
        assert len(history) == 2
        assert "task1" in history
        assert "task2" in history

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_clear_execution_history(self, mock_forecaster):
        """Test clearing execution history."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        orchestrator.execute_workflow([task])

        # Verify history exists
        history = orchestrator.get_execution_history()
        assert len(history) == 1

        # Clear history
        orchestrator.clear_execution_history()

        # Verify history is cleared
        history = orchestrator.get_execution_history()
        assert len(history) == 0


class TestAgentOrchestratorErrorHandling:
    """Tests for error handling and retry logic."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_task_execution_captures_errors(self, mock_forecaster):
        """Test that task execution captures errors."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify error handling
        assert results["task1"].status == "error"
        assert "Database error" in results["task1"].error

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_unknown_agent_type_error(self, mock_forecaster):
        """Test error handling for unknown agent type."""
        # Create task with unknown agent type
        task = AgentTask(
            task_id="task1",
            agent_type="unknown_agent",
            operation="some_operation",
            inputs={}
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify error handling
        assert results["task1"].status == "error"
        assert "Unknown agent type" in results["task1"].error

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_unknown_operation_error(self, mock_forecaster):
        """Test error handling for unknown operation."""
        # Setup mock - configure it to not have the method
        mock_forecaster_instance = Mock(spec=[])  # Empty spec means no methods
        mock_forecaster.return_value = mock_forecaster_instance

        # Create task with unknown operation
        task = AgentTask(
            task_id="task1",
            agent_type="forecasting",
            operation="unknown_operation",
            inputs={}
        )

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify error handling
        assert results["task1"].status == "error"
        assert "does not have operation" in results["task1"].error


class TestAgentOrchestratorExecutionMetrics:
    """Tests for execution metrics and timing."""

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_execution_time_tracking(self, mock_forecaster):
        """Test that execution time is tracked."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify execution time is tracked
        assert results["task1"].execution_time_ms >= 0

    @patch("src.orchestration.agent_orchestrator.DemandForecastingAgent")
    def test_execution_result_timestamp(self, mock_forecaster):
        """Test that execution result has timestamp."""
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

        # Execute workflow
        orchestrator = AgentOrchestrator()
        results = orchestrator.execute_workflow([task])

        # Verify timestamp exists
        assert results["task1"].timestamp is not None
        assert isinstance(results["task1"].timestamp, datetime)
