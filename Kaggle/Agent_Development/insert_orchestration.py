import json

# Read the notebook
with open('concierge_agents_system.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find the orchestration markdown cell
orchestration_idx = None
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        if '## Orchestration' in source and 'parallel, sequential, and loop' in source:
            orchestration_idx = i
            break

if orchestration_idx is None:
    print("ERROR: Could not find orchestration section!")
    exit(1)

print(f"Found orchestration section at cell index {orchestration_idx}")

# Create the orchestration implementation cells
new_cells = []


# 1. Parallel Executor header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Parallel Executor\n",
        "\n",
        "Execute multiple agents concurrently using asyncio."
    ]
})

# 2. Parallel Executor implementation
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "@dataclass\n",
        "class AggregatedResult:\n",
        "    \"\"\"Aggregated results from multiple agent executions.\"\"\"\n",
        "    responses: List[AgentResponse]\n",
        "    successful_count: int\n",
        "    failed_count: int\n",
        "    total_execution_time: float\n",
        "    errors: List[Exception]\n",
        "\n",
        "\n",
        "class ParallelExecutor:\n",
        "    \"\"\"Executes multiple agents concurrently.\"\"\"\n",
        "    \n",
        "    def __init__(self, agents: List[ConciergeAgent]):\n",
        "        \"\"\"\n",
        "        Initialize parallel executor.\n",
        "        \n",
        "        Args:\n",
        "            agents: List of agents to execute in parallel\n",
        "        \"\"\"\n",
        "        self.agents = agents\n",
        "    \n",
        "    async def execute_all(self, tasks: List[Task]) -> List[AgentResponse]:\n",
        "        \"\"\"\n",
        "        Execute all agents concurrently with their respective tasks.\n",
        "        \n",
        "        Args:\n",
        "            tasks: List of tasks (one per agent)\n",
        "            \n",
        "        Returns:\n",
        "            List of agent responses\n",
        "        \"\"\"\n",
        "        if len(tasks) != len(self.agents):\n",
        "            raise ValueError(f\"Number of tasks ({len(tasks)}) must match number of agents ({len(self.agents)})\")\n",
        "        \n",
        "        # Create async tasks for each agent\n",
        "        async_tasks = []\n",
        "        for agent, task in zip(self.agents, tasks):\n",
        "            async_tasks.append(self._execute_agent_async(agent, task))\n",
        "        \n",
        "        # Execute all tasks concurrently\n",
        "        responses = await asyncio.gather(*async_tasks, return_exceptions=True)\n",
        "        \n",
        "        # Convert exceptions to error responses\n",
        "        processed_responses = []\n",
        "        for i, response in enumerate(responses):\n",
        "            if isinstance(response, Exception):\n",
        "                # Create error response\n",
        "                processed_responses.append(AgentResponse(\n",
        "                    task_id=tasks[i].task_id,\n",
        "                    agent_id=self.agents[i].agent_id,\n",
        "                    output=None,\n",
        "                    tool_calls=[],\n",
        "                    execution_time=0.0,\n",
        "                    status='error',\n",
        "                    error=response\n",
        "                ))\n",
        "            else:\n",
        "                processed_responses.append(response)\n",
        "        \n",
        "        return processed_responses\n",
        "    \n",
        "    async def _execute_agent_async(self, agent: ConciergeAgent, task: Task) -> AgentResponse:\n",
        "        \"\"\"Execute a single agent asynchronously.\"\"\"\n",
        "        # Run the synchronous execute method in a thread pool\n",
        "        loop = asyncio.get_event_loop()\n",
        "        return await loop.run_in_executor(None, agent.execute, task)\n",
        "    \n",
        "    def aggregate_results(self, responses: List[AgentResponse]) -> AggregatedResult:\n",
        "        \"\"\"\n",
        "        Aggregate results from multiple agent executions.\n",
        "        \n",
        "        Args:\n",
        "            responses: List of agent responses\n",
        "            \n",
        "        Returns:\n",
        "            Aggregated result summary\n",
        "        \"\"\"\n",
        "        successful = [r for r in responses if r.status == 'success']\n",
        "        failed = [r for r in responses if r.status == 'error']\n",
        "        errors = [r.error for r in failed if r.error is not None]\n",
        "        total_time = sum(r.execution_time for r in responses)\n",
        "        \n",
        "        return AggregatedResult(\n",
        "            responses=responses,\n",
        "            successful_count=len(successful),\n",
        "            failed_count=len(failed),\n",
        "            total_execution_time=total_time,\n",
        "            errors=errors\n",
        "        )\n",
        "\n",
        "\n",
        "print(\"✓ ParallelExecutor class implemented successfully\")"
    ]
})


