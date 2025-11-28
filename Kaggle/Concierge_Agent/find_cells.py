import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find which cells contain what
code_cell_num = 0
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        code_cell_num += 1
        first_line = cell["source"][0] if cell["source"] else "(empty)"
        
        if "run_demo" in first_line or (len(cell["source"]) > 5 and any("async def run_demo" in line for line in cell["source"])):
            print(f"Cell {i} (code cell #{code_cell_num}): Contains run_demo")
            print(f"  First line: {first_line[:60]}")
        
        if "Missing Feature" in first_line:
            print(f"Cell {i} (code_cell #{code_cell_num}): Missing Features")
            print(f"  First line: {first_line[:60]}")
