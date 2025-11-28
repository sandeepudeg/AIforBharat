"""
Identify exactly which cells have the \n problem and show their content
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Checking cells for literal \\n in source...\n")

problem_cells = []

for idx, cell in enumerate(notebook['cells']):
    if 'source' in cell and isinstance(cell['source'], list):
        for line_num, line in enumerate(cell['source']):
            # Check for literal \n (the string contains backslash-n, not newline)
            if isinstance(line, str) and '\\n' in repr(line) and line != '\n':
                # Found a problem line
                problem_cells.append((idx, line_num, line, cell['cell_type']))
                print(f"Cell {idx} ({cell['cell_type']}), line {line_num}:")
                print(f"  Raw repr: {repr(line)}")
                print(f"  Content: {line[:80]}...")
                print()
                break  # Just show first problem line per cell

print(f"\n{'='*60}")
print(f"Found {len(problem_cells)} cells with literal \\n issues")
print(f"{'='*60}")
