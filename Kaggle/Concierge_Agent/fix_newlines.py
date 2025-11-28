"""
Fix literal \n characters in all notebook cells
The issue is that cell source has literal backslash-n instead of being split into array elements
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing literal \\n characters in all cells...\n")
fixes_count = 0

for idx, cell in enumerate(notebook['cells']):
    if 'source' in cell and isinstance(cell['source'], list):
        new_source = []
        changed = False
        
        for line in cell['source']:
            # Check if line has literal \n (backslash followed by n)
            if '\\n' in line and not line.endswith('\n'):
                # This line has literal \n that should be actual newlines
                # Split by literal \n and create separate lines
                parts = line.split('\\n')
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        # Not the last part, add newline
                        new_source.append(part + '\n')
                    else:
                        # Last part
                        if part:  # Only add if not empty
                            new_source.append(part)
                changed = True
            else:
                new_source.append(line)
        
        if changed:
            cell['source'] = new_source
            fixes_count += 1
            print(f"✓ Fixed cell {idx} ({cell['cell_type']})")

# Write back
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"\n✅ Fixed {fixes_count} cells with literal \\n characters")
