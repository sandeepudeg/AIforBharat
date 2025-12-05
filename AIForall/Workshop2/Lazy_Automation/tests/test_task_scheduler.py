"""Tests for the task scheduler module."""

import pytest
import time
import logging
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, HealthCheck, settings
from src.task_scheduler import TaskScheduler
from src.data_models import ScheduledTask, ValidationError


class TestTaskSchedulerBasic:
    """Basic unit tests for TaskScheduler."""

    def test_scheduler_initialization(self, tmp_path):
        """Test that scheduler initializes correctly."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        assert scheduler is not None
        assert len(scheduler.get_all_tasks()) == 0
        assert len(scheduler.get_execution_log()) == 0

    def test_schedule_task_with_cron(self, tmp_path):
        """Test scheduling a task with cron expression."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        task = scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="0 9 * * *",  # 9 AM daily
            callback=callback,
            enabled=True
        )

        assert task.task_id == "test_task"
        assert task.task_name == "Test Task"
        assert task.schedule == "0 9 * * *"
        assert task.enabled is True
        assert task.execution_count == 0

    def test_schedule_task_with_interval(self, tmp_path):
        """Test scheduling a task with interval."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        task = scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback,
            enabled=True
        )

        assert task.task_id == "test_task"
        assert task.schedule == "daily"

    def test_schedule_task_duplicate_id(self, tmp_path):
        """Test that scheduling with duplicate ID raises error."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        with pytest.raises(ValidationError):
            scheduler.schedule_task(
                task_id="test_task",
                task_name="Another Task",
                schedule="daily",
                callback=callback
            )

    def test_schedule_task_invalid_schedule(self, tmp_path):
        """Test that invalid schedule raises error."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        with pytest.raises(ValidationError):
            scheduler.schedule_task(
                task_id="test_task",
                task_name="Test Task",
                schedule="invalid_schedule",
                callback=callback
            )

    def test_unschedule_task(self, tmp_path):
        """Test unscheduling a task."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        assert len(scheduler.get_all_tasks()) == 1

        scheduler.unschedule_task("test_task")
        assert len(scheduler.get_all_tasks()) == 0

    def test_unschedule_nonexistent_task(self, tmp_path):
        """Test unscheduling a nonexistent task raises error."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))

        with pytest.raises(ValueError):
            scheduler.unschedule_task("nonexistent")

    def test_enable_task(self, tmp_path):
        """Test enabling a disabled task."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback,
            enabled=False
        )

        task = scheduler.get_task("test_task")
        assert task.enabled is False

        scheduler.enable_task("test_task")
        task = scheduler.get_task("test_task")
        assert task.enabled is True

    def test_disable_task(self, tmp_path):
        """Test disabling an enabled task."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback,
            enabled=True
        )

        task = scheduler.get_task("test_task")
        assert task.enabled is True

        scheduler.disable_task("test_task")
        task = scheduler.get_task("test_task")
        assert task.enabled is False

    def test_get_task(self, tmp_path):
        """Test retrieving a task by ID."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        task = scheduler.get_task("test_task")
        assert task is not None
        assert task.task_id == "test_task"

    def test_get_nonexistent_task(self, tmp_path):
        """Test retrieving a nonexistent task returns None."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        task = scheduler.get_task("nonexistent")
        assert task is None

    def test_get_all_tasks(self, tmp_path):
        """Test retrieving all tasks."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock()

        for i in range(3):
            scheduler.schedule_task(
                task_id=f"task_{i}",
                task_name=f"Task {i}",
                schedule="daily",
                callback=callback
            )

        tasks = scheduler.get_all_tasks()
        assert len(tasks) == 3

    def test_task_execution_logging(self, tmp_path):
        """Test that task execution is logged."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        # Manually execute the task
        scheduler._execute_task("test_task", callback)

        log = scheduler.get_execution_log()
        assert len(log) == 1
        assert log[0]["task_id"] == "test_task"
        assert log[0]["success"] is True
        assert log[0]["result"] == "success"

    def test_task_execution_error_logging(self, tmp_path):
        """Test that task execution errors are logged."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock(side_effect=Exception("Test error"))

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        # Manually execute the task
        scheduler._execute_task("test_task", callback)

        log = scheduler.get_execution_log()
        assert len(log) == 1
        assert log[0]["task_id"] == "test_task"
        assert log[0]["success"] is False
        assert "Test error" in log[0]["error"]

    def test_execution_count_increments(self, tmp_path):
        """Test that execution count increments."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        task = scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        assert task.execution_count == 0

        scheduler._execute_task("test_task", callback)
        task = scheduler.get_task("test_task")
        assert task.execution_count == 1

        scheduler._execute_task("test_task", callback)
        task = scheduler.get_task("test_task")
        assert task.execution_count == 2

    def test_notification_callback(self, tmp_path):
        """Test that notification callbacks are called."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        task_callback = Mock(return_value="success")
        notification_callback = Mock()

        scheduler.register_notification_callback(notification_callback)

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=task_callback
        )

        scheduler._execute_task("test_task", task_callback)

        notification_callback.assert_called_once()
        args = notification_callback.call_args[0]
        assert args[0] == "test_task"
        assert args[1] is True
        assert args[2] == "success"
        assert args[3] is None

    def test_get_execution_log_for_task(self, tmp_path):
        """Test retrieving execution log for a specific task."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        scheduler.schedule_task(
            task_id="task_1",
            task_name="Task 1",
            schedule="daily",
            callback=callback
        )

        scheduler.schedule_task(
            task_id="task_2",
            task_name="Task 2",
            schedule="daily",
            callback=callback
        )

        scheduler._execute_task("task_1", callback)
        scheduler._execute_task("task_2", callback)
        scheduler._execute_task("task_1", callback)

        log_task_1 = scheduler.get_execution_log_for_task("task_1")
        assert len(log_task_1) == 2
        assert all(record["task_id"] == "task_1" for record in log_task_1)

    def test_clear_execution_log(self, tmp_path):
        """Test clearing the execution log."""
        scheduler = TaskScheduler(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        scheduler.schedule_task(
            task_id="test_task",
            task_name="Test Task",
            schedule="daily",
            callback=callback
        )

        scheduler._execute_task("test_task", callback)
        assert len(scheduler.get_execution_log()) == 1

        scheduler.clear_execution_log()
        assert len(scheduler.get_execution_log()) == 0


class TestTaskSchedulerProperties:
    """Property-based tests for TaskScheduler."""

    @given(
        task_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        task_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        schedule=st.sampled_from(["daily", "weekly", "hourly", "monthly"])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_22_scheduled_task_execution(self, task_id, task_name, schedule):
        """
        **Feature: lazy-automation-platform, Property 22: Scheduled Task Execution**
        
        For any scheduled automation task, the system should execute the task at the 
        specified time or interval and log the execution.
        
        **Validates: Requirements 8.1, 8.2, 8.3**
        """
        scheduler = TaskScheduler(config_dir="config")
        callback = Mock(return_value="test_result")

        # Schedule the task
        task = scheduler.schedule_task(
            task_id=task_id,
            task_name=task_name,
            schedule=schedule,
            callback=callback,
            enabled=True
        )

        # Verify task was scheduled
        assert task.task_id == task_id
        assert task.task_name == task_name
        assert task.schedule == schedule
        assert task.enabled is True

        # Execute the task
        scheduler._execute_task(task_id, callback)

        # Verify execution was logged
        log = scheduler.get_execution_log_for_task(task_id)
        assert len(log) > 0
        assert log[0]["task_id"] == task_id
        assert log[0]["success"] is True
        assert "timestamp" in log[0]

        # Verify execution count incremented
        updated_task = scheduler.get_task(task_id)
        assert updated_task.execution_count == 1
        assert updated_task.last_execution is not None

    @given(
        task_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        task_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))).filter(lambda x: x.strip()),
        schedule=st.sampled_from(["daily", "weekly", "hourly", "monthly"]),
        success=st.booleans()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_23_scheduled_task_notification(self, task_id, task_name, schedule, success):
        """
        **Feature: lazy-automation-platform, Property 23: Scheduled Task Notification**
        
        For any completed scheduled task, the system should notify the user of the 
        result (success or failure).
        
        **Validates: Requirements 8.4**
        """
        scheduler = TaskScheduler(config_dir="config")
        
        # Create callback that succeeds or fails based on property
        if success:
            callback = Mock(return_value="success_result")
        else:
            callback = Mock(side_effect=Exception("Task failed"))

        # Register notification callback
        notification_callback = Mock()
        scheduler.register_notification_callback(notification_callback)

        # Schedule the task
        scheduler.schedule_task(
            task_id=task_id,
            task_name=task_name,
            schedule=schedule,
            callback=callback,
            enabled=True
        )

        # Execute the task
        scheduler._execute_task(task_id, callback)

        # Verify notification was called
        notification_callback.assert_called_once()
        
        # Verify notification contains correct status
        call_args = notification_callback.call_args[0]
        assert call_args[0] == task_id  # task_id
        assert call_args[1] == success  # success status
        
        # Verify execution was logged with correct status
        log = scheduler.get_execution_log_for_task(task_id)
        assert len(log) > 0
        assert log[0]["success"] == success
