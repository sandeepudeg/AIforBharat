# Agent Orchestration and Communication

## Overview

The Agent Orchestration module provides a flexible framework for coordinating the execution of multiple AI agents with support for different communication patterns. It enables complex workflows where agents can execute sequentially, in parallel, or conditionally based on runtime conditions.

## Architecture

### Core Components

1. **AgentOrchestrator**: Main orchestration engine that manages agent execution
2. **AgentTask**: Represents a task to be executed by an agent
3. **ExecutionResult**: Captures the result of a task execution
4. **ExecutionPattern**: Enum defining execution patterns (sequential, parallel, conditional)

### Execution Patterns

#### Sequential Execution
Tasks execute one after another, with outputs from previous tasks passed as inputs to subsequent tasks. Useful for workflows where each step depends on the previous one.

```python
orchestrator = AgentOrchestrator()
tasks = [
    AgentTask(task_id="forecast", agent_type="forecasting", operation="generate_forecast", inputs={"sku": "SKU-001"}),
    AgentTask(task_id="optimize", agent_type="optimization", operation="optimize_inventory", inputs={"sku": "SKU-001"}, dependencies=["forecast"])
]
results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.SEQUENTIAL)
```

#### Parallel Execution
Tasks execute concurrently, allowing independent operations to run simultaneously. Useful for workflows where multiple agents can work on different aspects without dependencies.

```python
tasks = [
    AgentTask(task_id="forecast", agent_type="forecasting", operation="generate_forecast", inputs={"sku": "SKU-001"}),
    AgentTask(task_id="anomaly", agent_type="anomaly_detection", operation="detect_anomalies", inputs={"sku": "SKU-001"}),
    AgentTask(task_id="report", agent_type="report_generation", operation="generate_report", inputs={})
]
results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.PARALLEL)
```

#### Conditional Execution
Tasks execute based on runtime conditions evaluated against the execution context. Useful for workflows with branching logic.

```python
def high_demand_condition(ctx):
    return ctx.get("forecast", {}).get("forecast", 0) > 100

tasks = [
    AgentTask(task_id="forecast", agent_type="forecasting", operation="generate_forecast", inputs={"sku": "SKU-001"}),
    AgentTask(
        task_id="emergency_procurement",
        agent_type="supplier_coordination",
        operation="send_purchase_order",
        inputs={"sku": "SKU-001"},
        condition=high_demand_condition
    )
]
results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.CONDITIONAL)
```

## Agent Communication

### Data Passing Between Agents

When tasks have dependencies, outputs from previous tasks are automatically merged into the inputs of dependent tasks:

```python
# Task 1 output: {"forecast": 100, "confidence": 0.95}
# Task 2 receives: {"sku": "SKU-001", "forecast": 100, "confidence": 0.95}
```

### Execution Context

The execution context maintains state across tasks and is used for conditional evaluation:

```python
context = {
    "task1": {"forecast": 100},
    "task2": {"eoq": 50}
}
```

## Error Handling

The orchestrator provides comprehensive error handling:

1. **Task-Level Errors**: Individual task failures don't stop the workflow; errors are captured and reported
2. **Dependency Errors**: If a dependency fails, dependent tasks are marked as failed
3. **Invalid Operations**: Attempts to call non-existent agent operations are caught and reported
4. **Execution Tracking**: All errors are logged and included in execution results

## Execution History

The orchestrator maintains a history of all executed tasks:

```python
orchestrator = AgentOrchestrator()
results = orchestrator.execute_workflow(tasks)
history = orchestrator.get_execution_history()

# Access results from previous executions
for task_id, result in history.items():
    print(f"{task_id}: {result.status} ({result.execution_time_ms}ms)")
```

## Supported Agents

The orchestrator supports the following agent types:

- **forecasting**: DemandForecastingAgent
- **optimization**: InventoryOptimizerAgent
- **supplier_coordination**: SupplierCoordinationAgent
- **anomaly_detection**: AnomalyDetectionAgent
- **report_generation**: ReportGenerationAgent

