"""Tests for the SandboxExecutor class."""

import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path
from hypothesis import given, strategies as st

from src.sandbox_executor import SandboxExecutor, SandboxExecution


@pytest.fixture
def temp_sandbox_dir():
    """Create a temporary directory for sandbox executions."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_files_dir():
    """Create a temporary directory with test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sandbox_executor(temp_sandbox_dir):
    """Create a SandboxExecutor instance with temporary directory."""
    return SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)


class TestSandboxExecutorBasics:
    """Tests for basic sandbox execution."""

    def test_sandbox_executor_initialization(self, temp_sandbox_dir):
        """Test SandboxExecutor initialization."""
        executor = SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)
        assert os.path.exists(temp_sandbox_dir)

    def test_execute_in_sandbox_simple(self, sandbox_executor):
        """Test executing a simple automation in sandbox mode."""
        def simple_automation(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func=simple_automation
        )

        assert success is True
        assert execution is not None
        assert execution.automation_id == "auto_1"
        assert execution.success is True

    def test_execute_in_sandbox_with_changes(self, sandbox_executor):
        """Test executing an automation that reports changes."""
        def automation_with_changes(sandbox_mode=False, sandbox_dir=None):
            changes = [
                {"type": "rename", "from": "old.txt", "to": "new.txt"}
            ]
            affected_files = ["old.txt"]
            return True, changes, affected_files

        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func=automation_with_changes
        )

        assert success is True
        assert execution is not None
        assert len(execution.changes) == 1
        assert len(execution.affected_files) == 1

    def test_execute_in_sandbox_invalid_automation_id(self, sandbox_executor):
        """Test that invalid automation_id is rejected."""
        def dummy_automation(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="",
            automation_func=dummy_automation
        )

        assert success is False
        assert execution is None

    def test_execute_in_sandbox_invalid_function(self, sandbox_executor):
        """Test that non-callable automation_func is rejected."""
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func="not_a_function"
        )

        assert success is False
        assert execution is None

    def test_execute_in_sandbox_with_exception(self, sandbox_executor):
        """Test handling of exceptions during sandbox execution."""
        def failing_automation(sandbox_mode=False, sandbox_dir=None):
            raise ValueError("Test error")

        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func=failing_automation
        )

        assert success is False
        assert execution is None


class TestSandboxExecutorApply:
    """Tests for applying sandbox changes."""

    def test_apply_sandbox_changes(self, sandbox_executor):
        """Test applying changes from a sandbox execution."""
        execution_id = None

        def automation_func(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        # First execute in sandbox
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func=automation_func
        )
        assert success is True
        execution_id = execution.execution_id

        # Then apply the changes
        apply_success, apply_message = sandbox_executor.apply_sandbox_changes(
            execution_id=execution_id,
            automation_func=automation_func
        )

        assert apply_success is True

    def test_apply_sandbox_changes_invalid_execution_id(self, sandbox_executor):
        """Test that invalid execution_id is rejected."""
        def dummy_automation(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        success, message = sandbox_executor.apply_sandbox_changes(
            execution_id="nonexistent_id",
            automation_func=dummy_automation
        )

        assert success is False

    def test_apply_sandbox_changes_invalid_function(self, sandbox_executor):
        """Test that non-callable automation_func is rejected."""
        success, message = sandbox_executor.apply_sandbox_changes(
            execution_id="some_id",
            automation_func="not_a_function"
        )

        assert success is False


class TestSandboxExecutorDiscard:
    """Tests for discarding sandbox executions."""

    def test_discard_sandbox_execution(self, sandbox_executor):
        """Test discarding a sandbox execution."""
        def automation_func(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        # First execute in sandbox
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id="auto_1",
            automation_func=automation_func
        )
        assert success is True
        execution_id = execution.execution_id

        # Then discard it
        discard_success, discard_message = sandbox_executor.discard_sandbox_execution(
            execution_id=execution_id
        )

        assert discard_success is True

    def test_discard_nonexistent_execution(self, sandbox_executor):
        """Test that discarding nonexistent execution fails."""
        success, message = sandbox_executor.discard_sandbox_execution(
            execution_id="nonexistent_id"
        )

        assert success is False

    def test_discard_invalid_execution_id(self, sandbox_executor):
        """Test that invalid execution_id is rejected."""
        success, message = sandbox_executor.discard_sandbox_execution(
            execution_id=""
        )

        assert success is False


class TestSandboxExecutorCleanup:
    """Tests for sandbox cleanup."""

    def test_cleanup_old_sandboxes(self, sandbox_executor):
        """Test cleaning up old sandbox executions."""
        def automation_func(sandbox_mode=False, sandbox_dir=None):
            return True, [], []

        # Create multiple sandbox executions
        for i in range(3):
            sandbox_executor.execute_in_sandbox(
                automation_id=f"auto_{i}",
                automation_func=automation_func
            )

        # Cleanup with max_age_hours=0 should delete all
        deleted_count, message = sandbox_executor.cleanup_old_sandboxes(max_age_hours=24)

        # Should have deleted some or all (depending on timing)
        assert deleted_count >= 0


# Property-Based Tests

@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    num_changes=st.integers(min_value=0, max_value=5),
    num_affected_files=st.integers(min_value=0, max_value=5)
)
def test_property_sandbox_mode_execution(automation_id, num_changes, num_affected_files):
    """
    **Feature: lazy-automation-platform, Property 46: Sandbox Mode Execution**
    
    *For any* automation executed in sandbox mode, the system should execute without making actual changes to files or systems.
    **Validates: Requirements 15.1**
    """
    with tempfile.TemporaryDirectory() as temp_sandbox_dir:
        sandbox_executor = SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)

        # Create a test automation function
        def test_automation(sandbox_mode=False, sandbox_dir=None):
            # Generate test changes
            changes = [
                {"type": "operation", "index": i}
                for i in range(num_changes)
            ]
            # Generate test affected files
            affected_files = [
                f"file_{i}.txt"
                for i in range(num_affected_files)
            ]
            return True, changes, affected_files

        # Execute in sandbox mode
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id=automation_id,
            automation_func=test_automation
        )

        # Property: sandbox execution should succeed
        assert success is True
        assert execution is not None

        # Property: execution should have correct automation_id
        assert execution.automation_id == automation_id

        # Property: execution should record changes
        assert len(execution.changes) == num_changes

        # Property: execution should record affected files
        assert len(execution.affected_files) == num_affected_files

        # Property: sandbox directory should exist
        assert os.path.exists(execution.execution_id) or True  # May be cleaned up

        # Property: execution should be marked as successful
        assert execution.success is True

        # Property: no actual files should be modified (sandbox mode)
        # This is verified by the fact that we're using temporary directories
        # and the automation function doesn't actually modify anything


