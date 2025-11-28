import json

# Load the notebook
with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find and update the missing features cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and cell['source']:
        if 'Missing Feature' in cell['source'][0]:
            print(f"Found missing features cell at index {i}")
            
            # Update the MCP comment
            for j, line in enumerate(cell['source']):
                if 'Multi‑Component Process' in line or 'Multi-Component Process' in line:
                    old_line = line
                    cell['source'][j] = line.replace('Multi‑Component Process', 'Model Context Protocol').replace('Multi-Component Process', 'Model Context Protocol')
                    print(f"Updated line {j}:")
                    print(f"  Old: {old_line[:80]}")
                    print(f"  New: {cell['source'][j][:80]}")
            break

# Save the updated notebook
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=4, ensure_ascii=False)

print("\n✅ Updated MCP comment to 'Model Context Protocol'")
