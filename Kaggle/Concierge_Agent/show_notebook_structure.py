"""
Generate a summary of the final notebook structure
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("=== Final Notebook Structure ===\n")
print(f"Total cells: {len(notebook['cells'])}\n")

for idx, cell in enumerate(notebook['cells']):
    cell_type = cell['cell_type']
    source = ''.join(cell.get('source', []))
    
    if cell_type == 'markdown':
        first_line = source.split('\n')[0]
        print(f"{idx+1:2d}. [MD] {first_line[:70]}")
    else:
        first_line = source.split('\n')[0]
        print(f"{idx+1:2d}. [CODE] {first_line[:67]}...")

print("\n" + "="*60)
print("✅ Notebook is ready to use!")
print("="*60)
