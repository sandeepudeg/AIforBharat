"""
Fix App name - use underscores instead of hyphens
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing App name...\n")

# Find and fix the App creation cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'app = App(' in source and 'concierge-agent' in source:
            # Replace hyphen with underscore
            new_source = source.replace('concierge-agent', 'concierge_agent')
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Fixed App name in cell {idx}: concierge-agent → concierge_agent")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixed - app name is now a valid identifier!")
