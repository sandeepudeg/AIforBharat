"""
Verify the notebook structure and count MCP cells
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print(f"Total cells in notebook: {len(notebook['cells'])}")
print("\nCell structure:")

mcp_cells = []
for idx, cell in enumerate(notebook['cells']):
    cell_type = cell['cell_type']
    if cell_type == 'markdown':
        source = ''.join(cell['source'])
        title = source.split('\n')[0][:60]
        print(f"{idx}: [MARKDOWN] {title}")
        if 'MCP' in source or 'Model Context Protocol' in source:
            mcp_cells.append((idx, 'markdown', title))
    else:
        source = ''.join(cell['source'])
        first_line = source.split('\n')[0][:60]
        print(f"{idx}: [CODE] {first_line}")
        if 'mcp' in source.lower() or 'MCP' in source:
            mcp_cells.append((idx, 'code', first_line))

print(f"\n✅ MCP-related cells: {len(mcp_cells)}")
print("\nMCP cells details:")
for idx, cell_type, desc in mcp_cells:
    print(f"  Cell {idx} ({cell_type}): {desc}")

# Verify tool count
tool_related = [c for c in mcp_cells if 'tool' in c[2].lower() or 'call_tool' in ''.join(notebook['cells'][c[0]]['source'])]
print(f"\n✅ Tool-related MCP cells: {len(tool_related)}")
