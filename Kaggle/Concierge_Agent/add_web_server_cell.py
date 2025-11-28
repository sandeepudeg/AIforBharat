"""
Add a final cell to run ADK web server directly from the notebook
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Adding web server cell to notebook...\n")

# Create a final cell that runs the web server
server_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Running the ADK Web Interface\n",
        "\n",
        "Execute the cell below to start the ADK web interface directly from this notebook.\n"
    ]
}

code_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Start ADK Web Server directly from notebook\n",
        "import asyncio\n",
        "from google.adk.cli.fast_api import create_web_app\n",
        "import uvicorn\n",
        "\n",
        "# Create the web app with our agent\n",
        "web_app = create_web_app(\n",
        "    apps_dir=\"./\",\n",
        "    agents_dir=\"./\",\n",
        "    disable_auth=True\n",
        ")\n",
        "\n",
        "# Register our agent\n",
        "from google.adk.cli.discovery import register_agent\n",
        "register_agent(\"concierge_agent\", agent)\n",
        "\n",
        "print(\"Starting ADK Web Server...\")\n",
        "print(\"Open http://127.0.0.1:8000 in your browser\")\n",
        "print(\"\\nPress Ctrl+C to stop the server\")\n",
        "\n",
        "# Run the server\n",
        "uvicorn.run(web_app, host=\"127.0.0.1\", port=8000)\n"
    ]
}

# Convert to proper format
server_cell['source'] = [line + '\n' for line in server_cell['source']]
server_cell['source'][-1] = server_cell['source'][-1].rstrip('\n')

code_cell['source'] = [line + '\n' for line in code_cell['source']]
code_cell['source'][-1] = code_cell['source'][-1].rstrip('\n')

# Remove old final cells about App
cells_to_remove = []
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'agent = root_agent' in source or 'app = App' in source:
        if idx >= len(notebook['cells']) - 5:  # Only remove if near the end
            cells_to_remove.append(idx)
            print(f"Removing old cell {idx}")

# Remove in reverse
for idx in reversed(cells_to_remove):
    del notebook['cells'][idx]

# Add new cells at the end
notebook['cells'].append(server_cell)
notebook['cells'].append(code_cell)

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"\n✅ Added web server cell to notebook!")
print(f"Total cells: {len(notebook['cells'])}")
