"""Tests for the workflow chaining module."""

import pytest
import logging
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, HealthCheck, settings
from src.workflow_chain import WorkflowChainEngine
from src.data_models import WorkflowChain, ValidationError


class TestWorkflowChainBasic:
    """Basic unit tests for WorkflowChainEngine."""

    def test_engine_initialization(self, tmp_path):
        """Test that engine initializes correctly."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        assert engine is not None
        assert len(engine.get_all_chains()) == 0
        assert len(engine.get_execution_log()) == 0

    def test_register_task(self, tmp_path):
        """Test registering a task."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        # Verify task is registered by creating a chain with it
        chain = engine.create_chain("chain_1", "Test Chain", ["task_1"])
        assert chain is not None

    def test_register_task_invalid_id(self, tmp_path):
        """Test registering a task with invalid ID raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        with pytest.raises(ValidationError):
            engine.register_task("", callback)

    def test_unregister_task(self, tmp_path):
        """Test unregistering a task."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.unregister_task("task_1")
        
        # Verify task is unregistered by trying to create chain with it
        with pytest.raises(ValidationError):
            engine.create_chain("chain_1", "Test Chain", ["task_1"])

    def test_unregister_nonexistent_task(self, tmp_path):
        """Test unregistering a nonexistent task raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        with pytest.raises(ValueError):
            engine.unregister_task("nonexistent")

    def test_create_chain(self, tmp_path):
        """Test creating a workflow chain."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        chain = engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        assert chain.chain_id == "chain_1"
        assert chain.name == "Test Chain"
        assert chain.tasks == ["task_1"]
        assert chain.enabled is True

    def test_create_chain_duplicate_id(self, tmp_path):
        """Test creating a chain with duplicate ID raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        with pytest.raises(ValidationError):
            engine.create_chain("chain_1", "Another Chain", ["task_1"])

    def test_create_chain_empty_tasks(self, tmp_path):
        """Test creating a chain with empty tasks raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        with pytest.raises(ValidationError):
            engine.create_chain("chain_1", "Test Chain", [])

    def test_create_chain_unregistered_task(self, tmp_path):
        """Test creating a chain with unregistered task raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        with pytest.raises(ValidationError):
            engine.create_chain("chain_1", "Test Chain", ["nonexistent"])

    def test_delete_chain(self, tmp_path):
        """Test deleting a workflow chain."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        assert len(engine.get_all_chains()) == 1
        
        engine.delete_chain("chain_1")
        assert len(engine.get_all_chains()) == 0

    def test_delete_nonexistent_chain(self, tmp_path):
        """Test deleting a nonexistent chain raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        with pytest.raises(ValueError):
            engine.delete_chain("nonexistent")

    def test_get_chain(self, tmp_path):
        """Test retrieving a chain by ID."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        chain = engine.get_chain("chain_1")
        assert chain is not None
        assert chain.chain_id == "chain_1"

    def test_get_nonexistent_chain(self, tmp_path):
        """Test retrieving a nonexistent chain returns None."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        chain = engine.get_chain("nonexistent")
        assert chain is None

    def test_get_all_chains(self, tmp_path):
        """Test retrieving all chains."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        
        for i in range(3):
            engine.create_chain(f"chain_{i}", f"Chain {i}", ["task_1"])
        
        chains = engine.get_all_chains()
        assert len(chains) == 3

    def test_enable_chain(self, tmp_path):
        """Test enabling a disabled chain."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"], enabled=False)
        
        chain = engine.get_chain("chain_1")
        assert chain.enabled is False
        
        engine.enable_chain("chain_1")
        chain = engine.get_chain("chain_1")
        assert chain.enabled is True

    def test_disable_chain(self, tmp_path):
        """Test disabling an enabled chain."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"], enabled=True)
        
        chain = engine.get_chain("chain_1")
        assert chain.enabled is True
        
        engine.disable_chain("chain_1")
        chain = engine.get_chain("chain_1")
        assert chain.enabled is False

    def test_execute_chain_single_task(self, tmp_path):
        """Test executing a chain with a single task."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result_1")
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        success, result, error = engine.execute_chain("chain_1")
        
        assert success is True
        assert result == "result_1"
        assert error is None
        callback.assert_called_once()

    def test_execute_chain_multiple_tasks(self, tmp_path):
        """Test executing a chain with multiple tasks."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        callback_1 = Mock(return_value="result_1")
        callback_2 = Mock(return_value="result_2")
        callback_3 = Mock(return_value="result_3")
        
        engine.register_task("task_1", callback_1)
        engine.register_task("task_2", callback_2)
        engine.register_task("task_3", callback_3)
        engine.create_chain("chain_1", "Test Chain", ["task_1", "task_2", "task_3"])
        
        success, result, error = engine.execute_chain("chain_1")
        
        assert success is True
        assert result == "result_3"
        assert error is None
        callback_1.assert_called_once()
        callback_2.assert_called_once()
        callback_3.assert_called_once()

    def test_execute_chain_with_input_passing(self, tmp_path):
        """Test executing a chain with output passing between tasks."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        # Task 1 returns initial value
        callback_1 = Mock(return_value=10)
        # Task 2 receives input and returns modified value
        callback_2 = Mock(return_value=20)
        # Task 3 receives input and returns final value
        callback_3 = Mock(return_value=30)
        
        engine.register_task("task_1", callback_1)
        engine.register_task("task_2", callback_2)
        engine.register_task("task_3", callback_3)
        engine.create_chain("chain_1", "Test Chain", ["task_1", "task_2", "task_3"])
        
        success, result, error = engine.execute_chain("chain_1")
        
        assert success is True
        assert result == 30
        assert error is None
        
        # Verify task 2 was called with output from task 1
        callback_2.assert_called_once_with(10)
        # Verify task 3 was called with output from task 2
        callback_3.assert_called_once_with(20)

    def test_execute_chain_task_failure(self, tmp_path):
        """Test executing a chain where a task fails."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        callback_1 = Mock(return_value="result_1")
        callback_2 = Mock(side_effect=Exception("Task 2 failed"))
        callback_3 = Mock(return_value="result_3")
        
        engine.register_task("task_1", callback_1)
        engine.register_task("task_2", callback_2)
        engine.register_task("task_3", callback_3)
        engine.create_chain("chain_1", "Test Chain", ["task_1", "task_2", "task_3"])
        
        success, result, error = engine.execute_chain("chain_1")
        
        assert success is False
        assert error is not None
        assert "task_2" in error.lower() or "Task 2" in error
        assert "failed" in error.lower()
        
        # Verify task 1 was called
        callback_1.assert_called_once()
        # Verify task 2 was called
        callback_2.assert_called_once()
        # Verify task 3 was NOT called
        callback_3.assert_not_called()

    def test_execute_disabled_chain(self, tmp_path):
        """Test executing a disabled chain returns error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock()
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"], enabled=False)
        
        success, result, error = engine.execute_chain("chain_1")
        
        assert success is False
        assert error is not None
        assert "disabled" in error.lower()
        callback.assert_not_called()

    def test_execute_nonexistent_chain(self, tmp_path):
        """Test executing a nonexistent chain raises error."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        
        with pytest.raises(ValueError):
            engine.execute_chain("nonexistent")

    def test_execution_logging(self, tmp_path):
        """Test that chain execution is logged."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        engine.execute_chain("chain_1")
        
        log = engine.get_execution_log()
        assert len(log) == 1
        assert log[0]["chain_id"] == "chain_1"
        assert log[0]["success"] is True
        assert log[0]["result"] == "result"
        assert log[0]["error"] is None

    def test_execution_error_logging(self, tmp_path):
        """Test that chain execution errors are logged."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(side_effect=Exception("Test error"))
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        engine.execute_chain("chain_1")
        
        log = engine.get_execution_log()
        assert len(log) == 1
        assert log[0]["chain_id"] == "chain_1"
        assert log[0]["success"] is False
        assert "Test error" in log[0]["error"]

    def test_get_execution_log_for_chain(self, tmp_path):
        """Test retrieving execution log for a specific chain."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Chain 1", ["task_1"])
        engine.create_chain("chain_2", "Chain 2", ["task_1"])
        
        engine.execute_chain("chain_1")
        engine.execute_chain("chain_2")
        engine.execute_chain("chain_1")
        
        log_chain_1 = engine.get_execution_log_for_chain("chain_1")
        assert len(log_chain_1) == 2
        assert all(record["chain_id"] == "chain_1" for record in log_chain_1)

    def test_clear_execution_log(self, tmp_path):
        """Test clearing the execution log."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        engine.execute_chain("chain_1")
        assert len(engine.get_execution_log()) == 1
        
        engine.clear_execution_log()
        assert len(engine.get_execution_log()) == 0

    def test_chain_last_executed_updated(self, tmp_path):
        """Test that chain's last_executed is updated after execution."""
        engine = WorkflowChainEngine(config_dir=str(tmp_path))
        callback = Mock(return_value="result")
        
        engine.register_task("task_1", callback)
        chain = engine.create_chain("chain_1", "Test Chain", ["task_1"])
        
        assert chain.last_executed is None
        
        engine.execute_chain("chain_1")
        
        chain = engine.get_chain("chain_1")
        assert chain.last_executed is not None


