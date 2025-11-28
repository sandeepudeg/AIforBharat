import json
import asyncio
import os

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Extract all code cells
code_cells = [cell["source"] for cell in nb["cells"] if cell["cell_type"] == "code"]

# Build the Python script
full_code = ""
for cell_lines in code_cells:
    for line in cell_lines:
        # Skip Jupyter magic commands
        if line.strip().startswith("!") or line.strip().startswith("%"):
            continue
        # Replace await run_demo() with asyncio.run(run_demo())
        if "await run_demo()" in line:
            line = "asyncio.run(run_demo())\n"
        # Ensure line ends with newline
        if not line.endswith("\n"):
            line = line + "\n"
        full_code += line

# Write to temp file
with open("temp_run.py", "w", encoding="utf-8") as f:
    f.write(full_code)

print("Extracted code to temp_run.py. Running...")
os.system("python temp_run.py")