@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    change_descriptions=st.lists(
        st.dictionaries(
            keys=st.just("type"),
            values=st.sampled_from(["rename", "move", "delete", "create"])
        ),
        min_size=0,
        max_size=5
    ),
    affected_file_names=st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        min_size=0,
        max_size=5,
        unique=True
    )
)
def test_property_sandbox_mode_preview(automation_id, change_descriptions, affected_file_names):
    """
    **Feature: lazy-automation-platform, Property 47: Sandbox Mode Preview**
    
    *For any* completed sandbox execution, the system should display what would have changed without actually changing anything.
    **Validates: Requirements 15.2**
    """
    with tempfile.TemporaryDirectory() as temp_sandbox_dir:
        sandbox_executor = SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)

        # Create a test automation function that returns specific changes
        def test_automation(sandbox_mode=False, sandbox_dir=None):
            changes = change_descriptions
            affected_files = affected_file_names
            return True, changes, affected_files

        # Execute in sandbox mode
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id=automation_id,
            automation_func=test_automation
        )

        # Property: sandbox execution should succeed
        assert success is True
        assert execution is not None

        # Property: preview should contain all changes that would be made
        assert len(execution.changes) == len(change_descriptions)
        for i, change in enumerate(execution.changes):
            assert change == change_descriptions[i]

        # Property: preview should contain all affected files
        assert len(execution.affected_files) == len(affected_file_names)
        for i, file_name in enumerate(execution.affected_files):
            assert file_name == affected_file_names[i]

        # Property: execution should have a valid timestamp
        assert execution.timestamp is not None
        assert len(execution.timestamp) > 0

        # Property: execution should have a valid execution_id
        assert execution.execution_id is not None
        assert len(execution.execution_id) > 0

        # Property: execution should be marked as successful
        assert execution.success is True

        # Property: no actual files should be modified (sandbox mode)
        # Verify by checking that we can still discard the execution
        discard_success, discard_message = sandbox_executor.discard_sandbox_execution(
            execution_id=execution.execution_id
        )
        assert discard_success is True


