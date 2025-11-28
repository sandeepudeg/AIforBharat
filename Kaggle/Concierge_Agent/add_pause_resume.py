import json

nb_path = r"d:\\Learning\\IITKML\\Self_learning\\Kaggle\\Concierge_Agent\\Concierge_Agent.ipynb"

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# New cell defining pause/resume utilities
new_cell = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "source": [
        "# --- Long‑running operation helpers (pause / resume) ---\n",
        "import asyncio\n",
        "\n",
        "# Simple flag‑based pause/resume for agents\n",
        "class AgentPauseController:\n",
        "    def __init__(self):\n",
        "        self.paused = False\n",
        "    async def pause(self):\n",
        "        self.paused = True\n",
        "        print('🛑 Agent execution paused')\n",
        "    async def resume(self):\n",
        "        self.paused = False\n",
        "        print('▶️ Agent execution resumed')\n",
        "    async def wait_if_paused(self):\n",
        "        while self.paused:\n",
        "            await asyncio.sleep(0.5)\n",
        "\n",
        "# Create a global controller that can be used by any agent\n",
        "agent_pause_controller = AgentPauseController()\n",
        "\n",
        "# Expose as FunctionTool so agents can request pause/resume\n",
        "pause_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.pause()))\n",
        "resume_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.resume()))\n",
        "# You can add these tools to any agent's tool list if needed\n",
        "# Example: planning_agent.tools.append(pause_tool)\n",
        "#          planning_agent.tools.append(resume_tool)\n",
        "print('✅ Pause/Resume utilities added')\n"
    ]
}

nb['cells'].append(new_cell)

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=4)

print('Notebook updated with pause/resume utilities')
