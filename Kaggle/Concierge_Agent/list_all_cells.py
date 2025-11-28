import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells in notebook: {len(nb['cells'])}\n")

# List all cells with their types
for i, cell in enumerate(nb["cells"]):
    cell_type = cell["cell_type"]
    if cell["source"]:
        first_line = cell["source"][0][:60]
    else:
        first_line = "(empty)"
    
    marker = " <-- MISSING FEATURES" if "Missing Feature" in first_line else ""
    print(f"Cell {i:2d}: {cell_type:10} - {first_line}{marker}")
