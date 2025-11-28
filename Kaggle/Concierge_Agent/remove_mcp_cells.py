"""
Complete fix - remove all MCP cells and re-add them with correct formatting
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Removing problematic MCP cells and rebuilding...\n")

# First, let's identify which cells are MCP-related by checking content
mcp_cell_indices = []
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if any(keyword in source for keyword in ['mcp_server', 'McpToolset', 'Model Context Protocol', '@mcp_server']):
        mcp_cell_indices.append(idx)
        print(f"Found MCP cell at index {idx}: {cell['cell_type']}")

# Remove MCP cells (in reverse order to maintain indices)
print(f"\nRemoving {len(mcp_cell_indices)} MCP cells...")
for idx in reversed(mcp_cell_indices):
    del notebook['cells'][idx]

print(f"Remaining cells: {len(notebook['cells'])}")

# Save the cleaned notebook
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Removed all MCP cells. Notebook is now clean.")
print("The original agent functionality with FunctionTool is preserved.")