# 3. Parallel Executor example header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Example: Parallel Agent Execution\n",
        "\n",
        "Demonstrate multiple agents running concurrently."
    ]
})

# 4. Create agents for parallel execution
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create multiple agents for parallel execution\n",
        "agent1 = ConciergeAgent(\n",
        "    name='summarizer',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "agent2 = ConciergeAgent(\n",
        "    name='analyzer',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "agent3 = ConciergeAgent(\n",
        "    name='translator',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "print(f\"✓ Created 3 agents for parallel execution\")\n",
        "print(f\"  Agent 1: {agent1.agent_id}\")\n",
        "print(f\"  Agent 2: {agent2.agent_id}\")\n",
        "print(f\"  Agent 3: {agent3.agent_id}\")"
    ]
})

# 5. Create tasks and execute
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create tasks for each agent\n",
        "task1 = Task(\n",
        "    task_id=str(uuid.uuid4()),\n",
        "    description=\"Summarize the key benefits of multi-agent systems in one sentence.\",\n",
        "    input_data={}\n",
        ")\n",
        "\n",
        "task2 = Task(\n",
        "    task_id=str(uuid.uuid4()),\n",
        "    description=\"Analyze the main challenges in building multi-agent systems.\",\n",
        "    input_data={}\n",
        ")\n",
        "\n",
        "task3 = Task(\n",
        "    task_id=str(uuid.uuid4()),\n",
        "    description=\"Explain what agent orchestration means in simple terms.\",\n",
        "    input_data={}\n",
        ")\n",
        "\n",
        "# Create parallel executor and run agents\n",
        "parallel_executor = ParallelExecutor([agent1, agent2, agent3])\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"PARALLEL EXECUTION\")\n",
        "print(f\"{'='*60}\\n\")\n",
        "print(f\"Executing {len(parallel_executor.agents)} agents in parallel...\\n\")\n",
        "\n",
        "# Execute all agents concurrently\n",
        "responses = await parallel_executor.execute_all([task1, task2, task3])\n",
        "\n",
        "# Display results\n",
        "for i, response in enumerate(responses, 1):\n",
        "    print(f\"Agent {i}: {response.agent_id}\")\n",
        "    print(f\"  Status: {response.status}\")\n",
        "    print(f\"  Execution Time: {response.execution_time:.3f}s\")\n",
        "    if response.status == 'success':\n",
        "        output_preview = response.output[:100] + '...' if len(response.output) > 100 else response.output\n",
        "        print(f\"  Output: {output_preview}\")\n",
        "    else:\n",
        "        print(f\"  Error: {response.error}\")\n",
        "    print()\n",
        "\n",
        "# Aggregate results\n",
        "aggregated = parallel_executor.aggregate_results(responses)\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"AGGREGATED RESULTS\")\n",
        "print(f\"{'='*60}\")\n",
        "print(f\"Total Agents: {len(responses)}\")\n",
        "print(f\"Successful: {aggregated.successful_count}\")\n",
        "print(f\"Failed: {aggregated.failed_count}\")\n",
        "print(f\"Total Execution Time: {aggregated.total_execution_time:.3f}s\")\n",
        "if aggregated.errors:\n",
        "    print(f\"\\nErrors:\")\n",
        "    for error in aggregated.errors:\n",
        "        print(f\"  - {error}\")"
    ]
})


# 6. Sequential Executor header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Sequential Executor\n",
        "\n",
        "Execute agents in order, passing outputs as inputs to the next agent."
    ]
})

