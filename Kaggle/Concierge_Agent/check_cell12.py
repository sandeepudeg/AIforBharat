import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Count code cells and check cell 12
code_cell_count = 0
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        code_cell_count += 1
        if i == 12:
            print(f"Cell 12 is code cell #{code_cell_count}")
            print(f"First 5 lines of cell 12:")
            for j, line in enumerate(cell["source"][:5]):
                print(f"  {j}: {line[:70]}")

print(f"\nTotal code cells: {code_cell_count}")
