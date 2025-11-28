"""
Add cell for MCP integration with ADK agents using McpToolset
"""
import json

# Read the notebook
with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find where we added MCP cells (should have "MCP Tool definitions registered" message)
insert_position = None
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and 'source' in cell:
        source_text = ''.join(cell['source'])
        if 'MCP Tool definitions registered' in source_text:
            insert_position = idx + 2  # After the markdown explaining MCP+ADK
            break

if insert_position is None:
    print("Could not find MCP cells. Ensure add_mcp_cells.py was run first.")
    exit(1)

# Create cell for using MCP with agents via McpToolset
mcp_with_agents_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Create MCP Toolset for use with ADK agents\\n",
        "import sys\\n",
        "import subprocess\\n",
        "\\n",
        "# Function to start MCP server as a subprocess\\n",
        "async def start_mcp_server():\\n",
        "    \\\"\\\"\\\"Start the MCP server via stdio\\\"\\\"\\\"\\n",
        "    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):\\n",
        "        await mcp_server.run(\\n",
        "            read_stream,\\n",
        "            write_stream,\\n",
        "            mcp_server.create_initialization_options()\\n",
        "        )\\n",
        "\\n",
        "# Create connection parameters for MCP server\\n",
        "mcp_connection_params = StdioConnectionParams(\\n",
        "    command=sys.executable,  # Python executable\\n",
        "    args=[\\\"-c\\\", \\\"\\\"\\\"\\n",
        "import asyncio\\n",
        "from mcp.server import Server\\n",
        "import mcp.server.stdio\\n",
        "\\n",
        "# Note: In production, you would import the actual server instance\\n",
        "# For this demo, we'll reference the server created above\\n",
        "print('MCP Server starting via stdio...', file=sys.stderr)\\n",
        "\\\"\\\"\\\"\\n",
        "    ],\\n",
        "    env=None\\n",
        ")\\n",
        "\\n",
        "# Create McpToolset that connects to our server\\n",
        "# Note: McpToolset requires the server to be running via stdio\\n",
        "async def create_mcp_toolset():\\n",
        "    \\\"\\\"\\\"Create an MCP toolset for ADK agents\\\"\\\"\\\"\\n",
        "    try:\\n",
        "        toolset = McpToolset(\\n",
        "            server_params=StdioServerParameters(\\n",
        "                command=sys.executable,\\n",
        "                args=[\\\"-m\\\", \\\"mcp_server\\\"],  # Would need mcp_server.py as module\\n",
        "                env=None\\n",
        "            )\\n",
        "        )\\n",
        "        return toolset\\n",
        "    except Exception as e:\\n",
        "        print(f\\\"Note: McpToolset requires a separate server process. Error: {e}\\\")\\n",
        "        return None\\n",
        "\\n",
        "print(\\\"✅ MCP integration functions defined.\\\")\\n",
        "print(\\\"📝 Note: For production use, run the MCP server as a separate process.\\\")\\n"
    ]
}

# Create alternative cell showing hybrid approach (FunctionTool + MCP documentation)
hybrid_approach_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Hybrid Approach: FunctionTool with MCP Documentation\\n",
        "\\n",
        "**Note**: Running an MCP server within a Jupyter notebook has limitations since MCP typically runs as a separate process. \\n",
        "\\n",
        "For this notebook, we'll continue using `FunctionTool` wrappers (as originally defined), but we've documented the MCP interface above. This provides:\\n",
        "\\n",
        "1. **Immediate usability** - The agents work directly in the notebook\\n",
        "2. **MCP readiness** - The tool schemas and handlers are defined for future MCP deployment\\n",
        "3. **Clear migration path** - When deploying to production, tools can be exposed via MCP server\\n",
        "\\n",
        "**For production deployment:**\\n",
        "- Export the MCP server code to a separate `mcp_server.py` file\\n",
        "- Run it as: `python mcp_server.py` (uses stdio transport)\\n",
        "- Connect ADK agents using `McpToolset` with the server process\\n",
        "\\n",
        "The sub-agents below will continue using `FunctionTool` for in-notebook execution."
    ]
}

# Create a cell showing how tools are currently grouped (no change to existing agents)
tools_grouping_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Tool groupings for reference (matches MCP tool organization)\\n",
        "PLANNING_TOOLS = ['suggest_destinations', 'create_itinerary', 'suggest_activities']\\n",
        "BOOKING_TOOLS = ['search_flights', 'book_flight', 'search_hotels', 'book_hotel', 'book_ride', 'book_activity']\\n",
        "UTILITY_TOOLS = ['get_weather_forecast', 'convert_currency', 'translate_text', \\n",
        "                 'check_visa_requirements', 'get_insurance_quote', 'get_emergency_contacts',\\n",
        "                 'get_flight_status', 'track_expense', 'get_budget_summary']\\n",
        "SOCIAL_TOOLS = ['update_user_preference', 'get_user_preferences', 'submit_feedback', 'share_to_social_media']\\n",
        "\\n",
        "print(f\\\"Planning Tools: {len(PLANNING_TOOLS)}\\\")\\n",
        "print(f\\\"Booking Tools: {len(BOOKING_TOOLS)}\\\")\\n",
        "print(f\\\"Utility Tools: {len(UTILITY_TOOLS)}\\\")\\n",
        "print(f\\\"Social Tools: {len(SOCIAL_TOOLS)}\\\")\\n",
        "print(f\\\"Total: {len(PLANNING_TOOLS) + len(BOOKING_TOOLS) + len(UTILITY_TOOLS) + len(SOCIAL_TOOLS)} tools\\\")\\n"
    ]
}

# Insert cells
for i, cell in enumerate([mcp_with_agents_cell, hybrid_approach_markdown, tools_grouping_cell]):
    notebook['cells'].insert(insert_position + i, cell)

# Write back
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully added 3 more cells for MCP integration")
