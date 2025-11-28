import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Fix all code cells to ensure proper line endings
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        if isinstance(source, list):
            # Ensure each line ends with \n
            fixed_source = []
            for line in source:
                if not line.endswith("\n"):
                    fixed_source.append(line + "\n")
                else:
                    fixed_source.append(line)
            cell["source"] = fixed_source

# Save the fixed notebook
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4, ensure_ascii=False)

print("✅ Fixed all cell line endings in Concierge_Agent.ipynb")
