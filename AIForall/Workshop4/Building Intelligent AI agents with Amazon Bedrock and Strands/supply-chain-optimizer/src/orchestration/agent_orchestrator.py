"""Agent orchestration and communication patterns."""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.config import logger
from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.supplier_coordination_agent import SupplierCoordinationAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent


class ExecutionPattern(Enum):
    """Execution patterns for agent workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class AgentTask:
    """Represents a task to be executed by an agent."""
    task_id: str
    agent_type: str  # Type of agent (forecasting, optimization, etc.)
    operation: str  # Operation to perform
    inputs: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None  # Conditional execution
    retry_count: int = 3
    timeout_seconds: int = 300


@dataclass
class ExecutionResult:
    """Result of a task execution."""
    task_id: str
    status: str  # success, error, skipped
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AgentOrchestrator:
    """Orchestrates agent execution with support for different communication patterns."""

    def __init__(self):
        """Initialize the Agent Orchestrator."""
        self.logger = logger
        self.agents = {
            "forecasting": DemandForecastingAgent(),
            "optimization": InventoryOptimizerAgent(),
            "supplier_coordination": SupplierCoordinationAgent(),
            "anomaly_detection": AnomalyDetectionAgent(),
            "report_generation": ReportGenerationAgent(),
        }
        self.execution_history: Dict[str, ExecutionResult] = {}

    def execute_sequential(
        self,
        tasks: List[AgentTask]
    ) -> Dict[str, ExecutionResult]:
        """Execute tasks sequentially, passing outputs to next task.

        Args:
            tasks: List of tasks to execute in order

        Returns:
            Dictionary mapping task IDs to execution results
        """
        results = {}
        
        for task in tasks:
            try:
                # Check if task has dependencies
                if task.dependencies:
                    # Verify all dependencies completed successfully
                    for dep_id in task.dependencies:
                        if dep_id not in results:
                            raise ValueError(f"Dependency {dep_id} not found in results")
                        if results[dep_id].status != "success":
                            raise ValueError(f"Dependency {dep_id} failed")
                        
                        # Pass previous task output as input to current task
                        task.inputs.update(results[dep_id].output or {})
                
                # Execute the task
                result = self._execute_task(task)
                results[task.task_id] = result
                
                self.logger.info(
                    f"Sequential execution: Task {task.task_id} completed with status {result.status}"
                )
            except Exception as e:
                self.logger.error(f"Sequential execution failed for task {task.task_id}: {str(e)}")
                results[task.task_id] = ExecutionResult(
                    task_id=task.task_id,
                    status="error",
                    error=str(e)
                )
        
        return results

    def execute_parallel(
        self,
        tasks: List[AgentTask]
    ) -> Dict[str, ExecutionResult]:
        """Execute tasks in parallel.

        Args:
            tasks: List of tasks to execute in parallel

        Returns:
            Dictionary mapping task IDs to execution results
        """
        results = {}
        
        # Create tasks for asyncio
        async_tasks = []
        for task in tasks:
            async_tasks.append(self._execute_task_async(task))
        
        # Run all tasks concurrently
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            execution_results = loop.run_until_complete(
                asyncio.gather(*async_tasks, return_exceptions=True)
            )
            loop.close()
            
            # Map results back to task IDs
            for task, result in zip(tasks, execution_results):
                if isinstance(result, Exception):
                    results[task.task_id] = ExecutionResult(
                        task_id=task.task_id,
                        status="error",
                        error=str(result)
                    )
                else:
                    results[task.task_id] = result
                
                self.logger.info(
                    f"Parallel execution: Task {task.task_id} completed with status {results[task.task_id].status}"
                )
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {str(e)}")
            for task in tasks:
                results[task.task_id] = ExecutionResult(
                    task_id=task.task_id,
                    status="error",
                    error=str(e)
                )
        
        return results

    def execute_conditional(
        self,
        tasks: List[AgentTask],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ExecutionResult]:
        """Execute tasks with conditional logic.

        Args:
            tasks: List of tasks with optional conditions
            context: Context data for evaluating conditions

        Returns:
            Dictionary mapping task IDs to execution results
        """
        results = {}
        context = context or {}
        
        for task in tasks:
            try:
                # Check if task should be executed based on condition
                if task.condition:
                    if not task.condition(context):
                        self.logger.info(f"Conditional execution: Task {task.task_id} skipped (condition not met)")
                        results[task.task_id] = ExecutionResult(
                            task_id=task.task_id,
                            status="skipped"
                        )
                        continue
                
                # Check dependencies
                if task.dependencies:
                    for dep_id in task.dependencies:
                        if dep_id not in results:
                            raise ValueError(f"Dependency {dep_id} not found")
                        if results[dep_id].status not in ["success", "skipped"]:
                            raise ValueError(f"Dependency {dep_id} failed")
                        
                        # Pass previous output to current task
                        if results[dep_id].output:
                            task.inputs.update(results[dep_id].output)
                
                # Execute the task
                result = self._execute_task(task)
                results[task.task_id] = result
                
                # Update context with result for next conditional checks
                if result.output:
                    context[task.task_id] = result.output
                
                self.logger.info(
                    f"Conditional execution: Task {task.task_id} completed with status {result.status}"
                )
            except Exception as e:
                self.logger.error(f"Conditional execution failed for task {task.task_id}: {str(e)}")
                results[task.task_id] = ExecutionResult(
                    task_id=task.task_id,
                    status="error",
                    error=str(e)
                )
        
        return results

    def execute_workflow(
        self,
        tasks: List[AgentTask],
        pattern: ExecutionPattern = ExecutionPattern.SEQUENTIAL,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ExecutionResult]:
        """Execute a workflow with specified pattern.

        Args:
            tasks: List of tasks to execute
            pattern: Execution pattern (sequential, parallel, conditional)
            context: Context data for conditional execution

        Returns:
            Dictionary mapping task IDs to execution results
        """
        self.logger.info(f"Starting workflow execution with pattern: {pattern.value}")
        
        if pattern == ExecutionPattern.SEQUENTIAL:
            results = self.execute_sequential(tasks)
        elif pattern == ExecutionPattern.PARALLEL:
            results = self.execute_parallel(tasks)
        elif pattern == ExecutionPattern.CONDITIONAL:
            results = self.execute_conditional(tasks, context)
        else:
            raise ValueError(f"Unknown execution pattern: {pattern}")
        
        # Store execution history
        self.execution_history.update(results)
        
        # Log summary
        success_count = sum(1 for r in results.values() if r.status == "success")
        error_count = sum(1 for r in results.values() if r.status == "error")
        skipped_count = sum(1 for r in results.values() if r.status == "skipped")
        
        self.logger.info(
            f"Workflow execution completed: {success_count} succeeded, "
            f"{error_count} failed, {skipped_count} skipped"
        )
        
        return results

    def _execute_task(self, task: AgentTask) -> ExecutionResult:
        """Execute a single task.

        Args:
            task: Task to execute

        Returns:
            Execution result
        """
        import time
        start_time = time.time()
        
        try:
            agent = self.agents.get(task.agent_type)
            if not agent:
                raise ValueError(f"Unknown agent type: {task.agent_type}")
            
            # Execute the operation on the agent
            output = self._call_agent_operation(agent, task.operation, task.inputs)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                task_id=task.task_id,
                status="success",
                output=output,
                execution_time_ms=execution_time_ms
            )
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Task execution failed: {str(e)}")
            
            return ExecutionResult(
                task_id=task.task_id,
                status="error",
                error=str(e),
                execution_time_ms=execution_time_ms
            )

    async def _execute_task_async(self, task: AgentTask) -> ExecutionResult:
        """Execute a task asynchronously.

        Args:
            task: Task to execute

        Returns:
            Execution result
        """
        return self._execute_task(task)

    def _call_agent_operation(
        self,
        agent: Any,
        operation: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an operation on an agent.

        Args:
            agent: Agent instance
            operation: Operation name
            inputs: Operation inputs

        Returns:
            Operation output
        """
        # Get the method from the agent
        method = getattr(agent, operation, None)
        if not method:
            raise ValueError(f"Agent does not have operation: {operation}")
        
        # Call the method with inputs
        return method(**inputs)

    def get_execution_history(self) -> Dict[str, ExecutionResult]:
        """Get execution history.

        Returns:
            Dictionary of execution results
        """
        return self.execution_history

    def clear_execution_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
        self.logger.info("Execution history cleared")
