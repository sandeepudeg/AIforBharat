"""Event trigger system for monitoring and executing automations based on trigger events."""

import logging
import os
import time
from typing import Callable, Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path
from src.data_models import ValidationError


class TriggerType(Enum):
    """Types of triggers supported by the system."""
    NEW_EMAIL = "new_email"
    FILE_ADDED = "file_added"
    TIME_BASED = "time_based"


class Trigger:
    """Represents a trigger configuration."""

    def __init__(
        self,
        trigger_id: str,
        trigger_type: TriggerType,
        automation_id: str,
        config: Dict[str, Any],
        enabled: bool = True
    ):
        """
        Initialize a Trigger.

        Args:
            trigger_id: Unique identifier for the trigger
            trigger_type: Type of trigger (NEW_EMAIL, FILE_ADDED, TIME_BASED)
            automation_id: ID of the automation to execute when triggered
            config: Configuration specific to the trigger type
            enabled: Whether the trigger is enabled
        """
        self.trigger_id = trigger_id
        self.trigger_type = trigger_type
        self.automation_id = automation_id
        self.config = config
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
        self.last_triggered = None
        self.trigger_count = 0

    def validate(self) -> None:
        """Validate the trigger configuration."""
        if not isinstance(self.trigger_id, str) or not self.trigger_id.strip():
            raise ValidationError("trigger_id must be a non-empty string")
        if not isinstance(self.automation_id, str) or not self.automation_id.strip():
            raise ValidationError("automation_id must be a non-empty string")
        if not isinstance(self.config, dict):
            raise ValidationError("config must be a dictionary")
        if not isinstance(self.enabled, bool):
            raise ValidationError("enabled must be a boolean")