# 7. Sequential Executor implementation
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "class SequentialExecutor:\n",
        "    \"\"\"Executes agents in order, passing outputs as inputs.\"\"\"\n",
        "    \n",
        "    def __init__(self, agents: List[ConciergeAgent]):\n",
        "        \"\"\"\n",
        "        Initialize sequential executor.\n",
        "        \n",
        "        Args:\n",
        "            agents: List of agents to execute sequentially\n",
        "        \"\"\"\n",
        "        self.agents = agents\n",
        "    \n",
        "    def execute_chain(self, initial_task: Task) -> AgentResponse:\n",
        "        \"\"\"\n",
        "        Execute agents in sequence, passing output to next agent.\n",
        "        \n",
        "        Args:\n",
        "            initial_task: Initial task for the first agent\n",
        "            \n",
        "        Returns:\n",
        "            Final agent response from the last agent in the chain\n",
        "        \"\"\"\n",
        "        current_task = initial_task\n",
        "        responses = []\n",
        "        \n",
        "        for i, agent in enumerate(self.agents):\n",
        "            # Execute current agent\n",
        "            response = agent.execute(current_task)\n",
        "            responses.append(response)\n",
        "            \n",
        "            # Check for failure\n",
        "            if response.status == 'error':\n",
        "                # Halt the chain on error\n",
        "                print(f\"Chain halted at agent {i+1}/{len(self.agents)} due to error: {response.error}\")\n",
        "                return response\n",
        "            \n",
        "            # Prepare task for next agent (if not last agent)\n",
        "            if i < len(self.agents) - 1:\n",
        "                current_task = self._pass_output_to_next(response, self.agents[i + 1])\n",
        "        \n",
        "        # Return the final response\n",
        "        return responses[-1]\n",
        "    \n",
        "    def _pass_output_to_next(self, output: AgentResponse, next_agent: ConciergeAgent) -> Task:\n",
        "        \"\"\"\n",
        "        Transform output from one agent into input for the next.\n",
        "        \n",
        "        Args:\n",
        "            output: Response from previous agent\n",
        "            next_agent: Next agent in the chain\n",
        "            \n",
        "        Returns:\n",
        "            New task for the next agent\n",
        "        \"\"\"\n",
        "        # Create new task with previous output as input\n",
        "        return Task(\n",
        "            task_id=str(uuid.uuid4()),\n",
        "            description=f\"Process the following input from the previous agent: {output.output}\",\n",
        "            input_data={\n",
        "                'previous_output': output.output,\n",
        "                'previous_agent': output.agent_id,\n",
        "                'previous_task_id': output.task_id\n",
        "            },\n",
        "            context={\n",
        "                'chain_position': len([a for a in self.agents if a.agent_id != next_agent.agent_id]) + 1,\n",
        "                'total_agents': len(self.agents)\n",
        "            }\n",
        "        )\n",
        "\n",
        "\n",
        "print(\"✓ SequentialExecutor class implemented successfully\")"
    ]
})


# 8. Sequential Executor example header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Example: Sequential Agent Execution\n",
        "\n",
        "Demonstrate agents executing in a chain, with each agent processing the previous agent's output."
    ]
})

# 9. Sequential execution example
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create agents for sequential execution\n",
        "researcher = ConciergeAgent(\n",
        "    name='researcher',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "summarizer = ConciergeAgent(\n",
        "    name='summarizer',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "reviewer = ConciergeAgent(\n",
        "    name='reviewer',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "# Create initial task\n",
        "initial_task = Task(\n",
        "    task_id=str(uuid.uuid4()),\n",
        "    description=\"Research and explain the concept of agent orchestration in AI systems.\",\n",
        "    input_data={'topic': 'agent orchestration'},\n",
        "    context={'domain': 'artificial intelligence'}\n",
        ")\n",
        "\n",
        "# Create sequential executor and run chain\n",
        "sequential_executor = SequentialExecutor([researcher, summarizer, reviewer])\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"SEQUENTIAL EXECUTION\")\n",
        "print(f\"{'='*60}\\n\")\n",
        "print(f\"Executing {len(sequential_executor.agents)} agents in sequence...\\n\")\n",
        "\n",
        "# Execute the chain\n",
        "final_response = sequential_executor.execute_chain(initial_task)\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"FINAL RESULT\")\n",
        "print(f\"{'='*60}\")\n",
        "print(f\"Final Agent: {final_response.agent_id}\")\n",
        "print(f\"Status: {final_response.status}\")\n",
        "print(f\"Execution Time: {final_response.execution_time:.3f}s\")\n",
        "print(f\"\\nFinal Output:\\n{final_response.output}\")"
    ]
})


