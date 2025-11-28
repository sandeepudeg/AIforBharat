"""
Add final usage example cell for MCP
"""
import json

# Read the notebook
with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find where to insert (after tools grouping)
insert_position = None
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and 'source' in cell:
        source_text = ''.join(cell['source'])
        if 'Total: {len(PLANNING_TOOLS)' in source_text:
            insert_position = idx + 1
            break

if insert_position is None:
    print("Could not find tools grouping cell.")
    exit(1)

# Create example usage markdown
usage_example_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## MCP Usage Example\\n",
        "\\n",
        "Below is an example of how the MCP server would be used in a production environment.\\n",
        "This demonstrates the request/response flow for MCP tools."
    ]
}

# Create usage example cell
usage_example_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Example: How MCP tools would be called\\n",
        "# This simulates what happens when an MCP client calls a tool\\n",
        "\\n",
        "async def mcp_example_usage():\\n",
        "    \\\"\\\"\\\"Demonstrates MCP tool calling pattern\\\"\\\"\\\"\\n",
        "    \\n",
        "    # Example 1: Suggest destinations\\n",
        "    print(\\\"=== Example 1: Suggest Destinations ===\")\\n",
        "    result = await mcp_server._call_tool_handler(\\n",
        "        \\\"suggest_destinations\\\",\\n",
        "        {\\n",
        "            \\\"budget\\\": \\\"medium\\\",\\n",
        "            \\\"season\\\": \\\"autumn\\\",\\n",
        "            \\\"interests\\\": \\\"culture, food\\\"\\n",
        "        }\\n",
        "    )\\n",
        "    print(f\\\"Result: {result[0].text}\\\\n\\\")\\n",
        "    \\n",
        "    # Example 2: Create itinerary\\n",
        "    print(\\\"=== Example 2: Create Itinerary ===\")\\n",
        "    result = await mcp_server._call_tool_handler(\\n",
        "        \\\"create_itinerary\\\",\\n",
        "        {\\n",
        "            \\\"destination\\\": \\\"Kyoto\\\",\\n",
        "            \\\"days\\\": 5\\n",
        "        }\\n",
        "    )\\n",
        "    print(f\\\"Result: {result[0].text}\\\\n\\\")\\n",
        "    \\n",
        "    # Example 3: Convert currency\\n",
        "    print(\\\"=== Example 3: Convert Currency ===\")\\n",
        "    result = await mcp_server._call_tool_handler(\\n",
        "        \\\"convert_currency\\\",\\n",
        "        {\\n",
        "            \\\"amount\\\": 1000,\\n",
        "            \\\"from_curr\\\": \\\"USD\\\",\\n",
        "            \\\"to_curr\\\": \\\"JPY\\\"\\n",
        "        }\\n",
        "    )\\n",
        "    print(f\\\"Result: {result[0].text}\\\\n\\\")\\n",
        "    \\n",
        "    # Example 4: Search hotels\\n",
        "    print(\\\"=== Example 4: Search Hotels ===\")\\n",
        "    result = await mcp_server._call_tool_handler(\\n",
        "        \\\"search_hotels\\\",\\n",
        "        {\\n",
        "            \\\"city\\\": \\\"Kyoto\\\",\\n",
        "            \\\"check_in\\\": \\\"2025-12-01\\\"\\n",
        "        }\\n",
        "    )\\n",
        "    print(f\\\"Result: {result[0].text}\\\\n\\\")\\n",
        "    \\n",
        "    print(\\\"✅ All MCP examples completed successfully!\\\")\\n",
        "\\n",
        "# Run the examples\\n",
        "# Uncomment to test:\\n",
        "# await mcp_example_usage()\\n",
        "\\n",
        "print(\\\"📝 MCP usage examples ready. Uncomment the last line to run.\\\")\\n"
    ]
}

# Create markdown about deployment
deployment_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Deploying the MCP Server\\n",
        "\\n",
        "To deploy this as a production MCP server:\\n",
        "\\n",
        "### 1. **Extract to Python Module**\\n",
        "```bash\\n",
        "# Convert notebook cells to a standalone mcp_server.py\\n",
        "jupyter nbconvert --to script Concierge_Agent.ipynb\\n",
        "# Then extract the MCP server code to mcp_server.py\\n",
        "```\\n",
        "\\n",
        "### 2. **Run the MCP Server**\\n",
        "```bash\\n",
        "# The MCP server uses stdio transport\\n",
        "python mcp_server.py\\n",
        "```\\n",
        "\\n",
        "### 3. **Connect from ADK**\\n",
        "```python\\n",
        "from google.adk.tools.mcp_tool.mcp_toolset import McpToolset\\n",
        "from mcp import StdioServerParameters\\n",
        "\\n",
        "toolset = McpToolset(\\n",
        "    server_params=StdioServerParameters(\\n",
        "        command=\\\"python\\\",\\n",
        "        args=[\\\"mcp_server.py\\\"],\\n",
        "        env=None\\n",
        "    )\\n",
        ")\\n",
        "\\n",
        "# Use in agent\\n",
        "agent = Agent(\\n",
        "    name=\\\"MyAgent\\\",\\n",
        "    tools=[toolset],\\n",
        "    ...\\n",
        ")\\n",
        "```\\n",
        "\\n",
        "### 4. **Use MCP Inspector (Optional)**\\n",
        "```bash\\n",
        "# Install MCP inspector\\n",
        "npx @modelcontextprotocol/inspector python mcp_server.py\\n",
        "```\\n",
        "\\n",
        "This will open a web interface to browse and test your MCP tools interactively."
    ]
}

# Insert cells
for i, cell in enumerate([usage_example_markdown, usage_example_cell, deployment_markdown]):
    notebook['cells'].insert(insert_position + i, cell)

# Write back
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully added 3 usage example and deployment cells")
print(f"📊 Total MCP-related cells added: 10")