class TriggerManager:
    """Manages trigger creation, monitoring, and execution."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the TriggerManager.

        Args:
            config_dir: Directory for storing trigger state
        """
        self.config_dir = config_dir
        self._triggers: Dict[str, Trigger] = {}
        self._automation_callbacks: Dict[str, Callable] = {}
        self._execution_log: List[Dict[str, Any]] = []
        self._file_watchers: Dict[str, float] = {}  # Track file modification times
        self._monitoring = False

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Only add file handler if not already present
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            try:
                handler = logging.FileHandler(f"{config_dir}/trigger.log", encoding='utf-8')
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except (OSError, IOError):
                # If file handler fails, just use console logging
                pass

    def register_automation(self, automation_id: str, callback: Callable) -> None:
        """
        Register an automation that can be triggered.

        Args:
            automation_id: Unique identifier for the automation
            callback: Function to call when automation is triggered

        Raises:
            ValidationError: If automation_id is invalid
        """
        if not isinstance(automation_id, str) or not automation_id.strip():
            raise ValidationError("automation_id must be a non-empty string")

        self._automation_callbacks[automation_id] = callback
        self.logger.info(f"Automation registered: {automation_id}")

    def unregister_automation(self, automation_id: str) -> None:
        """
        Unregister an automation.

        Args:
            automation_id: ID of the automation to unregister

        Raises:
            ValueError: If automation_id does not exist
        """
        if automation_id not in self._automation_callbacks:
            raise ValueError(f"Automation with ID '{automation_id}' not found")

        del self._automation_callbacks[automation_id]
        self.logger.info(f"Automation unregistered: {automation_id}")

    def create_trigger(
        self,
        trigger_id: str,
        trigger_type: str,
        automation_id: str,
        config: Dict[str, Any],
        enabled: bool = True
    ) -> Trigger:
        """
        Create a new trigger.

        Args:
            trigger_id: Unique identifier for the trigger
            trigger_type: Type of trigger ("new_email", "file_added", "time_based")
            automation_id: ID of the automation to execute
            config: Configuration specific to the trigger type
            enabled: Whether the trigger is enabled

        Returns:
            Trigger object

        Raises:
            ValidationError: If trigger_id already exists or parameters are invalid
        """
        if trigger_id in self._triggers:
            raise ValidationError(f"Trigger with ID '{trigger_id}' already exists")

        if automation_id not in self._automation_callbacks:
            raise ValidationError(f"Automation '{automation_id}' is not registered")

        # Validate trigger type
        try:
            trigger_type_enum = TriggerType(trigger_type)
        except ValueError:
            raise ValidationError(f"Invalid trigger type: {trigger_type}")

        # Validate trigger-specific config
        self._validate_trigger_config(trigger_type_enum, config)

        # Create trigger
        trigger = Trigger(
            trigger_id=trigger_id,
            trigger_type=trigger_type_enum,
            automation_id=automation_id,
            config=config,
            enabled=enabled
        )

        trigger.validate()
        self._triggers[trigger_id] = trigger

        self.logger.info(
            f"Trigger created: {trigger_id} (type: {trigger_type}, automation: {automation_id})"
        )

        return trigger

    def delete_trigger(self, trigger_id: str) -> None:
        """
        Delete a trigger.

        Args:
            trigger_id: ID of the trigger to delete

        Raises:
            ValueError: If trigger_id does not exist
        """
        if trigger_id not in self._triggers:
            raise ValueError(f"Trigger with ID '{trigger_id}' not found")

        del self._triggers[trigger_id]
        self.logger.info(f"Trigger deleted: {trigger_id}")

    def enable_trigger(self, trigger_id: str) -> None:
        """
        Enable a trigger.

        Args:
            trigger_id: ID of the trigger to enable

        Raises:
            ValueError: If trigger_id does not exist
        """
        if trigger_id not in self._triggers:
            raise ValueError(f"Trigger with ID '{trigger_id}' not found")

        trigger = self._triggers[trigger_id]
        if trigger.enabled:
            return

        trigger.enabled = True
        self.logger.info(f"Trigger enabled: {trigger_id}")

    def disable_trigger(self, trigger_id: str) -> None:
        """
        Disable a trigger.

        Args:
            trigger_id: ID of the trigger to disable

        Raises:
            ValueError: If trigger_id does not exist
        """
        if trigger_id not in self._triggers:
            raise ValueError(f"Trigger with ID '{trigger_id}' not found")

        trigger = self._triggers[trigger_id]
        if not trigger.enabled:
            return

        trigger.enabled = False
        self.logger.info(f"Trigger disabled: {trigger_id}")

    def get_trigger(self, trigger_id: str) -> Optional[Trigger]:
        """
        Get a trigger by ID.

        Args:
            trigger_id: ID of the trigger

        Returns:
            Trigger or None if not found
        """
        return self._triggers.get(trigger_id)

    def get_all_triggers(self) -> List[Trigger]:
        """
        Get all triggers.

        Returns:
            List of Trigger objects
        """
        return list(self._triggers.values())

    def get_triggers_for_automation(self, automation_id: str) -> List[Trigger]:
        """
        Get all triggers for a specific automation.

        Args:
            automation_id: ID of the automation

        Returns:
            List of Trigger objects
        """
        return [t for t in self._triggers.values() if t.automation_id == automation_id]

    def check_triggers(self) -> Tuple[int, List[str]]:
        """
        Check all triggers for events and execute automations if triggered.

        Returns:
            Tuple of (triggered_count, list of triggered_trigger_ids)
        """
        triggered_count = 0
        triggered_ids = []

        for trigger_id, trigger in self._triggers.items():
            if not trigger.enabled:
                continue

            # Check if trigger event occurred
            if self._check_trigger_event(trigger):
                # Execute the associated automation
                success = self._execute_trigger(trigger)
                if success:
                    triggered_count += 1
                    triggered_ids.append(trigger_id)

        return triggered_count, triggered_ids

    def _check_trigger_event(self, trigger: Trigger) -> bool:
        """
        Check if a trigger event has occurred.

        Args:
            trigger: Trigger to check

        Returns:
            True if trigger event occurred, False otherwise
        """
        try:
            if trigger.trigger_type == TriggerType.FILE_ADDED:
                return self._check_file_added_trigger(trigger)
            elif trigger.trigger_type == TriggerType.NEW_EMAIL:
                return self._check_new_email_trigger(trigger)
            elif trigger.trigger_type == TriggerType.TIME_BASED:
                return self._check_time_based_trigger(trigger)
        except Exception as e:
            self.logger.error(f"Error checking trigger {trigger.trigger_id}: {str(e)}")

        return False

    def _check_file_added_trigger(self, trigger: Trigger) -> bool:
        """
        Check if a file has been added to the monitored directory.

        Args:
            trigger: FILE_ADDED trigger to check

        Returns:
            True if new file detected, False otherwise
        """
        watch_path = trigger.config.get("watch_path")
        if not watch_path or not os.path.isdir(watch_path):
            return False

        # Get current files in directory
        try:
            current_files = set(os.listdir(watch_path))
        except OSError:
            return False

        # Get previously seen files
        previous_files = set(trigger.config.get("previous_files", []))

        # Check for new files
        new_files = current_files - previous_files

        if new_files:
            # Update the previous files list
            trigger.config["previous_files"] = list(current_files)
            return True

        return False

    def _check_new_email_trigger(self, trigger: Trigger) -> bool:
        """
        Check if new emails have arrived.

        Args:
            trigger: NEW_EMAIL trigger to check

        Returns:
            True if new emails detected, False otherwise
        """
        # This is a placeholder implementation
        # In a real system, this would check an email service
        # For now, we'll use a simple flag-based approach
        check_flag = trigger.config.get("check_flag", False)
        if check_flag:
            trigger.config["check_flag"] = False
            return True

        return False

    def _check_time_based_trigger(self, trigger: Trigger) -> bool:
        """
        Check if a time-based trigger should fire.

        Args:
            trigger: TIME_BASED trigger to check

        Returns:
            True if trigger should fire, False otherwise
        """
        # This is a placeholder implementation
        # In a real system, this would check against scheduled times
        # For now, we'll use a simple flag-based approach
        check_flag = trigger.config.get("check_flag", False)
        if check_flag:
            trigger.config["check_flag"] = False
            return True

        return False

    def _execute_trigger(self, trigger: Trigger) -> bool:
        """
        Execute the automation associated with a trigger.

        Args:
            trigger: Trigger to execute

        Returns:
            True if execution was successful, False otherwise
        """
        automation_id = trigger.automation_id
        callback = self._automation_callbacks.get(automation_id)

        if not callback:
            self.logger.error(f"Automation callback not found: {automation_id}")
            return False

        start_time = datetime.now().isoformat()
        success = False
        result = None
        error = None

        try:
            # Execute the automation
            result = callback()
            success = True
            self.logger.info(f"Trigger executed successfully: {trigger.trigger_id}")
        except Exception as e:
            error = str(e)
            self.logger.error(f"Trigger execution failed: {trigger.trigger_id} - {error}")

        # Update trigger info
        trigger.last_triggered = start_time
        trigger.trigger_count += 1

        # Log execution
        execution_record = {
            "trigger_id": trigger.trigger_id,
            "trigger_type": trigger.trigger_type.value,
            "automation_id": automation_id,
            "timestamp": start_time,
            "success": success,
            "result": result,
            "error": error
        }
        self._execution_log.append(execution_record)

        return success

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.

        Returns:
            List of execution records
        """
        return list(self._execution_log)

    def get_execution_log_for_trigger(self, trigger_id: str) -> List[Dict[str, Any]]:
        """
        Get execution log for a specific trigger.

        Args:
            trigger_id: ID of the trigger

        Returns:
            List of execution records for the trigger
        """
        return [record for record in self._execution_log if record["trigger_id"] == trigger_id]

    def clear_execution_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()
        self.logger.info("Execution log cleared")

    @staticmethod
    def _validate_trigger_config(trigger_type: TriggerType, config: Dict[str, Any]) -> None:
        """
        Validate trigger-specific configuration.

        Args:
            trigger_type: Type of trigger
            config: Configuration to validate

        Raises:
            ValidationError: If configuration is invalid
        """
        if trigger_type == TriggerType.FILE_ADDED:
            if "watch_path" not in config:
                raise ValidationError("FILE_ADDED trigger requires 'watch_path' in config")
            if not isinstance(config["watch_path"], str):
                raise ValidationError("watch_path must be a string")

        elif trigger_type == TriggerType.NEW_EMAIL:
            # NEW_EMAIL trigger can have optional email configuration
            pass

        elif trigger_type == TriggerType.TIME_BASED:
            # TIME_BASED trigger can have optional time configuration
            pass