# 10. Loop Executor header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Loop Executor\n",
        "\n",
        "Execute an agent repeatedly based on a condition, with iteration state management."
    ]
})

# 11. Loop Executor implementation
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "class LoopExecutor:\n",
        "    \"\"\"Executes agent repeatedly based on condition.\"\"\"\n",
        "    \n",
        "    def __init__(self, agent: ConciergeAgent, condition: Callable[[AgentResponse], bool], max_iterations: int = 100):\n",
        "        \"\"\"\n",
        "        Initialize loop executor.\n",
        "        \n",
        "        Args:\n",
        "            agent: Agent to execute in loop\n",
        "            condition: Function that returns True to continue loop, False to stop\n",
        "            max_iterations: Maximum number of iterations to prevent infinite loops\n",
        "        \"\"\"\n",
        "        self.agent = agent\n",
        "        self.condition = condition\n",
        "        self.max_iterations = max_iterations\n",
        "        self.iteration_state: Dict[str, Any] = {}\n",
        "    \n",
        "    def execute_loop(self, initial_task: Task) -> List[AgentResponse]:\n",
        "        \"\"\"\n",
        "        Execute agent in a loop until condition is met or max iterations reached.\n",
        "        \n",
        "        Args:\n",
        "            initial_task: Initial task for the first iteration\n",
        "            \n",
        "        Returns:\n",
        "            List of agent responses from all iterations\n",
        "        \"\"\"\n",
        "        responses = []\n",
        "        current_task = initial_task\n",
        "        iteration = 0\n",
        "        \n",
        "        while iteration < self.max_iterations:\n",
        "            iteration += 1\n",
        "            \n",
        "            # Update iteration state\n",
        "            self.iteration_state['current_iteration'] = iteration\n",
        "            self.iteration_state['max_iterations'] = self.max_iterations\n",
        "            \n",
        "            # Add iteration info to task context\n",
        "            current_task.context = current_task.context or {}\n",
        "            current_task.context['iteration'] = iteration\n",
        "            current_task.context['max_iterations'] = self.max_iterations\n",
        "            \n",
        "            # Execute agent\n",
        "            response = self.agent.execute(current_task)\n",
        "            responses.append(response)\n",
        "            \n",
        "            # Check for error\n",
        "            if response.status == 'error':\n",
        "                print(f\"Loop stopped at iteration {iteration} due to error: {response.error}\")\n",
        "                break\n",
        "            \n",
        "            # Evaluate condition\n",
        "            should_continue = self.evaluate_condition(response)\n",
        "            \n",
        "            if not should_continue:\n",
        "                print(f\"Loop condition met at iteration {iteration}. Stopping.\")\n",
        "                break\n",
        "            \n",
        "            # Check max iterations\n",
        "            if iteration >= self.max_iterations:\n",
        "                print(f\"Maximum iterations ({self.max_iterations}) reached. Stopping.\")\n",
        "                break\n",
        "            \n",
        "            # Prepare task for next iteration\n",
        "            current_task = self._create_next_iteration_task(response, iteration)\n",
        "        \n",
        "        return responses\n",
        "    \n",
        "    def evaluate_condition(self, response: AgentResponse) -> bool:\n",
        "        \"\"\"\n",
        "        Evaluate whether to continue the loop.\n",
        "        \n",
        "        Args:\n",
        "            response: Response from current iteration\n",
        "            \n",
        "        Returns:\n",
        "            True to continue loop, False to stop\n",
        "        \"\"\"\n",
        "        try:\n",
        "            return self.condition(response)\n",
        "        except Exception as e:\n",
        "            print(f\"Error evaluating condition: {e}. Stopping loop.\")\n",
        "            return False\n",
        "    \n",
        "    def _create_next_iteration_task(self, previous_response: AgentResponse, iteration: int) -> Task:\n",
        "        \"\"\"\n",
        "        Create task for next iteration based on previous response.\n",
        "        \n",
        "        Args:\n",
        "            previous_response: Response from previous iteration\n",
        "            iteration: Current iteration number\n",
        "            \n",
        "        Returns:\n",
        "            Task for next iteration\n",
        "        \"\"\"\n",
        "        return Task(\n",
        "            task_id=str(uuid.uuid4()),\n",
        "            description=f\"Continue processing based on previous iteration result.\",\n",
        "            input_data={\n",
        "                'previous_output': previous_response.output,\n",
        "                'iteration': iteration + 1\n",
        "            },\n",
        "            context={\n",
        "                'previous_task_id': previous_response.task_id,\n",
        "                'iteration': iteration + 1\n",
        "            }\n",
        "        )\n",
        "\n",
        "\n",
        "print(\"✓ LoopExecutor class implemented successfully\")"
    ]
})


