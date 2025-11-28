import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Count code cells
code_cells = [cell for cell in nb["cells"] if cell["cell_type"] == "code"]
print(f"Total code cells: {len(code_cells)}")

# Check if cell 12 is a code cell
cell12 = nb["cells"][12]
print(f"\nCell 12 type: {cell12['cell_type']}")
print(f"Cell 12 first 3 lines:")
for i, line in enumerate(cell12["source"][:3]):
    print(f"  {i}: {line[:60]}")

# Check if verify_notebook.py would extract it
if cell12["cell_type"] == "code":
    print("\n✅ Cell 12 should be extracted by verify_notebook.py")
else:
    print("\n❌ Cell 12 is not a code cell!")
