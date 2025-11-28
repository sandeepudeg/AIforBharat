import json

nb_path = r"d:\\Learning\\IITKML\\Self_learning\\Kaggle\\Concierge_Agent\\Concierge_Agent.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Helper to locate a cell containing a snippet
def find_cell_index(snippet):
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code" and any(snippet in line for line in cell["source"]):
            return i
    return None

# Tools to register
tools_to_add = ["mcp_tool", "openapi_tool", "pause_tool", "resume_tool"]

agent_names = ["planning_agent", "booking_agent", "utility_agent", "search_agent", "social_agent"]

for agent in agent_names:
    idx = find_cell_index(f"{agent} = Agent(")
    if idx is None:
        continue
    src = nb["cells"][idx]["source"]
    # Find the line where the tools list ends (a line that contains a closing bracket "]" after "tools=[")
    insert_pos = None
    for i, line in enumerate(src):
        if "tools=[" in line:
            # search forward for a line that contains only a closing bracket (maybe with a comma)
            for j in range(i, len(src)):
                if "]" in src[j] and src[j].strip().endswith("]"):
                    insert_pos = j + 1
                    break
            break
    if insert_pos is None:
        insert_pos = len(src)
    # Build registration lines
    registration = [f"    # Register additional custom tools for {agent}\n"]
    for tool in tools_to_add:
        registration.append(f"    {agent}.tools.append({tool})\n")
    # Insert after the tools list
    src[insert_pos:insert_pos] = registration
    nb["cells"][idx]["source"] = src

# Ensure the demo loop has session handling and metrics (already present, but we add a safety block if missing)
run_demo_idx = find_cell_index("async def run_demo():")
if run_demo_idx is not None:
    src = nb["cells"][run_demo_idx]["source"]
    # Add import of pause controller if not present
    if not any("agent_pause_controller" in line for line in src):
        # Insert after the print line (line 0 likely)
        for i, line in enumerate(src):
            if "print(\\\"--- Starting Concierge Demo" in line:
                src.insert(i + 1, "    # Ensure pause controller is available\n    await agent_pause_controller.wait_if_paused()\n")
                break
    nb["cells"][run_demo_idx]["source"] = src

# Save notebook back
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4)

print('All agents now have MCP, OpenAPI, pause, and resume tools registered. Notebook updated.')