# 12. Loop Executor example header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Example: Loop Agent Execution\n",
        "\n",
        "Demonstrate an agent executing in a loop until a condition is met."
    ]
})

# 13. Loop execution example
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create agent for loop execution\n",
        "counter_agent = ConciergeAgent(\n",
        "    name='counter',\n",
        "    llm_config=llm_config\n",
        ")\n",
        "\n",
        "# Define a condition function\n",
        "def should_continue(response: AgentResponse) -> bool:\n",
        "    \"\"\"\n",
        "    Condition to continue loop.\n",
        "    Stops after 3 iterations for this example.\n",
        "    \"\"\"\n",
        "    # Check iteration count from task context\n",
        "    iteration = response.output.count('iteration') if response.output else 0\n",
        "    return iteration < 3\n",
        "\n",
        "# Create initial task\n",
        "loop_task = Task(\n",
        "    task_id=str(uuid.uuid4()),\n",
        "    description=\"Count and describe iteration 1. Mention 'iteration' in your response.\",\n",
        "    input_data={'count': 1},\n",
        "    context={'iteration': 1}\n",
        ")\n",
        "\n",
        "# Create loop executor and run\n",
        "loop_executor = LoopExecutor(\n",
        "    agent=counter_agent,\n",
        "    condition=should_continue,\n",
        "    max_iterations=5\n",
        ")\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"LOOP EXECUTION\")\n",
        "print(f\"{'='*60}\\n\")\n",
        "print(f\"Executing agent in loop (max {loop_executor.max_iterations} iterations)...\\n\")\n",
        "\n",
        "# Execute the loop\n",
        "loop_responses = loop_executor.execute_loop(loop_task)\n",
        "\n",
        "print(f\"\\n{'='*60}\")\n",
        "print(f\"LOOP RESULTS\")\n",
        "print(f\"{'='*60}\")\n",
        "print(f\"Total Iterations: {len(loop_responses)}\")\n",
        "print(f\"\\nIteration Details:\")\n",
        "for i, response in enumerate(loop_responses, 1):\n",
        "    print(f\"\\nIteration {i}:\")\n",
        "    print(f\"  Status: {response.status}\")\n",
        "    print(f\"  Execution Time: {response.execution_time:.3f}s\")\n",
        "    output_preview = response.output[:100] + '...' if len(response.output) > 100 else response.output\n",
        "    print(f\"  Output: {output_preview}\")"
    ]
})

# Insert the new cells into the notebook
print(f"\nInserting {len(new_cells)} orchestration cells into notebook...")
notebook['cells'] = (
    notebook['cells'][:orchestration_idx + 1] +
    new_cells +
    notebook['cells'][orchestration_idx + 1:]
)

# Save the modified notebook
with open('concierge_agents_system.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"✓ Successfully added orchestration implementation!")
print(f"  Total cells in notebook: {len(notebook['cells'])}")
print(f"  Orchestration cells added: {len(new_cells)}")