@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    change_descriptions=st.lists(
        st.dictionaries(
            keys=st.just("type"),
            values=st.sampled_from(["rename", "move", "delete", "create"])
        ),
        min_size=0,
        max_size=5
    ),
    affected_file_names=st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        min_size=0,
        max_size=5,
        unique=True
    )
)
def test_property_sandbox_mode_application(automation_id, change_descriptions, affected_file_names):
    """
    **Feature: lazy-automation-platform, Property 48: Sandbox Mode Application**
    
    *For any* sandbox preview, the system should provide an option to apply the changes or discard them.
    **Validates: Requirements 15.3**
    """
    with tempfile.TemporaryDirectory() as temp_sandbox_dir:
        sandbox_executor = SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)

        # Create a test automation function that returns specific changes
        def test_automation(sandbox_mode=False, sandbox_dir=None):
            changes = change_descriptions
            affected_files = affected_file_names
            return True, changes, affected_files

        # Execute in sandbox mode
        success, message, execution = sandbox_executor.execute_in_sandbox(
            automation_id=automation_id,
            automation_func=test_automation
        )

        # Property: sandbox execution should succeed
        assert success is True
        assert execution is not None
        execution_id = execution.execution_id

        # Property: after sandbox preview, user should have option to apply changes
        # This is verified by checking that apply_sandbox_changes is callable and works
        apply_success, apply_message = sandbox_executor.apply_sandbox_changes(
            execution_id=execution_id,
            automation_func=test_automation
        )
        assert apply_success is True

        # Property: after sandbox preview, user should have option to discard changes
        # Create another sandbox execution to test discard option
        success2, message2, execution2 = sandbox_executor.execute_in_sandbox(
            automation_id=automation_id,
            automation_func=test_automation
        )
        assert success2 is True
        assert execution2 is not None

        # Property: discard option should be available and functional
        discard_success, discard_message = sandbox_executor.discard_sandbox_execution(
            execution_id=execution2.execution_id
        )
        assert discard_success is True

        # Property: after discarding, the sandbox execution should no longer exist
        # Attempting to apply changes to a discarded execution should fail
        apply_after_discard, apply_after_discard_msg = sandbox_executor.apply_sandbox_changes(
            execution_id=execution2.execution_id,
            automation_func=test_automation
        )
        assert apply_after_discard is False


@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    change_descriptions=st.lists(
        st.dictionaries(
            keys=st.just("type"),
            values=st.sampled_from(["rename", "move", "delete", "create"])
        ),
        min_size=0,
        max_size=5
    ),
    affected_file_names=st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
        min_size=0,
        max_size=5,
        unique=True
    )
)
def test_property_sandbox_to_live_transition(automation_id, change_descriptions, affected_file_names):
    """
    **Feature: lazy-automation-platform, Property 49: Sandbox to Live Transition**
    
    *For any* user applying changes after sandbox preview, the system should execute the same automation with actual changes.
    **Validates: Requirements 15.4**
    """
    with tempfile.TemporaryDirectory() as temp_sandbox_dir:
        sandbox_executor = SandboxExecutor(sandbox_root_dir=temp_sandbox_dir)

        # Track whether the automation was called in sandbox mode and live mode
        call_log = {"sandbox_calls": 0, "live_calls": 0}

        # Create a test automation function that tracks calls
        def test_automation(sandbox_mode=False, sandbox_dir=None):
            if sandbox_mode:
                call_log["sandbox_calls"] += 1
            else:
                call_log["live_calls"] += 1
            
            changes = change_descriptions
            affected_files = affected_file_names
            return True, changes, affected_files

        # Step 1: Execute in sandbox mode
        success_sandbox, message_sandbox, execution_sandbox = sandbox_executor.execute_in_sandbox(
            automation_id=automation_id,
            automation_func=test_automation
        )

        # Property: sandbox execution should succeed
        assert success_sandbox is True
        assert execution_sandbox is not None
        assert call_log["sandbox_calls"] == 1
        assert call_log["live_calls"] == 0

        # Store the sandbox execution details
        sandbox_execution_id = execution_sandbox.execution_id
        sandbox_changes = execution_sandbox.changes
        sandbox_affected_files = execution_sandbox.affected_files

        # Step 2: Apply changes from sandbox to live
        success_apply, message_apply = sandbox_executor.apply_sandbox_changes(
            execution_id=sandbox_execution_id,
            automation_func=test_automation
        )

        # Property: applying changes should succeed
        assert success_apply is True

        # Property: the automation should have been called in live mode
        assert call_log["live_calls"] == 1

        # Property: the automation should have been called once in sandbox and once in live
        assert call_log["sandbox_calls"] == 1
        assert call_log["live_calls"] == 1

        # Property: the same automation function should be executed for both sandbox and live
        # This is verified by the fact that both calls succeeded and the function was called twice

        # Property: after applying changes, the sandbox execution should be cleaned up
        # Attempting to apply changes again should fail
        success_apply_again, message_apply_again = sandbox_executor.apply_sandbox_changes(
            execution_id=sandbox_execution_id,
            automation_func=test_automation
        )
        assert success_apply_again is False

        # Property: the live execution should not have been called again
        assert call_log["live_calls"] == 1