## Usage Examples

### Example 1: Complete Inventory Update Workflow

```python
orchestrator = AgentOrchestrator()

tasks = [
    # Step 1: Generate forecast
    AgentTask(
        task_id="forecast",
        agent_type="forecasting",
        operation="generate_forecast",
        inputs={"sku": "SKU-001"}
    ),
    # Step 2: Optimize inventory (depends on forecast)
    AgentTask(
        task_id="optimize",
        agent_type="optimization",
        operation="optimize_inventory",
        inputs={"sku": "SKU-001"},
        dependencies=["forecast"]
    ),
    # Step 3: Detect anomalies (depends on optimization)
    AgentTask(
        task_id="anomaly",
        agent_type="anomaly_detection",
        operation="detect_anomalies",
        inputs={"sku": "SKU-001"},
        dependencies=["optimize"]
    ),
    # Step 4: Generate report (depends on anomaly detection)
    AgentTask(
        task_id="report",
        agent_type="report_generation",
        operation="generate_report",
        inputs={}
    )
]

results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.SEQUENTIAL)

for task_id, result in results.items():
    if result.status == "success":
        print(f"{task_id}: Success ({result.execution_time_ms}ms)")
    else:
        print(f"{task_id}: Failed - {result.error}")
```

### Example 2: Parallel Analysis Workflow

```python
orchestrator = AgentOrchestrator()

tasks = [
    AgentTask(
        task_id="forecast",
        agent_type="forecasting",
        operation="generate_forecast",
        inputs={"sku": "SKU-001"}
    ),
    AgentTask(
        task_id="anomaly",
        agent_type="anomaly_detection",
        operation="detect_anomalies",
        inputs={"sku": "SKU-001"}
    ),
    AgentTask(
        task_id="supplier_check",
        agent_type="supplier_coordination",
        operation="get_supplier_performance",
        inputs={"supplier_id": "SUP-001"}
    )
]

results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.PARALLEL)
```

### Example 3: Conditional Procurement Workflow

```python
def needs_emergency_order(ctx):
    forecast = ctx.get("forecast", {}).get("forecast", 0)
    return forecast > 500  # Emergency order if forecast > 500

orchestrator = AgentOrchestrator()

tasks = [
    AgentTask(
        task_id="forecast",
        agent_type="forecasting",
        operation="generate_forecast",
        inputs={"sku": "SKU-001"}
    ),
    AgentTask(
        task_id="emergency_order",
        agent_type="supplier_coordination",
        operation="send_purchase_order",
        inputs={"sku": "SKU-001", "quantity": 1000},
        condition=needs_emergency_order
    )
]

results = orchestrator.execute_workflow(tasks, pattern=ExecutionPattern.CONDITIONAL)
```

## Performance Considerations

1. **Sequential Execution**: Total time = sum of all task times
2. **Parallel Execution**: Total time = max of all task times (faster for independent tasks)
3. **Conditional Execution**: Total time = sum of executed tasks (skipped tasks have minimal overhead)

## Testing

The agent orchestration module includes comprehensive integration tests covering:

- Sequential execution with dependencies
- Parallel execution of independent tasks
- Conditional execution with runtime conditions
- Error handling and recovery
- Agent communication and data passing
- Execution history tracking

Run tests with:
```bash
pytest tests/test_agent_orchestration.py -v
```

## Integration with Event-Driven Orchestration

The Agent Orchestrator works seamlessly with the Event-Driven Orchestration layer:

1. **EventBridge** triggers Lambda functions on events
2. **Lambda handlers** create AgentTask instances
3. **AgentOrchestrator** executes tasks with specified patterns
4. **Results** are stored in RDS/DynamoDB and alerts sent via SNS

This two-layer architecture provides both event-driven responsiveness and flexible agent coordination.
