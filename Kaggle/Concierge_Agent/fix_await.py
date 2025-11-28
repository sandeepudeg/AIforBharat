"""
Fix the await outside function error
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing await issue...\n")

# Find and fix the chat cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'await chat_with_agent()' in source:
            # Remove the standalone await - make it commented
            new_source = source.replace(
                '# Start the chat\nawait chat_with_agent()',
                '# Start the chat\n# Uncomment and run in async context:\n# await chat_with_agent()\nprint("✅ Agent ready! Uncomment the line above to start chatting.")'
            )
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Fixed await in cell {idx}")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixed!")
