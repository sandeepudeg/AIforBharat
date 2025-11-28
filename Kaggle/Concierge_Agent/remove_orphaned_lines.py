import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find the cell with run_demo function
for idx, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code" and any("await run_demo()" in line for line in cell["source"]):
        print(f"Found run_demo cell at index {idx}")
        
        # Remove the orphaned lines (523-528 in the original, which are the last 6 lines)
        # These are the indented lines after "await run_demo()"
        new_source = []
        found_await = False
        
        for line in cell["source"]:
            if "await run_demo()" in line:
                found_await = True
                new_source.append(line)
            elif found_await and line.strip().startswith("# Store interaction"):
                # Skip this and the following indented lines
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            elif found_await and "history.append({'user':" in line:
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            elif found_await and "session_service.set(" in line:
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            elif found_await and "# Simple evaluation" in line:
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            elif found_await and "score = evaluate_response" in line:
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            elif found_await and "logger.log_step('Evaluation'" in line:
                print(f"Skipping orphaned line: {line.strip()[:50]}")
                continue
            else:
                new_source.append(line)
        
        cell["source"] = new_source
        print(f"Removed {len(cell['source']) - len(new_source)} orphaned lines")
        break

# Save the fixed notebook
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4, ensure_ascii=False)

print("✅ Removed orphaned lines from Concierge_Agent.ipynb")
