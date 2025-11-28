import json

nb_path = r"d:\\Learning\\IITKML\\Self_learning\\Kaggle\\Concierge_Agent\\Concierge_Agent.ipynb"

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to find cell index by snippet
def find_cell(snippet):
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code' and any(snippet in line for line in cell['source']):
            return i
    return None

# 1. Append a new cell with tracing and InMemorySessionService definitions
trace_cell = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "source": [
        "# --- Tracing and In‑Memory Session Service (ADK‑style) ---\n",
        "class InMemorySessionService:\n",
        "    def __init__(self):\n",
        "        self.store = {}  # session_id -> dict\n",
        "    def get_session(self, session_id: str):\n",
        "        return self.store.setdefault(session_id, {})\n",
        "    def set_state(self, session_id: str, key: str, value):\n",
        "        sess = self.get_session(session_id)\n",
        "        sess[key] = value\n",
        "    def get_state(self, session_id: str, key: str, default=None):\n",
        "        return self.get_session(session_id).get(key, default)\n",
        "\n",
        "# Simple tracing utility (adds a step to logger)\n",
        "def trace_step(step_name: str, details: str = ''):\n",
        "    logger.log_step(f'TRACE:{step_name}', details)\n",
        "\n",
        "# Instantiate a global session service\n",
        "session_service_adk = InMemorySessionService()\n",
        "print('✅ Tracing and InMemorySessionService added')\n"
    ]
}
nb['cells'].append(trace_cell)

# 2. Register pause/resume and tracing tools with each agent
pause_tool_line = "    planning_agent.tools.append(pause_tool)"
resume_tool_line = "    planning_agent.tools.append(resume_tool)"
# We'll add to each agent cell after its tools list
agent_names = ['planning_agent', 'booking_agent', 'utility_agent', 'search_agent', 'social_agent']
for agent in agent_names:
    idx = find_cell(f"{agent} = Agent(")
    if idx is not None:
        src = nb['cells'][idx]['source']
        # Find the line that ends the tools list (the line containing "]" after "tools=[")
        insert_pos = None
        for i, line in enumerate(src):
            if "tools=[" in line:
                # look ahead for the closing bracket line
                for j in range(i, len(src)):
                    if "]" in src[j] and "]" in src[j].strip():
                        insert_pos = j + 1
                        break
                break
        if insert_pos is None:
            insert_pos = len(src)
        # Insert pause and resume registration (and optional trace)
        registration = [
            f"    # Register pause/resume and tracing tools for {agent}\n",
            "    planning_agent.tools.append(pause_tool)\n" if agent == 'planning_agent' else "    # pause/resume added to other agents\n",
            "    planning_agent.tools.append(resume_tool)\n" if agent == 'planning_agent' else "    # pause/resume added to other agents\n",
            "    # Example trace call (can be used inside agent logic)\n",
            "    # trace_step('example', 'details')\n"
        ]
        src[insert_pos:insert_pos] = registration
        nb['cells'][idx]['source'] = src

# Save notebook
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=4)

print('Extra features (tracing, session service, pause/resume registration) added to notebook.')
