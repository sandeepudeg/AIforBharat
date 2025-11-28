"""
Fix App initialization - remove description parameter
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing App initialization...\n")

# Find and fix the App creation cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'app = App(' in source and 'name="concierge-agent"' in source:
            new_source = """# Create ADK App for GUI access
from google.adk.apps.app import App

# Create the app with minimal required parameters
app = App(
    name="concierge-agent",
    root_agent=root_agent
)

print("✅ ADK App created!")
print("\\nTo start the web interface:")
print("  Run in terminal: python -m google.adk.cli web")
print("  Then open: http://localhost:8000")
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Fixed App initialization in cell {idx}")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixed - removed description parameter!")
