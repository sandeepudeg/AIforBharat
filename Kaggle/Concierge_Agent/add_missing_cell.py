import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Create the missing features cell
missing_features_cell = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "source": [
        "# --- Missing Feature Implementations ---\n",
        "# 1. Mock MCP Tool (Multi-Component Process)\n",
        "class MCPTool(FunctionTool):\n",
        "    def __init__(self, name: str):\n",
        "        super().__init__(self.run)\n",
        "        self.name = name\n",
        "    def run(self, *args, **kwargs):\n",
        "        # Simulate a multi-step process\n",
        "        logger.log_step(f'MCP {self.name}', f'args={args}, kwargs={kwargs}')\n",
        "        return f'MCP {self.name} completed'\n",
        "\n",
        "# 2. OpenAPI Tool (mock)\n",
        "def call_openapi(endpoint: str, payload: dict):\n",
        "    logger.log_step('OpenAPI Call', f'endpoint={endpoint}')\n",
        "    # In a real scenario you would use requests.post...\n",
        "    return {'status': 'success', 'data': payload}\n",
        "\n",
        "# 3. Simple Session Service (in-memory)\n",
        "class SimpleSessionService:\n",
        "    def __init__(self):\n",
        "        self.sessions = {}\n",
        "    def get(self, session_id):\n",
        "        return self.sessions.get(session_id, {})\n",
        "    def set(self, session_id, state):\n",
        "        self.sessions[session_id] = state\n",
        "    def clear(self, session_id):\n",
        "        self.sessions.pop(session_id, None)\n",
        "\n",
        "session_service = SimpleSessionService()\n",
        "\n",
        "# 4. Context Compaction (simple token limit)\n",
        "def compact_context(messages, max_tokens=500):\n",
        "    # Very naive compaction: keep last N messages\n",
        "    if len(messages) <= max_tokens:\n",
        "        return messages\n",
        "    return messages[-max_tokens:]\n",
        "\n",
        "# 5. Metrics (simple counters)\n",
        "class Metrics:\n",
        "    def __init__(self):\n",
        "        self.counters = {}\n",
        "    def inc(self, name, amount=1):\n",
        "        self.counters[name] = self.counters.get(name, 0) + amount\n",
        "    def report(self):\n",
        "        return self.counters\n",
        "\n",
        "metrics = Metrics()\n",
        "\n",
        "# 6. Agent Evaluation (simple scoring)\n",
        "def evaluate_response(response: str) -> float:\n",
        "    # Placeholder: reward length and presence of keywords\n",
        "    score = len(response) * 0.01\n",
        "    for kw in ['success', 'confirmed', 'done']:\n",
        "        if kw in response.lower():\n",
        "            score += 0.5\n",
        "    return min(score, 1.0)\n",
        "\n",
        "# 7. Register new tools with agents\n",
        "mcp_tool = MCPTool('example_mcp')\n",
        "openapi_tool = FunctionTool(lambda endpoint, payload: call_openapi(endpoint, payload))\n",
        "\n",
        "print('✅ Missing feature implementations added.')\n"
    ]
}

# Insert this cell before the pause/resume cell (which is the last cell, index 14)
nb['cells'].insert(12, missing_features_cell)

# Save the notebook
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4, ensure_ascii=False)

print("✅ Added missing features cell to Concierge_Agent.ipynb")
print(f"Total cells now: {len(nb['cells'])}")
