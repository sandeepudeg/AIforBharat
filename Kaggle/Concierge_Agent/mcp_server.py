"""
Concierge Agent MCP Server

This MCP server exposes all 23 concierge tools through the Model Context Protocol.
Run with: python mcp_server.py
"""

import json
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

# --- Planning Tools ---
def suggest_destinations(budget: str, season: str, interests: str):
    """Suggests travel destinations based on user preferences."""
    return json.dumps([
        {"city": "Kyoto", "country": "Japan", "reason": "Autumn foliage", "cost": "Medium"},
        {"city": "Reykjavik", "country": "Iceland", "reason": "Northern lights", "cost": "High"},
        {"city": "Bali", "country": "Indonesia", "reason": "Beaches", "cost": "Low"}
    ])

def create_itinerary(destination: str, days: int):
    """Creates a day-by-day itinerary."""
    return json.dumps({f"Day {i}": f"Activity in {destination}" for i in range(1, days + 1)})

def suggest_activities(city: str, interests: str):
    """Suggests activities in a city."""
    return json.dumps(["Museum Tour", "Hiking", "Food Tasting"])

# --- Booking Tools ---
def search_flights(origin: str, destination: str, date: str):
    """Searches for flights."""
    return json.dumps([{"airline": "AirFly", "price": 500, "id": "FL123"}])

def book_flight(flight_id: str, passenger_name: str):
    """Books a flight."""
    return json.dumps({"status": "confirmed", "ref": "BK-FL-001"})

def search_hotels(city: str, check_in: str):
    """Searches for hotels."""
    return json.dumps([{"name": "Grand Hotel", "price": 200, "id": "HTL1"}])

def book_hotel(hotel_id: str, guest_name: str):
    """Books a hotel."""
    return json.dumps({"status": "confirmed", "ref": "BK-HTL-001"})

def book_ride(pickup: str, dropoff: str):
    """Books a local ride."""
    return json.dumps({"driver": "John", "eta": "5 mins"})

def book_activity(activity_name: str, date: str):
    """Books an activity ticket."""
    return json.dumps({"status": "confirmed", "ticket": "ACT-001"})

# --- Utility Tools ---
def get_weather_forecast(city: str):
    """Gets weather forecast."""
    return "Sunny, 25°C"

def convert_currency(amount: float, from_curr: str, to_curr: str):
    """Converts currency."""
    return f"{amount * 1.1:.2f} {to_curr}"

def translate_text(text: str, target_lang: str):
    """Translates text."""
    return f"[Translated to {target_lang}]: {text}"

def check_visa_requirements(citizenship: str, country: str):
    """Checks visa requirements."""
    return "Visa-free for 90 days (Simulated)"

def get_insurance_quote(destination: str, days: int):
    """Gets travel insurance quote."""
    return "$50 Standard Plan"

def get_emergency_contacts(city: str):
    """Gets emergency contacts."""
    return "Police: 911, Embassy: +1-555-0199"

def get_flight_status(flight_number: str):
    """Checks flight status."""
    return "On Time"

def track_expense(item: str, amount: float):
    """Logs an expense."""
    return "Expense logged."

def get_budget_summary():
    """Returns total expenses."""
    return "Total: $150"

# --- Social Tools ---
user_prefs = {}

def update_user_preference(key: str, value: str):
    """Updates user preference."""
    user_prefs[key] = value
    return "Updated."

def get_user_preferences():
    """Gets user preferences."""
    return json.dumps(user_prefs)

def submit_feedback(rating: int, comment: str):
    """Submits feedback."""
    return "Feedback received."

