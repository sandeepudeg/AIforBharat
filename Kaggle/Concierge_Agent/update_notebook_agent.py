"""
Update the App creation cell in notebook to export agent for ADK CLI
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating agent export in notebook...\n")

# Find and fix the App creation cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'app = App(' in source and 'concierge_agent' in source:
            new_source = """# Export agent for ADK CLI
# ADK CLI looks for an 'agent' variable in the file

agent = root_agent

print("✅ Agent exported for ADK CLI!")
print(f"   Agent name: {agent.name}")
print(f"   Agent type: {type(agent).__name__}")
print("\\nTo start the web interface:")
print("  1. Save this notebook as a .py file, OR")
print("  2. Run: python -m google.adk.cli web")
print("     (ADK will auto-discover app.py)")
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Updated agent export in cell {idx}")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Notebook updated - agent will be exported when cell runs!")
