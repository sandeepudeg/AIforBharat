"""
Fix errors in the notebook
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing errors in notebook...\n")

# Fix 1: Remove logger references from MCPTool classes (cells 21 and 23)
for idx in [21, 23]:
    if idx < len(notebook['cells']):
        cell = notebook['cells'][idx]
        source = ''.join(cell['source'])
        
        if 'logger.log_step' in source:
            # Replace logger.log_step with print
            new_source = source.replace(
                "logger.log_step(f'MCP {self.name}', f'args={args}, kwargs={kwargs}')",
                "print(f'MCP {self.name} called with args={args}, kwargs={kwargs}')"
            )
            new_source = new_source.replace(
                "logger.log_step('OpenAPI Call', f'endpoint={endpoint}')",
                "print(f'OpenAPI Call to endpoint={endpoint}')"
            )
            new_source = new_source.replace(
                "logger.log_step('A2A', f'{sender} -> {receiver}')",
                "print(f'A2A: {sender} -> {receiver}')"
            )
            
            # Update the cell
            notebook['cells'][idx]['source'] = new_source.split('\n')
            # Ensure each line ends with \n except the last one
            notebook['cells'][idx]['source'] = [
                line + '\n' if i < len(notebook['cells'][idx]['source']) - 1 else line
                for i, line in enumerate(notebook['cells'][idx]['source'])
            ]
            print(f"✓ Fixed cell {idx}: Replaced logger with print statements")

# Write back
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixes applied successfully!")
