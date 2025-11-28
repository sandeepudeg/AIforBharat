"""
Check for syntax and import errors in the notebook
"""
import json
import ast

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Checking for errors in notebook cells...\n")
errors_found = []

for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if not source.strip():
            continue
            
        # Check for common issues
        first_lines = source.split('\n')[:3]
        print(f"Cell {idx}: {' '.join(first_lines)[:60]}...")
        
        # Check for syntax errors
        try:
            ast.parse(source)
            print(f"  ✓ Syntax OK")
        except SyntaxError as e:
            print(f"  ✗ Syntax Error: {e}")
            errors_found.append((idx, 'syntax', str(e), source[:200]))
        except Exception as e:
            print(f"  ! Warning: {e}")
        
        # Check for undefined references
        if 'logger' in source and 'logger' not in source[:source.find('logger')]:
            if idx not in [c[0] for c in errors_found]:
                errors_found.append((idx, 'undefined', 'logger not defined', source[:200]))
                print(f"  ✗ Undefined: logger")
        
        print()

if errors_found:
    print(f"\n{'='*60}")
    print(f"ERRORS FOUND: {len(errors_found)}")
    print(f"{'='*60}\n")
    for idx, err_type, msg, code_preview in errors_found:
        print(f"Cell {idx} ({err_type}):")
        print(f"  Error: {msg}")
        print(f"  Preview: {code_preview}...")
        print()
else:
    print("✅ No errors found!")
