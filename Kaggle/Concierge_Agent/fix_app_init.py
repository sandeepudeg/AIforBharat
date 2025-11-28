"""
Fix App initialization and ADK commands in notebook
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing App initialization and commands...\n")

# Find and fix the App creation cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        # Fix App initialization
        if 'app = App(' in source and 'app_name' in source:
            new_source = """# Create ADK App for GUI access
from google.adk.apps.app import App

app = App(
    name="concierge-agent",
    root_agent=root_agent,
    description="A comprehensive travel concierge agent with 15 features for trip planning, bookings, and assistance."
)

print("✅ ADK App created!")
print("\\nTo start the web interface:")
print("  1. Save this notebook")
print("  2. In terminal, run: python -m google.adk.cli web")
print("  3. The app.py file is already configured for ADK CLI")
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Fixed App initialization in cell {idx}")
    
    elif cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        
        # Fix ADK web command instructions
        if 'adk web --app app:app' in source:
            new_source = source.replace(
                'adk web --app app:app --log_level DEBUG',
                'python -m google.adk.cli web'
            ).replace(
                'adk web --app app:app',
                'python -m google.adk.cli web'
            ).replace(
                'adk web --app Concierge_Agent:app',
                'python -m google.adk.cli web'
            )
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Fixed ADK commands in cell {idx}")

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixes applied!")
