"""Sandbox mode execution for preview-only automation tasks."""

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from uuid import uuid4

from src.data_models import ValidationError


@dataclass
class SandboxExecution:
    """Result of a sandbox mode execution."""

    execution_id: str
    automation_id: str
    timestamp: str
    changes: List[Dict[str, Any]]  # List of changes that would be made
    affected_files: List[str]  # Files that would be affected
    success: bool
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate the execution after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the SandboxExecution."""
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValidationError("execution_id must be a non-empty string")
        if not isinstance(self.automation_id, str) or not self.automation_id.strip():
            raise ValidationError("automation_id must be a non-empty string")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValidationError("timestamp must be a non-empty string")
        if not isinstance(self.changes, list):
            raise ValidationError("changes must be a list")
        if not isinstance(self.affected_files, list):
            raise ValidationError("affected_files must be a list")
        if not isinstance(self.success, bool):
            raise ValidationError("success must be a boolean")


class SandboxExecutor:
    """Executes automations in sandbox mode without making actual changes."""

    def __init__(self, sandbox_root_dir: str = "data/sandbox"):
        """
        Initialize the SandboxExecutor.

        Args:
            sandbox_root_dir: Root directory for sandbox executions
        """
        self.sandbox_root_dir = sandbox_root_dir
        os.makedirs(sandbox_root_dir, exist_ok=True)

    def execute_in_sandbox(
        self,
        automation_id: str,
        automation_func,
        *args,
        **kwargs
    ) -> Tuple[bool, str, Optional[SandboxExecution]]:
        """
        Execute an automation in sandbox mode.

        Args:
            automation_id: ID of the automation task
            automation_func: The automation function to execute
            *args: Positional arguments for the automation function
            **kwargs: Keyword arguments for the automation function

        Returns:
            Tuple of (success, message, sandbox_execution)
        """
        if not automation_id or not isinstance(automation_id, str):
            return False, "automation_id must be a non-empty string", None

        if not callable(automation_func):
            return False, "automation_func must be callable", None

        execution_id = str(uuid4())
        sandbox_dir = os.path.join(self.sandbox_root_dir, execution_id)

        try:
            os.makedirs(sandbox_dir, exist_ok=True)

            # Create a temporary copy of affected files for simulation
            affected_files = []
            changes = []

            # Execute the automation function with sandbox context
            # The function should return (success, changes, affected_files)
            result = automation_func(
                sandbox_mode=True,
                sandbox_dir=sandbox_dir,
                *args,
                **kwargs
            )

            if isinstance(result, tuple) and len(result) >= 3:
                success, changes, affected_files = result[0], result[1], result[2]
            else:
                success = result if isinstance(result, bool) else True
                changes = []
                affected_files = []

            # Create sandbox execution record
            execution = SandboxExecution(
                execution_id=execution_id,
                automation_id=automation_id,
                timestamp=datetime.now().isoformat(),
                changes=changes,
                affected_files=affected_files,
                success=success
            )

            return True, f"Sandbox execution completed: {execution_id}", execution

        except Exception as e:
            # Clean up sandbox directory
            if os.path.exists(sandbox_dir):
                shutil.rmtree(sandbox_dir)
            return False, f"Sandbox execution failed: {str(e)}", None

    def apply_sandbox_changes(
        self,
        execution_id: str,
        automation_func,
        *args,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Apply changes from a sandbox execution to the actual system.

        Args:
            execution_id: ID of the sandbox execution
            automation_func: The automation function to execute for real
            *args: Positional arguments for the automation function
            **kwargs: Keyword arguments for the automation function

        Returns:
            Tuple of (success, message)
        """
        if not execution_id or not isinstance(execution_id, str):
            return False, "execution_id must be a non-empty string"

        if not callable(automation_func):
            return False, "automation_func must be callable"

        sandbox_dir = os.path.join(self.sandbox_root_dir, execution_id)

        if not os.path.exists(sandbox_dir):
            return False, f"Sandbox execution not found: {execution_id}"

        try:
            # Execute the automation function for real (not in sandbox mode)
            result = automation_func(
                sandbox_mode=False,
                sandbox_dir=sandbox_dir,
                *args,
                **kwargs
            )

            # Clean up sandbox directory after successful application
            if os.path.exists(sandbox_dir):
                shutil.rmtree(sandbox_dir)

            return True, f"Changes applied successfully from sandbox: {execution_id}"

        except Exception as e:
            return False, f"Failed to apply sandbox changes: {str(e)}"

    def discard_sandbox_execution(self, execution_id: str) -> Tuple[bool, str]:
        """
        Discard a sandbox execution and clean up.

        Args:
            execution_id: ID of the sandbox execution to discard

        Returns:
            Tuple of (success, message)
        """
        if not execution_id or not isinstance(execution_id, str):
            return False, "execution_id must be a non-empty string"

        sandbox_dir = os.path.join(self.sandbox_root_dir, execution_id)

        if not os.path.exists(sandbox_dir):
            return False, f"Sandbox execution not found: {execution_id}"

        try:
            shutil.rmtree(sandbox_dir)
            return True, f"Sandbox execution discarded: {execution_id}"
        except Exception as e:
            return False, f"Failed to discard sandbox execution: {str(e)}"

    def get_sandbox_changes(self, execution_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get the changes that would be made by a sandbox execution.

        Args:
            execution_id: ID of the sandbox execution

        Returns:
            List of changes or None if execution not found
        """
        sandbox_dir = os.path.join(self.sandbox_root_dir, execution_id)

        if not os.path.exists(sandbox_dir):
            return None

        # Read changes from sandbox execution metadata
        changes_file = os.path.join(sandbox_dir, "changes.json")
        if os.path.exists(changes_file):
            import json
            try:
                with open(changes_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []

        return []

    def cleanup_old_sandboxes(self, max_age_hours: int = 24) -> Tuple[int, str]:
        """
        Clean up old sandbox executions.

        Args:
            max_age_hours: Maximum age of sandbox executions to keep

        Returns:
            Tuple of (deleted_count, message)
        """
        if max_age_hours <= 0:
            return 0, "max_age_hours must be greater than 0"

        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        try:
            for execution_id in os.listdir(self.sandbox_root_dir):
                sandbox_dir = os.path.join(self.sandbox_root_dir, execution_id)

                if os.path.isdir(sandbox_dir):
                    dir_age = current_time - os.path.getmtime(sandbox_dir)

                    if dir_age > max_age_seconds:
                        shutil.rmtree(sandbox_dir)
                        deleted_count += 1

            return deleted_count, f"Deleted {deleted_count} old sandbox executions"

        except Exception as e:
            return 0, f"Failed to cleanup sandboxes: {str(e)}"
