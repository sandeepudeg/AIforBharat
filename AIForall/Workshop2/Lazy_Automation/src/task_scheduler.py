"""Task scheduling system for automating tasks at specified times or intervals."""

import logging
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from src.data_models import ScheduledTask, ValidationError


class TaskScheduler:
    """Manages scheduling and execution of automation tasks."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the TaskScheduler.

        Args:
            config_dir: Directory for storing scheduler state
        """
        self.config_dir = config_dir
        self.scheduler = BackgroundScheduler()
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_callbacks: Dict[str, Callable] = {}
        self._execution_log: List[Dict[str, Any]] = []
        self._notification_callbacks: List[Callable] = []
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Only add file handler if not already present
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            try:
                handler = logging.FileHandler(f"{config_dir}/scheduler.log", encoding='utf-8')
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except (OSError, IOError):
                # If file handler fails, just use console logging
                pass

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Task scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Task scheduler stopped")

    def schedule_task(
        self,
        task_id: str,
        task_name: str,
        schedule: str,
        callback: Callable,
        enabled: bool = True
    ) -> ScheduledTask:
        """
        Schedule a new automation task.

        Args:
            task_id: Unique identifier for the task
            task_name: Human-readable name for the task
            schedule: Cron expression or interval string (e.g., "0 9 * * *" for 9 AM daily)
            callback: Function to call when task is triggered
            enabled: Whether the task is enabled

        Returns:
            ScheduledTask object

        Raises:
            ValidationError: If task_id already exists or schedule is invalid
        """
        if task_id in self._tasks:
            raise ValidationError(f"Task with ID '{task_id}' already exists")

        # Validate schedule format
        if not self._is_valid_schedule(schedule):
            raise ValidationError(f"Invalid schedule format: {schedule}")

        # Create scheduled task
        scheduled_task = ScheduledTask(
            task_id=task_id,
            task_name=task_name,
            schedule=schedule,
            enabled=enabled,
            execution_count=0,
            last_execution=None,
            next_execution=""
        )

        # Store task and callback
        self._tasks[task_id] = scheduled_task
        self._task_callbacks[task_id] = callback

        # Add job to scheduler if enabled
        if enabled:
            self._add_job_to_scheduler(task_id, schedule, callback)

        self.logger.info(f"Task scheduled: {task_name} (ID: {task_id}) with schedule: {schedule}")
        return scheduled_task

    def unschedule_task(self, task_id: str) -> None:
        """
        Remove a scheduled task.

        Args:
            task_id: ID of the task to remove

        Raises:
            ValueError: If task_id does not exist
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID '{task_id}' not found")

        # Remove job from scheduler
        job = self.scheduler.get_job(task_id)
        if job:
            job.remove()

        # Remove task and callback
        del self._tasks[task_id]
        del self._task_callbacks[task_id]

        self.logger.info(f"Task unscheduled: {task_id}")

    def enable_task(self, task_id: str) -> None:
        """
        Enable a scheduled task.

        Args:
            task_id: ID of the task to enable

        Raises:
            ValueError: If task_id does not exist
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID '{task_id}' not found")

        task = self._tasks[task_id]
        if task.enabled:
            return

        task.enabled = True
        callback = self._task_callbacks[task_id]
        self._add_job_to_scheduler(task_id, task.schedule, callback)

        self.logger.info(f"Task enabled: {task_id}")

    def disable_task(self, task_id: str) -> None:
        """
        Disable a scheduled task.

        Args:
            task_id: ID of the task to disable

        Raises:
            ValueError: If task_id does not exist
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID '{task_id}' not found")

        task = self._tasks[task_id]
        if not task.enabled:
            return

        task.enabled = False
        job = self.scheduler.get_job(task_id)
        if job:
            job.remove()

        self.logger.info(f"Task disabled: {task_id}")

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """
        Get a scheduled task by ID.

        Args:
            task_id: ID of the task

        Returns:
            ScheduledTask or None if not found
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[ScheduledTask]:
        """
        Get all scheduled tasks.

        Returns:
            List of ScheduledTask objects
        """
        return list(self._tasks.values())

    def register_notification_callback(self, callback: Callable) -> None:
        """
        Register a callback for task completion notifications.

        Args:
            callback: Function to call with (task_id, success, result, error)
        """
        self._notification_callbacks.append(callback)

    def _add_job_to_scheduler(
        self,
        task_id: str,
        schedule: str,
        callback: Callable
    ) -> None:
        """
        Add a job to the APScheduler.

        Args:
            task_id: ID of the task
            schedule: Cron expression or interval string
            callback: Function to call when triggered
        """
        try:
            # Try to parse as cron expression
            if self._is_cron_expression(schedule):
                trigger = CronTrigger.from_crontab(schedule)
            else:
                # Parse as interval (e.g., "daily", "weekly", "hourly")
                trigger = self._parse_interval_trigger(schedule)

            # Create wrapper to handle execution and logging
            def job_wrapper():
                self._execute_task(task_id, callback)

            self.scheduler.add_job(
                job_wrapper,
                trigger=trigger,
                id=task_id,
                replace_existing=True
            )
        except Exception as e:
            self.logger.error(f"Failed to add job {task_id}: {str(e)}")
            raise ValidationError(f"Invalid schedule format: {schedule}")

    def _execute_task(self, task_id: str, callback: Callable) -> None:
        """
        Execute a scheduled task and log the result.

        Args:
            task_id: ID of the task
            callback: Function to execute
        """
        task = self._tasks.get(task_id)
        if not task:
            return

        start_time = datetime.now().isoformat()
        success = False
        result = None
        error = None

        try:
            # Execute the task callback
            result = callback()
            success = True
            self.logger.info(f"Task executed successfully: {task_id}")
        except Exception as e:
            error = str(e)
            self.logger.error(f"Task execution failed: {task_id} - {error}")

        # Update task execution info
        task.last_execution = start_time
        task.execution_count += 1

        # Log execution
        execution_record = {
            "task_id": task_id,
            "task_name": task.task_name,
            "timestamp": start_time,
            "success": success,
            "result": result,
            "error": error
        }
        self._execution_log.append(execution_record)

        # Notify registered callbacks
        self._notify_completion(task_id, success, result, error)

    def _notify_completion(
        self,
        task_id: str,
        success: bool,
        result: Any,
        error: Optional[str]
    ) -> None:
        """
        Notify registered callbacks of task completion.

        Args:
            task_id: ID of the completed task
            success: Whether the task succeeded
            result: Result of the task
            error: Error message if task failed
        """
        for callback in self._notification_callbacks:
            try:
                callback(task_id, success, result, error)
            except Exception as e:
                self.logger.error(f"Notification callback failed: {str(e)}")

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.

        Returns:
            List of execution records
        """
        return list(self._execution_log)

    def get_execution_log_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get execution log for a specific task.

        Args:
            task_id: ID of the task

        Returns:
            List of execution records for the task
        """
        return [record for record in self._execution_log if record["task_id"] == task_id]

    def clear_execution_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()
        self.logger.info("Execution log cleared")

    @staticmethod
    def _is_valid_schedule(schedule: str) -> bool:
        """
        Check if a schedule string is valid.

        Args:
            schedule: Schedule string to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(schedule, str) or not schedule.strip():
            return False

        # Check if it's a cron expression or interval
        if TaskScheduler._is_cron_expression(schedule):
            try:
                CronTrigger.from_crontab(schedule)
                return True
            except Exception:
                return False
        else:
            # Check if it's a valid interval
            valid_intervals = ["daily", "weekly", "hourly", "monthly"]
            return schedule.lower() in valid_intervals or schedule.startswith("interval:")

    @staticmethod
    def _is_cron_expression(schedule: str) -> bool:
        """
        Check if a schedule string is a cron expression.

        Args:
            schedule: Schedule string to check

        Returns:
            True if it looks like a cron expression, False otherwise
        """
        # Cron expressions have 5 or 6 space-separated fields
        parts = schedule.strip().split()
        return len(parts) >= 5

    @staticmethod
    def _parse_interval_trigger(schedule: str):
        """
        Parse an interval trigger from a string.

        Args:
            schedule: Interval string (e.g., "daily", "weekly", "interval:3600")

        Returns:
            IntervalTrigger object

        Raises:
            ValidationError: If schedule format is invalid
        """
        schedule_lower = schedule.lower()

        if schedule_lower == "daily":
            return IntervalTrigger(days=1)
        elif schedule_lower == "weekly":
            return IntervalTrigger(weeks=1)
        elif schedule_lower == "hourly":
            return IntervalTrigger(hours=1)
        elif schedule_lower == "monthly":
            return IntervalTrigger(days=30)
        elif schedule_lower.startswith("interval:"):
            try:
                seconds = int(schedule_lower.split(":")[1])
                return IntervalTrigger(seconds=seconds)
            except (ValueError, IndexError):
                raise ValidationError(f"Invalid interval format: {schedule}")
        else:
            raise ValidationError(f"Unknown interval type: {schedule}")