class TestWorkflowChainProperties:
    """Property-based tests for WorkflowChainEngine."""

    @given(
        chain_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        chain_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        num_tasks=st.integers(min_value=1, max_value=5)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_24_workflow_chain_execution_order(self, chain_id, chain_name, num_tasks):
        """
        **Feature: lazy-automation-platform, Property 24: Workflow Chain Execution Order**
        
        For any workflow chain, tasks should execute in the specified order with 
        output from one task passed as input to the next.
        
        **Validates: Requirements 9.1, 9.2**
        """
        engine = WorkflowChainEngine(config_dir="config")
        
        # Create mock tasks that track execution order
        execution_order = []
        task_callbacks = []
        
        for i in range(num_tasks):
            def make_callback(task_num):
                def callback(input_val=None):
                    execution_order.append(task_num)
                    return f"output_{task_num}"
                return callback
            
            callback = make_callback(i)
            task_callbacks.append(callback)
            engine.register_task(f"task_{i}", callback)
        
        # Create chain with all tasks
        task_ids = [f"task_{i}" for i in range(num_tasks)]
        chain = engine.create_chain(chain_id, chain_name, task_ids)
        
        # Verify chain was created with correct task order
        assert chain.tasks == task_ids
        assert len(chain.tasks) == num_tasks
        
        # Execute the chain
        success, result, error = engine.execute_chain(chain_id)
        
        # Verify execution was successful
        assert success is True
        assert error is None
        
        # Verify tasks executed in order
        assert execution_order == list(range(num_tasks))
        
        # Verify final result is from last task
        assert result == f"output_{num_tasks - 1}"

    @given(
        chain_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        chain_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        failure_position=st.integers(min_value=0, max_value=2)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_25_workflow_chain_error_handling(self, chain_id, chain_name, failure_position):
        """
        **Feature: lazy-automation-platform, Property 25: Workflow Chain Error Handling**
        
        For any workflow chain where a task fails, the system should stop execution 
        and report which task failed and why.
        
        **Validates: Requirements 9.3**
        """
        engine = WorkflowChainEngine(config_dir="config")
        
        # Create 3 tasks where one fails
        task_ids = ["task_0", "task_1", "task_2"]
        
        for i, task_id in enumerate(task_ids):
            if i == failure_position:
                # This task will fail
                callback = Mock(side_effect=Exception(f"Error in {task_id}"))
            else:
                # This task will succeed
                callback = Mock(return_value=f"output_{i}")
            
            engine.register_task(task_id, callback)
        
        # Create chain
        chain = engine.create_chain(chain_id, chain_name, task_ids)
        
        # Execute the chain
        success, result, error = engine.execute_chain(chain_id)
        
        # Verify execution failed
        assert success is False
        assert error is not None
        
        # Verify error message contains the failed task ID
        assert f"task_{failure_position}" in error
        
        # Verify error message indicates failure
        assert "failed" in error.lower()
        
        # Verify execution log contains failed task info
        log = engine.get_execution_log_for_chain(chain_id)
        assert len(log) > 0
        assert log[0]["success"] is False
        assert log[0]["failed_task"] == f"task_{failure_position}"

    @given(
        chain_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        chain_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        num_tasks=st.integers(min_value=1, max_value=5)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_26_workflow_chain_output(self, chain_id, chain_name, num_tasks):
        """
        **Feature: lazy-automation-platform, Property 26: Workflow Chain Output**
        
        For any successfully completed workflow chain, the system should display 
        the final result and provide a download option.
        
        **Validates: Requirements 9.4**
        """
        engine = WorkflowChainEngine(config_dir="config")
        
        # Create mock tasks
        for i in range(num_tasks):
            callback = Mock(return_value=f"output_{i}")
            engine.register_task(f"task_{i}", callback)
        
        # Create chain
        task_ids = [f"task_{i}" for i in range(num_tasks)]
        chain = engine.create_chain(chain_id, chain_name, task_ids)
        
        # Execute the chain
        success, result, error = engine.execute_chain(chain_id)
        
        # Verify execution was successful
        assert success is True
        assert error is None
        
        # Verify result is not None (can be downloaded)
        assert result is not None
        
        # Verify result is from the last task
        assert result == f"output_{num_tasks - 1}"
        
        # Verify execution was logged
        log = engine.get_execution_log_for_chain(chain_id)
        assert len(log) > 0
        assert log[0]["success"] is True
        assert log[0]["result"] == result
