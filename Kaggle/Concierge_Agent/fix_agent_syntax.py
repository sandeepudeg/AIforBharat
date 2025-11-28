import json

# Load the notebook
notebook_path = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find the cell with agent definitions
for idx, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code" and any("planning_agent = Agent(" in line for line in cell["source"]):
        print(f"Found agent definition cell at index {idx}")
        
        # The problematic lines are those that have tool.append() inside Agent() constructors
        # We need to remove lines 234-236, 282-283, and the duplicate registrations at the end
        
        new_source = []
        skip_next = False
        
        for i, line in enumerate(cell["source"]):
            # Skip lines that are comments about registering tools inside Agent constructors
            if "# Register additional custom tools for" in line and i < 300:
                # Check if next lines are .tools.append() - if so, skip them
                j = i + 1
                while j < len(cell["source"]) and ".tools.append(" in cell["source"][j]:
                    j += 1
                # Skip from i to j-1
                if j > i + 1:
                    print(f"Skipping lines {i}-{j-1}: invalid tool registrations inside Agent constructor")
                    # Mark to skip
                    for k in range(i, j):
                        cell["source"][k] = "<<<SKIP>>>"
        
        # Now filter out the marked lines
        new_source = [line for line in cell["source"] if line != "<<<SKIP>>>"]
        
        # Also remove the duplicate tool registrations after the print statement (lines 301-334)
        final_source = []
        found_print = False
        for line in new_source:
            if 'print("✅ Sub-agents created' in line:
                found_print = True
                final_source.append(line)
            elif found_print and (".tools.append(" in line or "# Register additional" in line):
                # Skip these duplicate lines
                continue
            else:
                final_source.append(line)
        
        cell["source"] = final_source
        print(f"Removed {len(cell['source']) - len(final_source)} invalid lines")
        break

# Save the fixed notebook
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4, ensure_ascii=False)

print("✅ Fixed agent definition syntax in Concierge_Agent.ipynb")
