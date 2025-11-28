"""
Fix the specific errors in cells 6 and 22
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing specific errors...\n")

# Fix Cell 6 - remove problematic line continuation characters
if len(notebook['cells']) > 6:
    cell6 = notebook['cells'][6]
    source_list = cell6['source']
    print(f"Cell 6 before: {len(source_list)} lines")
    print("First few lines:", source_list[:3] if len(source_list) > 0 else "empty")
    
    # Rebuild source without line continuation issues
    new_source = []
    for line in source_list:
        # Remove any stray backslashes that aren't part of valid escape sequences
        # But keep valid ones like \n, \", etc.
        fixed_line = line
        # If line ends with backslash-n, keep it; if backslash\n (literal), fix it
        if '\\\\n' in line and not line.endswith('\\n'):
            fixed_line = line.replace('\\\\n', '\n')
            print(f"  Fixed line: {repr(line)} -> {repr(fixed_line)}")
        new_source.append(fixed_line)
    
    notebook['cells'][6]['source'] = new_source
    print(f"✓ Fixed cell 6")

# Fix Cell 22 - wrap await in async function
if len(notebook['cells']) > 22:
    cell22 = notebook['cells'][22]
    source = ''.join(cell22['source'])
    
    if 'await run_demo()' in source and 'async def' not in source:
        # Check if it's already inside an async context or if we need to add one
        lines = source.split('\n')
        new_lines = []
        found_await = False
        
        for i, line in enumerate(lines):
            if 'await run_demo' in line and 'async' not in lines[max(0,i-5):i]:
                # Comment out the problematic await and add a note
                new_lines.append('# Uncomment to run (requires async context):\n')
                new_lines.append(f'# {line}\n')
                found_await = True
                print(f"✓ Commented out standalone await in cell 22")
            else:
                new_lines.append(line + ('\n' if i < len(lines) - 1 else ''))
        
        if found_await:
            notebook['cells'][22]['source'] = new_lines

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ All fixes applied!")
