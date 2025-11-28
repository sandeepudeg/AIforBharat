"""
Fix all syntax errors in the notebook by finding and fixing problematic cells
"""
import json
import re

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing syntax errors in notebook...\n")
fixes_applied = 0

for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = cell['source']
        # Fix escaped newlines in markdown (should be just \n not \\n)
        new_source = []
        changed = False
        for line in source:
            if '\\\\n' in line:
                new_line = line.replace('\\\\n', '\\n')
                new_source.append(new_line)
                changed = True
            else:
                new_source.append(line)
        
        if changed:
            cell['source'] = new_source
            print(f"✓ Fixed cell {idx}: Removed escaped newlines in markdown")
            fixes_applied += 1
    
    elif cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Check for the specific syntax error pattern
        if 'print("✅ MCP Tool' in source and 'definitions registered.")' in source:
            # The issue is a line break in the middle of the print statement
            lines = cell['source']
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                # If this line has print("✅ MCP Tool and doesn't end properly
                if 'print("✅ MCP Tool' in line and 'registered.")' not in line:
                    # Combine with next line
                    if i + 1 < len(lines):
                        combined = line.rstrip('\\n') + lines[i + 1]
                        new_lines.append(combined)
                        i += 2
                        print(f"✓ Fixed cell {idx}: Combined split print statement")
                        fixes_applied += 1
                        continue
                new_lines.append(line)
                i += 1
            
            if new_lines != lines:
                cell['source'] = new_lines

# Write back
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"\n✅ Applied {fixes_applied} fixes to the notebook")
