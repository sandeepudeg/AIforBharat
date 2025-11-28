"""
Simple error check using compile() instead of ast.parse()
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Checking for syntax errors...\n")
errors = []

for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if not source.strip():
            continue
        
        try:
            compile(source, f'<cell{idx}>', 'exec')
        except SyntaxError as e:
            errors.append((idx, e.lineno, e.msg, str(e)))
            print(f"Cell {idx}, Line {e.lineno}: {e.msg}")

if not errors:
    print("✅ No syntax errors found!")
else:
    print(f"\n❌ Found {len(errors)} errors")
