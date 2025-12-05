"""Custom rules engine for the Lazy Automation Platform."""

import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Callable
from src.data_models import CustomRule
from src.file_service import FileService
from src.error_handler import ErrorHandler


class RulesEngine:
    """Engine for evaluating and executing custom automation rules."""

    # Supported condition types
    CONDITION_TYPES = {
        'file_type': 'Check file type',
        'file_size': 'Check file size',
        'file_age': 'Check file age',
        'file_pattern': 'Check file name pattern',
        'content_pattern': 'Check file content pattern',
    }

    # Supported action types
    ACTION_TYPES = {
        'move': 'Move file to destination',
        'rename': 'Rename file',
        'delete': 'Delete file',
        'notify': 'Send notification',
        'copy': 'Copy file to destination',
    }

    def __init__(self):
        """Initialize the RulesEngine."""
        self.execution_log: List[Dict[str, Any]] = []

    def evaluate_condition(self, condition: Dict[str, Any], file_path: str) -> bool:
        """
        Evaluate a single condition against a file.

        Args:
            condition: Condition definition with type and parameters
            file_path: Path to the file to evaluate

        Returns:
            True if condition is met, False otherwise

        Raises:
            ValueError: If condition type is not supported
        """
        if not os.path.exists(file_path):
            return False

        condition_type = condition.get('type')

        if condition_type == 'file_type':
            return self._evaluate_file_type(condition, file_path)
        elif condition_type == 'file_size':
            return self._evaluate_file_size(condition, file_path)
        elif condition_type == 'file_age':
            return self._evaluate_file_age(condition, file_path)
        elif condition_type == 'file_pattern':
            return self._evaluate_file_pattern(condition, file_path)
        elif condition_type == 'content_pattern':
            return self._evaluate_content_pattern(condition, file_path)
        else:
            raise ValueError(f"Unsupported condition type: {condition_type}")

    def _evaluate_file_type(self, condition: Dict[str, Any], file_path: str) -> bool:
        """Evaluate file type condition."""
        target_type = condition.get('value', '').lower()
        if not target_type:
            return False

        try:
            detected_type = FileService.detect_file_type(file_path)
            return detected_type == target_type
        except (FileNotFoundError, IOError):
            return False

    def _evaluate_file_size(self, condition: Dict[str, Any], file_path: str) -> bool:
        """Evaluate file size condition."""
        operator = condition.get('operator', '>')
        size_mb = condition.get('value', 0)

        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if operator == '>':
                return file_size_mb > size_mb
            elif operator == '<':
                return file_size_mb < size_mb
            elif operator == '==':
                return file_size_mb == size_mb
            elif operator == '>=':
                return file_size_mb >= size_mb
            elif operator == '<=':
                return file_size_mb <= size_mb
            else:
                return False
        except (OSError, IOError):
            return False

    def _evaluate_file_age(self, condition: Dict[str, Any], file_path: str) -> bool:
        """Evaluate file age condition."""
        operator = condition.get('operator', '>')
        days = condition.get('value', 0)

        try:
            file_mtime = os.path.getmtime(file_path)
            file_age_days = (datetime.now().timestamp() - file_mtime) / (24 * 3600)

            if operator == '>':
                return file_age_days > days
            elif operator == '<':
                return file_age_days < days
            elif operator == '==':
                return file_age_days == days
            elif operator == '>=':
                return file_age_days >= days
            elif operator == '<=':
                return file_age_days <= days
            else:
                return False
        except (OSError, IOError):
            return False

    def _evaluate_file_pattern(self, condition: Dict[str, Any], file_path: str) -> bool:
        """Evaluate file name pattern condition."""
        pattern = condition.get('value', '')
        if not pattern:
            return False

        try:
            filename = os.path.basename(file_path)
            return bool(re.search(pattern, filename))
        except re.error:
            return False

    def _evaluate_content_pattern(self, condition: Dict[str, Any], file_path: str) -> bool:
        """Evaluate file content pattern condition."""
        pattern = condition.get('value', '')
        if not pattern:
            return False

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return bool(re.search(pattern, content))
        except (IOError, OSError):
            return False

    def evaluate_all_conditions(self, conditions: Dict[str, Any], file_path: str) -> bool:
        """
        Evaluate all conditions (AND logic).

        Args:
            conditions: Dictionary of conditions
            file_path: Path to the file to evaluate

        Returns:
            True if all conditions are met, False otherwise
        """
        if not conditions:
            return True

        for condition_key, condition_value in conditions.items():
            if isinstance(condition_value, dict):
                if not self.evaluate_condition(condition_value, file_path):
                    return False
            else:
                # Handle simple condition format
                if not condition_value:
                    return False

        return True

    def execute_action(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """
        Execute a single action on a file.

        Args:
            action: Action definition with type and parameters
            file_path: Path to the file to act upon
            preview: If True, show what would happen without making changes

        Returns:
            Tuple of (success, message)

        Raises:
            ValueError: If action type is not supported
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        action_type = action.get('type')

        if action_type == 'move':
            return self._execute_move(action, file_path, preview)
        elif action_type == 'rename':
            return self._execute_rename(action, file_path, preview)
        elif action_type == 'delete':
            return self._execute_delete(action, file_path, preview)
        elif action_type == 'notify':
            return self._execute_notify(action, file_path, preview)
        elif action_type == 'copy':
            return self._execute_copy(action, file_path, preview)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    def _execute_move(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """Execute move action."""
        destination = action.get('destination', '')
        if not destination:
            return False, "Move action requires 'destination' parameter"

        try:
            if preview:
                return True, f"Would move '{file_path}' to '{destination}'"
            else:
                FileService.move_file(file_path, destination)
                return True, f"Moved '{file_path}' to '{destination}'"
        except Exception as e:
            return False, f"Failed to move file: {ErrorHandler.handle_exception(e)}"

    def _execute_rename(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """Execute rename action."""
        new_name = action.get('new_name', '')
        if not new_name:
            return False, "Rename action requires 'new_name' parameter"

        try:
            directory = os.path.dirname(file_path)
            new_path = os.path.join(directory, new_name)

            if preview:
                return True, f"Would rename '{os.path.basename(file_path)}' to '{new_name}'"
            else:
                os.rename(file_path, new_path)
                return True, f"Renamed to '{new_name}'"
        except Exception as e:
            return False, f"Failed to rename file: {ErrorHandler.handle_exception(e)}"

    def _execute_delete(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """Execute delete action."""
        try:
            if preview:
                return True, f"Would delete '{file_path}'"
            else:
                os.remove(file_path)
                return True, f"Deleted '{file_path}'"
        except Exception as e:
            return False, f"Failed to delete file: {ErrorHandler.handle_exception(e)}"

    def _execute_notify(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """Execute notify action."""
        message = action.get('message', f"Rule executed on {file_path}")

        if preview:
            return True, f"Would send notification: {message}"
        else:
            # In a real implementation, this would send a notification
            return True, f"Notification sent: {message}"

    def _execute_copy(self, action: Dict[str, Any], file_path: str, preview: bool = False) -> Tuple[bool, str]:
        """Execute copy action."""
        destination = action.get('destination', '')
        if not destination:
            return False, "Copy action requires 'destination' parameter"

        try:
            if preview:
                return True, f"Would copy '{file_path}' to '{destination}'"
            else:
                # Create destination directory if needed
                dest_dir = os.path.dirname(destination)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)

                shutil.copy2(file_path, destination)
                return True, f"Copied '{file_path}' to '{destination}'"
        except Exception as e:
            return False, f"Failed to copy file: {ErrorHandler.handle_exception(e)}"

    def execute_all_actions(self, actions: List[Dict[str, Any]], file_path: str, preview: bool = False) -> Tuple[bool, List[str]]:
        """
        Execute all actions on a file.

        Args:
            actions: List of action definitions
            file_path: Path to the file to act upon
            preview: If True, show what would happen without making changes

        Returns:
            Tuple of (all_success, list_of_messages)
        """
        messages = []
        all_success = True

        for action in actions:
            try:
                success, message = self.execute_action(action, file_path, preview)
                messages.append(message)
                if not success:
                    all_success = False
            except ValueError as e:
                messages.append(str(e))
                all_success = False

        return all_success, messages

    def apply_rule(self, rule: CustomRule, directory: str, preview: bool = False) -> Dict[str, Any]:
        """
        Apply a rule to all files in a directory.

        Args:
            rule: CustomRule to apply
            directory: Directory to apply rule to
            preview: If True, show what would happen without making changes

        Returns:
            Dictionary with execution results

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        results = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'preview': preview,
            'timestamp': datetime.now().isoformat(),
            'matched_files': [],
            'executed_actions': [],
            'errors': [],
            'total_matched': 0,
            'total_executed': 0,
            'total_errors': 0,
        }

        # Walk through directory and apply rule
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    # Check if conditions are met
                    if self.evaluate_all_conditions(rule.conditions, file_path):
                        results['matched_files'].append(file_path)
                        results['total_matched'] += 1

                        # Execute actions
                        success, messages = self.execute_all_actions(rule.actions, file_path, preview)

                        if success:
                            results['executed_actions'].append({
                                'file': file_path,
                                'messages': messages,
                            })
                            results['total_executed'] += 1
                        else:
                            results['errors'].append({
                                'file': file_path,
                                'messages': messages,
                            })
                            results['total_errors'] += 1

                except Exception as e:
                    results['errors'].append({
                        'file': file_path,
                        'messages': [ErrorHandler.handle_exception(e)],
                    })
                    results['total_errors'] += 1

        # Log the execution
        self._log_execution(results)

        # Increment execution count
        if not preview:
            rule.execution_count += 1

        return results

    def _log_execution(self, results: Dict[str, Any]) -> None:
        """
        Log rule execution details.

        Args:
            results: Execution results to log
        """
        log_entry = {
            'timestamp': results['timestamp'],
            'rule_id': results['rule_id'],
            'rule_name': results['rule_name'],
            'preview': results['preview'],
            'total_matched': results['total_matched'],
            'total_executed': results['total_executed'],
            'total_errors': results['total_errors'],
        }

        self.execution_log.append(log_entry)

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.

        Returns:
            List of execution log entries
        """
        return self.execution_log.copy()

    def clear_execution_log(self) -> None:
        """Clear the execution log."""
        self.execution_log.clear()

    def validate_rule(self, rule: CustomRule) -> Tuple[bool, str]:
        """
        Validate a rule definition.

        Args:
            rule: CustomRule to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not rule.conditions:
            return False, "Rule must have at least one condition"

        if not rule.actions:
            return False, "Rule must have at least one action"

        # Validate conditions
        for condition_key, condition_value in rule.conditions.items():
            if isinstance(condition_value, dict):
                condition_type = condition_value.get('type')
                if condition_type not in self.CONDITION_TYPES:
                    return False, f"Unknown condition type: {condition_type}"

        # Validate actions
        for action in rule.actions:
            if not isinstance(action, dict):
                return False, "Each action must be a dictionary"

            action_type = action.get('type')
            if action_type not in self.ACTION_TYPES:
                return False, f"Unknown action type: {action_type}"

        return True, ""
