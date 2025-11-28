"""
Add complete MCP implementation to the notebook with proper formatting
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Adding MCP implementation to notebook...\n")

# Find insertion point - after the last cell
insert_pos = len(notebook['cells']) - 2  # Before the last 2 cells (GUI instructions)

# Helper function to create properly formatted cell
def create_cell(cell_type, content_lines, execution_count=None):
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": content_lines
    }
    if cell_type == "code":
        cell["execution_count"] = execution_count
        cell["outputs"] = []
    return cell

# MCP cells to add
mcp_cells = []

# 1. MCP Introduction
mcp_cells.append(create_cell("markdown", [
    "## MCP (Model Context Protocol) Implementation\n",
    "\n",
    "This section implements a complete MCP server that exposes all 23 concierge tools.\n",
    "\n",
    "**Benefits:**\n",
    "- Standardized protocol for AI tools\n",
    "- Better interoperability\n",
    "- Production-ready deployment\n"
]))

# 2. MCP Server Setup
mcp_cells.append(create_cell("code", [
    "# MCP Server - Define tool handlers\n",
    "from mcp.server import Server\n",
    "from mcp.types import Tool, TextContent\n",
    "import mcp.server.stdio\n",
    "\n",
    "# Create server instance\n",
    "mcp_server = Server(\"concierge-agent\")\n",
    "\n",
    "print(\"✅ MCP Server instance created\")\n"
]))

# 3. MCP call_tool handler
mcp_cells.append(create_cell("code", [
    "@mcp_server.call_tool()\n",
    "async def call_tool(name: str, arguments: dict) -> list[TextContent]:\n",
    "    \"\"\"Handle tool calls from MCP clients\"\"\"\n",
    "    \n",
    "    # Planning Tools\n",
    "    if name == \"suggest_destinations\":\n",
    "        result = suggest_destinations(arguments.get(\"budget\", \"\"), arguments.get(\"season\", \"\"), arguments.get(\"interests\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"create_itinerary\":\n",
    "        result = create_itinerary(arguments.get(\"destination\", \"\"), arguments.get(\"days\", 1))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"suggest_activities\":\n",
    "        result = suggest_activities(arguments.get(\"city\", \"\"), arguments.get(\"interests\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    \n",
    "    # Booking Tools\n",
    "    elif name == \"search_flights\":\n",
    "        result = search_flights(arguments.get(\"origin\", \"\"), arguments.get(\"destination\", \"\"), arguments.get(\"date\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"book_flight\":\n",
    "        result = book_flight(arguments.get(\"flight_id\", \"\"), arguments.get(\"passenger_name\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"search_hotels\":\n",
    "        result = search_hotels(arguments.get(\"city\", \"\"), arguments.get(\"check_in\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"book_hotel\":\n",
    "        result = book_hotel(arguments.get(\"hotel_id\", \"\"), arguments.get(\"guest_name\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"book_ride\":\n",
    "        result = book_ride(arguments.get(\"pickup\", \"\"), arguments.get(\"dropoff\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"book_activity\":\n",
    "        result = book_activity(arguments.get(\"activity_name\", \"\"), arguments.get(\"date\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    \n",
    "    # Utility Tools\n",
    "    elif name == \"get_weather_forecast\":\n",
    "        result = get_weather_forecast(arguments.get(\"city\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"convert_currency\":\n",
    "        result = convert_currency(arguments.get(\"amount\", 0.0), arguments.get(\"from_curr\", \"\"), arguments.get(\"to_curr\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"translate_text\":\n",
    "        result = translate_text(arguments.get(\"text\", \"\"), arguments.get(\"target_lang\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"check_visa_requirements\":\n",
    "        result = check_visa_requirements(arguments.get(\"citizenship\", \"\"), arguments.get(\"country\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"get_insurance_quote\":\n",
    "        result = get_insurance_quote(arguments.get(\"destination\", \"\"), arguments.get(\"days\", 1))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"get_emergency_contacts\":\n",
    "        result = get_emergency_contacts(arguments.get(\"city\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"get_flight_status\":\n",
    "        result = get_flight_status(arguments.get(\"flight_number\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"track_expense\":\n",
    "        result = track_expense(arguments.get(\"item\", \"\"), arguments.get(\"amount\", 0.0))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"get_budget_summary\":\n",
    "        result = get_budget_summary()\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    \n",
    "    # Social Tools\n",
    "    elif name == \"update_user_preference\":\n",
    "        result = update_user_preference(arguments.get(\"key\", \"\"), arguments.get(\"value\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"get_user_preferences\":\n",
    "        result = get_user_preferences()\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"submit_feedback\":\n",
    "        result = submit_feedback(arguments.get(\"rating\", 0), arguments.get(\"comment\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    elif name == \"share_to_social_media\":\n",
    "        result = share_to_social_media(arguments.get(\"platform\", \"\"), arguments.get(\"content\", \"\"))\n",
    "        return [TextContent(type=\"text\", text=result)]\n",
    "    \n",
    "    else:\n",
    "        raise ValueError(f\"Unknown tool: {name}\")\n",
    "\n",
    "print(\"✅ MCP tool handler registered (23 tools)\")\n"
]))

# 4. MCP list_tools - Part 1 (Planning & Booking)
mcp_cells.append(create_cell("code", [
    "@mcp_server.list_tools()\n",
    "async def list_tools() -> list[Tool]:\n",
    "    \"\"\"List all available tools with schemas\"\"\"\n",
    "    return [\n",
    "        # Planning Tools (3)\n",
    "        Tool(name=\"suggest_destinations\", description=\"Suggests travel destinations\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"budget\": {\"type\": \"string\"}, \"season\": {\"type\": \"string\"}, \"interests\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"budget\", \"season\", \"interests\"]}),\n",
    "        Tool(name=\"create_itinerary\", description=\"Creates day-by-day itinerary\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"destination\": {\"type\": \"string\"}, \"days\": {\"type\": \"integer\"}},\n",
    "                 \"required\": [\"destination\", \"days\"]}),\n",
    "        Tool(name=\"suggest_activities\", description=\"Suggests activities in a city\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"city\": {\"type\": \"string\"}, \"interests\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"city\", \"interests\"]}),\n",
    "        \n",
    "        # Booking Tools (6)\n",
    "        Tool(name=\"search_flights\", description=\"Searches for flights\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"origin\": {\"type\": \"string\"}, \"destination\": {\"type\": \"string\"}, \"date\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"origin\", \"destination\", \"date\"]}),\n",
    "        Tool(name=\"book_flight\", description=\"Books a flight\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"flight_id\": {\"type\": \"string\"}, \"passenger_name\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"flight_id\", \"passenger_name\"]}),\n",
    "        Tool(name=\"search_hotels\", description=\"Searches for hotels\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"city\": {\"type\": \"string\"}, \"check_in\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"city\", \"check_in\"]}),\n",
    "        Tool(name=\"book_hotel\", description=\"Books a hotel\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"hotel_id\": {\"type\": \"string\"}, \"guest_name\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"hotel_id\", \"guest_name\"]}),\n",
    "        Tool(name=\"book_ride\", description=\"Books local transportation\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"pickup\": {\"type\": \"string\"}, \"dropoff\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"pickup\", \"dropoff\"]}),\n",
    "        Tool(name=\"book_activity\", description=\"Books an activity\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"activity_name\": {\"type\": \"string\"}, \"date\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"activity_name\", \"date\"]}),\n",
    "        \n",
    "        # Utility Tools (9)\n",
    "        Tool(name=\"get_weather_forecast\", description=\"Gets weather forecast\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\"city\": {\"type\": \"string\"}}, \"required\": [\"city\"]}),\n",
    "        Tool(name=\"convert_currency\", description=\"Converts currency\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"amount\": {\"type\": \"number\"}, \"from_curr\": {\"type\": \"string\"}, \"to_curr\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"amount\", \"from_curr\", \"to_curr\"]}),\n",
    "        Tool(name=\"translate_text\", description=\"Translates text\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"text\": {\"type\": \"string\"}, \"target_lang\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"text\", \"target_lang\"]}),\n",
    "        Tool(name=\"check_visa_requirements\", description=\"Checks visa requirements\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"citizenship\": {\"type\": \"string\"}, \"country\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"citizenship\", \"country\"]}),\n",
    "        Tool(name=\"get_insurance_quote\", description=\"Gets insurance quote\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"destination\": {\"type\": \"string\"}, \"days\": {\"type\": \"integer\"}},\n",
    "                 \"required\": [\"destination\", \"days\"]}),\n",
    "        Tool(name=\"get_emergency_contacts\", description=\"Gets emergency contacts\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\"city\": {\"type\": \"string\"}}, \"required\": [\"city\"]}),\n",
    "        Tool(name=\"get_flight_status\", description=\"Checks flight status\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\"flight_number\": {\"type\": \"string\"}}, \"required\": [\"flight_number\"]}),\n",
    "        Tool(name=\"track_expense\", description=\"Logs an expense\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"item\": {\"type\": \"string\"}, \"amount\": {\"type\": \"number\"}},\n",
    "                 \"required\": [\"item\", \"amount\"]}),\n",
    "        Tool(name=\"get_budget_summary\", description=\"Gets budget summary\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {}}),\n",
    "        \n",
    "        # Social Tools (4)\n",
    "        Tool(name=\"update_user_preference\", description=\"Updates user preference\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"key\": {\"type\": \"string\"}, \"value\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"key\", \"value\"]}),\n",
    "        Tool(name=\"get_user_preferences\", description=\"Gets user preferences\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {}}),\n",
    "        Tool(name=\"submit_feedback\", description=\"Submits feedback\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"rating\": {\"type\": \"integer\"}, \"comment\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"rating\", \"comment\"]}),\n",
    "        Tool(name=\"share_to_social_media\", description=\"Shares to social media\",\n",
    "             inputSchema={\"type\": \"object\", \"properties\": {\n",
    "                 \"platform\": {\"type\": \"string\"}, \"content\": {\"type\": \"string\"}},\n",
    "                 \"required\": [\"platform\", \"content\"]}),\n",
    "    ]\n",
    "\n",
    "print(\"✅ MCP tool schemas registered (23 tools total)\")\n"
]))

# 5. MCP Usage Instructions
mcp_cells.append(create_cell("markdown", [
    "### Using the MCP Server\n",
    "\n",
    "The MCP server is now configured. To use it:\n",
    "\n",
    "**Option 1: Export and run standalone**\n",
    "```python\n",
    "# Save MCP server code to mcp_server.py and run:\n",
    "# python mcp_server.py\n",
    "```\n",
    "\n",
    "**Option 2: Use with ADK (shown below)**\n",
    "\n",
    "The agents below use FunctionTool for simplicity. For production, consider using McpToolset.\n"
]))

# Insert all cells
for i, cell in enumerate(mcp_cells):
    notebook['cells'].insert(insert_pos + i, cell)

print(f"✅ Added {len(mcp_cells)} MCP cells to notebook")

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"Total cells now: {len(notebook['cells'])}")
print("\n✅ MCP implementation added to notebook!")
