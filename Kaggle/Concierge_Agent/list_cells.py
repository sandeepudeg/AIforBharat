import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}\n")

for i, cell in enumerate(nb['cells']):
    cell_type = cell['cell_type']
    if cell['source']:
        first_line = cell['source'][0][:80]
    else:
        first_line = "(empty)"
    print(f"Cell {i}: {cell_type:10} - {first_line}")
