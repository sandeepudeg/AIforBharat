"""
Clean up the notebook - remove demo code and organize cells
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Cleaning notebook...\n")

# Remove cells that contain demo code
cells_to_remove = []
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    
    # Check for demo-related content
    if any(keyword in source.lower() for keyword in ['demo', 'run_demo', 'input()', '# run the demo']):
        cells_to_remove.append(idx)
        print(f"Marking cell {idx} for removal: {cell['cell_type']} - contains demo code")

# Remove in reverse order
for idx in reversed(cells_to_remove):
    del notebook['cells'][idx]

print(f"\n✓ Removed {len(cells_to_remove)} demo-related cells")

# Add a final cell for ADK GUI instructions
final_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Running the Concierge Agent with ADK GUI\n",
        "\n",
        "After executing all cells above, you can access the agent through the ADK web interface:\n",
        "\n",
        "### Option 1: Using app.py (Recommended)\n",
        "```bash\n",
        "# In terminal, run:\n",
        "adk web --app app:app --log_level DEBUG\n",
        "```\n",
        "\n",
        "Then open your browser to the URL shown (typically http://localhost:8000)\n",
        "\n",
        "### Option 2: Direct from Notebook\n",
        "If you want to create an app directly in this notebook, run the cell below.\n"
    ]
}

# Add app creation cell
app_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create ADK App for GUI access\n",
        "from google.adk.apps.app import App\n",
        "\n",
        "app = App(\n",
        "    agent=root_agent,\n",
        "    app_name=\"Concierge Agent\",\n",
        "    description=\"A comprehensive travel concierge agent with 15 features for trip planning, bookings, and assistance.\"\n",
        ")\n",
        "\n",
        "print(\"✅ ADK App created!\")\n",
        "print(\"\\nTo start the web interface, run in terminal:\")\n",
        "print(\"  adk web --app app:app\")\n",
        "print(\"\\nOr if running from notebook:\")\n",
        "print(\"  Save this notebook, then run: adk web --app Concierge_Agent:app\")\n"
    ]
}

# Convert to proper format
final_cell['source'] = [line + '\n' for line in final_cell['source']]
final_cell['source'][-1] = final_cell['source'][-1].rstrip('\n')

app_cell['source'] = [line + '\n' for line in app_cell['source']]
app_cell['source'][-1] = app_cell['source'][-1].rstrip('\n')

# Add at the end
notebook['cells'].append(final_cell)
notebook['cells'].append(app_cell)

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"\n✅ Notebook cleaned!")
print(f"Total cells: {len(notebook['cells'])}")
print(f"Added GUI access instructions")
