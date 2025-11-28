import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find the missing features cell and the run_demo cell
missing_features_idx = None
run_demo_idx = None

for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        first_line = cell["source"][0] if cell["source"] else ""
        
        if "Missing Feature" in first_line:
            missing_features_idx = i
            print(f"Found missing features cell at index {i}")
        
        if any("async def run_demo" in line for line in cell["source"]):
            run_demo_idx = i
            print(f"Found run_demo cell at index {i}")

if missing_features_idx and run_demo_idx:
    if missing_features_idx > run_demo_idx:
        print(f"\n❌ Missing features cell ({missing_features_idx}) is AFTER run_demo cell ({run_demo_idx})")
        print("Moving missing features cell to before run_demo...")
        
        # Remove the missing features cell from its current position
        missing_cell = nb["cells"].pop(missing_features_idx)
        
        # Insert it before the run_demo cell
        nb["cells"].insert(run_demo_idx, missing_cell)
        
        # Save the notebook
        with open(notebook_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Moved missing features cell from position {missing_features_idx} to position {run_demo_idx}")
    else:
        print(f"\n✅ Missing features cell ({missing_features_idx}) is already BEFORE run_demo cell ({run_demo_idx})")
