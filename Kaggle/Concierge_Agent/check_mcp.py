import json

# Load the notebook
with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the missing features cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and cell['source']:
        if 'Missing Feature' in cell['source'][0]:
            print(f"Found missing features cell at index {i}")
            print("\nFirst 10 lines:")
            for j, line in enumerate(cell['source'][:10]):
                print(f"{j}: {line[:80]}")
            break
