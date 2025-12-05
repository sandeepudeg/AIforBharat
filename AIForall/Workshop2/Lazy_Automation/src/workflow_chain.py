"""Workflow chaining system for combining multiple automation tasks."""

import logging
from typing import Callable, Dict, Any, Optional, List, Tuple
from datetime import datetime
from src.data_models import WorkflowChain, ValidationError


class WorkflowChainEngine:
    """Manages creation and execution of workflow chains."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the WorkflowChainEngine.

        Args:
            config_dir: Directory for storing workflow state
        """
        self.config_dir = config_dir
        self._chains: Dict[str, WorkflowChain] = {}
        self._task_registry: Dict[str, Callable] = {}
        self._execution_log: List[Dict[str, Any]] = []
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Only add file handler if not already present
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            try:
                handler = logging.FileHandler(f"{config_dir}/workflow.log", encoding='utf-8')
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except (OSError, IOError):
                # If file handler fails, just use console logging
                pass

    def register_task(self, task_id: str, task_callback: Callable) -> None:
        """
        Register an automation task that can be used in workflows.

        Args:
            task_id: Unique identifier for the task
            task_callback: Function to call when task is executed

        Raises:
            ValidationError: If task_id is invalid
        """
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValidationError("task_id must be a non-empty string")
        
        self._task_registry[task_id] = task_callback
        self.logger.info(f"Task registered: {task_id}")

    def unregister_task(self, task_id: str) -> None:
        """
        Unregister an automation task.

        Args:
            task_id: ID of the task to unregister

        Raises:
            ValueError: If task_id does not exist
        """
        if task_id not in self._task_registry:
            raise ValueError(f"Task with ID '{task_id}' not found")
        
        del self._task_registry[task_id]
        self.logger.info(f"Task unregistered: {task_id}")

    def create_chain(
        self,
        chain_id: str,
        name: str,
        tasks: List[str],
        enabled: bool = True
    ) -> WorkflowChain:
        """
        Create a new workflow chain.

        Args:
            chain_id: Unique identifier for the chain
            name: Human-readable name for the chain
            tasks: Ordered list of task IDs to execute
            enabled: Whether the chain is enabled

        Returns:
            WorkflowChain object

        Raises:
            ValidationError: If chain_id already exists or tasks are invalid
        """
        if chain_id in self._chains:
            raise ValidationError(f"Chain with ID '{chain_id}' already exists")
        
        if not tasks:
            raise ValidationError("tasks list cannot be empty")
        
        # Verify all tasks are registered
        for task_id in tasks:
            if task_id not in self._task_registry:
                raise ValidationError(f"Task '{task_id}' is not registered")
        
        # Create workflow chain
        chain = WorkflowChain(
            chain_id=chain_id,
            name=name,
            tasks=tasks,
            enabled=enabled,
            created_at=datetime.now().isoformat(),
            last_executed=None
        )
        
        self._chains[chain_id] = chain
        self.logger.info(f"Workflow chain created: {name} (ID: {chain_id}) with {len(tasks)} tasks")
        return chain

    def delete_chain(self, chain_id: str) -> None:
        """
        Delete a workflow chain.

        Args:
            chain_id: ID of the chain to delete

        Raises:
            ValueError: If chain_id does not exist
        """
        if chain_id not in self._chains:
            raise ValueError(f"Chain with ID '{chain_id}' not found")
        
        del self._chains[chain_id]
        self.logger.info(f"Workflow chain deleted: {chain_id}")

    def get_chain(self, chain_id: str) -> Optional[WorkflowChain]:
        """
        Get a workflow chain by ID.

        Args:
            chain_id: ID of the chain

        Returns:
            WorkflowChain or None if not found
        """
        return self._chains.get(chain_id)

    def get_all_chains(self) -> List[WorkflowChain]:
        """
        Get all workflow chains.

        Returns:
            List of WorkflowChain objects
        """
        return list(self._chains.values())

    def enable_chain(self, chain_id: str) -> None:
        """
        Enable a workflow chain.

        Args:
            chain_id: ID of the chain to enable

        Raises:
            ValueError: If chain_id does not exist
        """
        if chain_id not in self._chains:
            raise ValueError(f"Chain with ID '{chain_id}' not found")
        
        self._chains[chain_id].enabled = True
        self.logger.info(f"Workflow chain enabled: {chain_id}")

    def disable_chain(self, chain_id: str) -> None:
        """
        Disable a workflow chain.

        Args:
            chain_id: ID of the chain to disable

        Raises:
            ValueError: If chain_id does not exist
        """
        if chain_id not in self._chains:
            raise ValueError(f"Chain with ID '{chain_id}' not found")
        
        self._chains[chain_id].enabled = False
        self.logger.info(f"Workflow chain disabled: {chain_id}")

    def execute_chain(self, chain_id: str) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute a workflow chain.

        Args:
            chain_id: ID of the chain to execute

        Returns:
            Tuple of (success, result, error_message)
            - success: True if all tasks completed successfully
            - result: Final output from the last task
            - error_message: Error message if a task failed

        Raises:
            ValueError: If chain_id does not exist
        """
        if chain_id not in self._chains:
            raise ValueError(f"Chain with ID '{chain_id}' not found")
        
        chain = self._chains[chain_id]
        
        if not chain.enabled:
            error_msg = f"Workflow chain '{chain_id}' is disabled"
            self.logger.warning(error_msg)
            return False, None, error_msg
        
        start_time = datetime.now().isoformat()
        current_input = None
        success = False
        error_message = None
        failed_task_id = None
        
        try:
            # Execute each task in sequence
            for task_id in chain.tasks:
                try:
                    task_callback = self._task_registry[task_id]
                    
                    # Execute task with current input
                    if current_input is None:
                        current_input = task_callback()
                    else:
                        current_input = task_callback(current_input)
                    
                    self.logger.info(f"Task executed in chain: {task_id}")
                
                except Exception as e:
                    error_message = f"Task '{task_id}' failed: {str(e)}"
                    failed_task_id = task_id
                    self.logger.error(error_message)
                    break
            
            # If no error occurred, mark as success
            if error_message is None:
                success = True
                self.logger.info(f"Workflow chain executed successfully: {chain_id}")
        
        except Exception as e:
            error_message = f"Workflow chain execution failed: {str(e)}"
            self.logger.error(error_message)
        
        # Update chain execution info
        chain.last_executed = start_time
        
        # Log execution
        execution_record = {
            "chain_id": chain_id,
            "chain_name": chain.name,
            "timestamp": start_time,
            "success": success,
            "result": current_input,
            "error": error_message,
            "failed_task": failed_task_id,
            "tasks_executed": chain.tasks[:chain.tasks.index(failed_task_id) + 1] if failed_task_id else chain.tasks
        }
        self._execution_log.append(execution_record)
        
        return success, current_input, error_message

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.

        Returns:
            List of execution records
        """
        return list(self._execution_log)

    def get_execution_log_for_chain(self, chain_id: str) -> List[Dict[str, Any]]:
        """
        Get execution log for a specific chain.

        Args:
            chain_id: ID of the chain

        Returns:
            List of execution records for the chain
        """
        return [record for record in self._execution_log if record["chain_id"] == chain_id]

    def clear_execution_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()
        self.logger.info("Execution log cleared")