def share_to_social_media(platform: str, content: str):
    """Shares content to social media."""
    return f"Shared to {platform}."


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Create MCP server instance
mcp_server = Server("concierge-agent")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return [
        # Planning Tools
        Tool(
            name="suggest_destinations",
            description="Suggests travel destinations based on budget, season, and interests",
            inputSchema={
                "type": "object",
                "properties": {
                    "budget": {"type": "string", "description": "Budget level (low/medium/high)"},
                    "season": {"type": "string", "description": "Travel season"},
                    "interests": {"type": "string", "description": "User interests"}
                },
                "required": ["budget", "season", "interests"]
            }
        ),
        Tool(
            name="create_itinerary",
            description="Creates a day-by-day itinerary for a destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "days": {"type": "integer"}
                },
                "required": ["destination", "days"]
            }
        ),
        Tool(
            name="suggest_activities",
            description="Suggests activities in a city based on interests",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "interests": {"type": "string"}
                },
                "required": ["city", "interests"]
            }
        ),
        # Booking Tools
        Tool(
            name="search_flights",
            description="Searches for available flights",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["origin", "destination", "date"]
            }
        ),
        Tool(
            name="book_flight",
            description="Books a flight",
            inputSchema={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string"},
                    "passenger_name": {"type": "string"}
                },
                "required": ["flight_id", "passenger_name"]
            }
        ),
        Tool(
            name="search_hotels",
            description="Searches for available hotels",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "check_in": {"type": "string"}
                },
                "required": ["city", "check_in"]
            }
        ),
        Tool(
            name="book_hotel",
            description="Books a hotel",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotel_id": {"type": "string"},
                    "guest_name": {"type": "string"}
                },
                "required": ["hotel_id", "guest_name"]
            }
        ),
        Tool(
            name="book_ride",
            description="Books a local transportation ride",
            inputSchema={
                "type": "object",
                "properties": {
                    "pickup": {"type": "string"},
                    "dropoff": {"type": "string"}
                },
                "required": ["pickup", "dropoff"]
            }
        ),
        Tool(
            name="book_activity",
            description="Books an activity or tour",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["activity_name", "date"]
            }
        ),
        # Utility Tools
        Tool(
            name="get_weather_forecast",
            description="Gets weather forecast for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        ),
        Tool(
            name="convert_currency",
            description="Converts currency from one to another",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_curr": {"type": "string"},
                    "to_curr": {"type": "string"}
                },
                "required": ["amount", "from_curr", "to_curr"]
            }
        ),
        Tool(
            name="translate_text",
            description="Translates text to target language",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "target_lang": {"type": "string"}
                },
                "required": ["text", "target_lang"]
            }
        ),
        Tool(
            name="check_visa_requirements",
            description="Checks visa requirements for a country",
            inputSchema={
                "type": "object",
                "properties": {
                    "citizenship": {"type": "string"},
                    "country": {"type": "string"}
                },
                "required": ["citizenship", "country"]
            }
        ),
        Tool(
            name="get_insurance_quote",
            description="Gets travel insurance quote",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "days": {"type": "integer"}
                },
                "required": ["destination", "days"]
            }
        ),
        Tool(
            name="get_emergency_contacts",
            description="Gets emergency contacts for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        ),
        Tool(
            name="get_flight_status",
            description="Checks flight status",
            inputSchema={
                "type": "object",
                "properties": {"flight_number": {"type": "string"}},
                "required": ["flight_number"]
            }
        ),
        Tool(
            name="track_expense",
            description="Logs a travel expense",
            inputSchema={
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "amount": {"type": "number"}
                },
                "required": ["item", "amount"]
            }
        ),
        Tool(
            name="get_budget_summary",
            description="Returns total expenses summary",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Social Tools
        Tool(
            name="update_user_preference",
            description="Updates user preference",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="get_user_preferences",
            description="Gets all user preferences",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="submit_feedback",
            description="Submits user feedback",
            inputSchema={
                "type": "object",
                "properties": {
                    "rating": {"type": "integer"},
                    "comment": {"type": "string"}
                },
                "required": ["rating", "comment"]
            }
        ),
        Tool(
            name="share_to_social_media",
            description="Shares content to social media",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["platform", "content"]
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP clients"""
    
    # Planning Tools
    if name == "suggest_destinations":
        result = suggest_destinations(
            arguments.get("budget", ""),
            arguments.get("season", ""),
            arguments.get("interests", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "create_itinerary":
        result = create_itinerary(
            arguments.get("destination", ""),
            arguments.get("days", 1)
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "suggest_activities":
        result = suggest_activities(
            arguments.get("city", ""),
            arguments.get("interests", "")
        )
        return [TextContent(type="text", text=result)]
    
    # Booking Tools
    elif name == "search_flights":
        result = search_flights(
            arguments.get("origin", ""),
            arguments.get("destination", ""),
            arguments.get("date", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "book_flight":
        result = book_flight(
            arguments.get("flight_id", ""),
            arguments.get("passenger_name", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "search_hotels":
        result = search_hotels(
            arguments.get("city", ""),
            arguments.get("check_in", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "book_hotel":
        result = book_hotel(
            arguments.get("hotel_id", ""),
            arguments.get("guest_name", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "book_ride":
        result = book_ride(
            arguments.get("pickup", ""),
            arguments.get("dropoff", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "book_activity":
        result = book_activity(
            arguments.get("activity_name", ""),
            arguments.get("date", "")
        )
        return [TextContent(type="text", text=result)]
    
    # Utility Tools
    elif name == "get_weather_forecast":
        result = get_weather_forecast(arguments.get("city", ""))
        return [TextContent(type="text", text=result)]
    
    elif name == "convert_currency":
        result = convert_currency(
            arguments.get("amount", 0.0),
            arguments.get("from_curr", ""),
            arguments.get("to_curr", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "translate_text":
        result = translate_text(
            arguments.get("text", ""),
            arguments.get("target_lang", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "check_visa_requirements":
        result = check_visa_requirements(
            arguments.get("citizenship", ""),
            arguments.get("country", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_insurance_quote":
        result = get_insurance_quote(
            arguments.get("destination", ""),
            arguments.get("days", 1)
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_emergency_contacts":
        result = get_emergency_contacts(arguments.get("city", ""))
        return [TextContent(type="text", text=result)]
    
    elif name == "get_flight_status":
        result = get_flight_status(arguments.get("flight_number", ""))
        return [TextContent(type="text", text=result)]
    
    elif name == "track_expense":
        result = track_expense(
            arguments.get("item", ""),
            arguments.get("amount", 0.0)
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_budget_summary":
        result = get_budget_summary()
        return [TextContent(type="text", text=result)]
    
    # Social Tools
    elif name == "update_user_preference":
        result = update_user_preference(
            arguments.get("key", ""),
            arguments.get("value", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_user_preferences":
        result = get_user_preferences()
        return [TextContent(type="text", text=result)]
    
    elif name == "submit_feedback":
        result = submit_feedback(
            arguments.get("rating", 0),
            arguments.get("comment", "")
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "share_to_social_media":
        result = share_to_social_media(
            arguments.get("platform", ""),
            arguments.get("content", "")
        )
        return [TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server via stdio"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    print("Starting Concierge Agent MCP Server...")
    asyncio.run(main())
