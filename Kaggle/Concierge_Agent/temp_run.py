# Install ADK if not already installed (Uncomment if needed)
# !pip install google-adk
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    print("Warning: GOOGLE_API_KEY not found in environment. Please set it.")
    # os.environ["GOOGLE_API_KEY"] = "YOUR_KEY_HERE"
else:
    print("✅ Google API Key loaded.")
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

print("✅ ADK components imported successfully.")
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
# Planning Agent
planning_agent = Agent(
    name="PlanningAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a Travel Planner. Use your tools to suggest destinations, create itineraries, and suggest activities.
    IMPORTANT: After using a tool, you MUST provide a text summary of the results to the user. Do not just return the tool output.""",
    tools=[FunctionTool(suggest_destinations), FunctionTool(create_itinerary), FunctionTool(suggest_activities)],
    output_key="planning_output"
)

# Booking Agent
booking_agent = Agent(
    name="BookingAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a Booking Specialist. Use your tools to search and book flights, hotels, rides, and activities.
    IMPORTANT: After using a tool, you MUST provide a text confirmation or summary of the booking details to the user.""",
    tools=[
        FunctionTool(search_flights), FunctionTool(book_flight),
        FunctionTool(search_hotels), FunctionTool(book_hotel),
        FunctionTool(book_ride), FunctionTool(book_activity)
    ],
    output_key="booking_output"
)

# Utility Agent (Mock Tools)
utility_agent = Agent(
    name="UtilityAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a Travel Assistant. Provide info on weather, currency, visa, insurance, emergency contacts, and flight status using your specific tools.
    IMPORTANT: After using a tool, you MUST provide a clear text report of the information to the user.""",
    tools=[
        FunctionTool(get_weather_forecast), FunctionTool(convert_currency),
        FunctionTool(translate_text), FunctionTool(check_visa_requirements),
        FunctionTool(get_insurance_quote), FunctionTool(get_emergency_contacts),
        FunctionTool(get_flight_status), FunctionTool(track_expense),
        FunctionTool(get_budget_summary)
    ],
    output_key="utility_output"
)

# Search Agent (Real-time Tools)
# We separate this to avoid mixing FunctionTool and google_search which causes compatibility issues.
search_agent = Agent(
    name="SearchAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a Real-Time Information Specialist. Use `google_search` to find up-to-date information on:
    - Currency exchange rates
    - Real-time weather conditions
    - Visa requirements and travel advisories
    - Local events and news
    Always summarize the search results clearly for the user.""",
    tools=[google_search],
    output_key="search_output"
)

# Social Agent
social_agent = Agent(
    name="SocialAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You handle User Profile and Socials. Update preferences, collect feedback, and share updates.
    IMPORTANT: After using a tool, you MUST provide a text confirmation of the action to the user.""",
    tools=[
        FunctionTool(update_user_preference), FunctionTool(get_user_preferences),
        FunctionTool(submit_feedback), FunctionTool(share_to_social_media)
    ],
    output_key="social_output"
)

print("✅ Sub-agents created. SearchAgent separated for compatibility.")
root_agent = Agent(
    name="ConciergeCoordinator",
    model="gemini-2.5-flash-lite",
    instruction="""You are the Head Concierge. Your goal is to assist the user with their travel needs by coordinating with specialized agents.
    - For planning (destinations, itineraries), call `PlanningAgent`.
    - For bookings (flights, hotels, rides), call `BookingAgent`.
    - For specific utilities (simulated weather, simulated currency, expenses), call `UtilityAgent`.
    - For REAL-TIME information (actual currency rates, actual weather, news), call `SearchAgent`.
    - For social/profile (preferences, feedback, sharing), call `SocialAgent`.
    
    Always answer the user politely. If a sub-agent returns information, summarize it for the user and ask if they need anything else.""",
    tools=[
        AgentTool(planning_agent),
        AgentTool(booking_agent),
        AgentTool(utility_agent),
        AgentTool(search_agent),
        AgentTool(social_agent)
    ]
)

print("✅ Root Coordinator created.")
# --- Missing Feature Implementations ---
# 1. Mock MCP Tool (Multi‑Component Process)
class MCPTool(FunctionTool):
    def __init__(self, name: str):
        super().__init__(self.run)
        self.name = name
    def run(self, *args, **kwargs):
        # Simulate a multi‑step process
        logger.log_step(f'MCP {self.name}', f'args={args}, kwargs={kwargs}')
        return f'MCP {self.name} completed'

# 2. OpenAPI Tool (mock)
def call_openapi(endpoint: str, payload: dict):
    logger.log_step('OpenAPI Call', f'endpoint={endpoint}')
    # In a real scenario you would use requests.post...
    return {'status': 'success', 'data': payload}

# 3. Simple Session Service (in‑memory)
class SimpleSessionService:
    def __init__(self):
        self.sessions = {}
    def get(self, session_id):
        return self.sessions.get(session_id, {})
    def set(self, session_id, state):
        self.sessions[session_id] = state
    def clear(self, session_id):
        self.sessions.pop(session_id, None)

session_service = SimpleSessionService()

# 4. Context Compaction (simple token limit)
def compact_context(messages, max_tokens=500):
    # Very naive compaction: keep last N messages
    # Assume each message ~1 token for demo purposes
    if len(messages) <= max_tokens:
        return messages
    return messages[-max_tokens:]

# 5. Observability – Metrics counters
class Metrics:
    def __init__(self):
        self.counters = {}
    def inc(self, name, amount=1):
        self.counters[name] = self.counters.get(name, 0) + amount
    def report(self):
        return self.counters

metrics = Metrics()

# 6. Agent Evaluation (simple scoring)
def evaluate_response(response: str) -> float:
    # Placeholder: reward length and presence of keywords
    score = len(response) * 0.01
    for kw in ['success', 'confirmed', 'done']:
        if kw in response.lower():
            score += 0.5
    return min(score, 1.0)

# 7. A2A Protocol mock (agent‑to‑agent message)
def a2a_message(sender, receiver, payload):
    logger.log_step('A2A', f'{sender} -> {receiver}')
    # Direct function call for demo
    return receiver(payload)

# 8. Deployment helper (export to Dockerfile)
def export_to_docker(image_name='concierge-agent'):
    dockerfile = f'''
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir google-adk
CMD ["python", "-m", "nbconvert", "--to", "script", "Concierge_Agent.ipynb"]
'''
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    print(f'Dockerfile created for image {image_name}')

# Register new tools with agents where appropriate (example)
# Here we simply expose them as FunctionTool instances for potential use
mcp_tool = MCPTool('example_mcp')
openapi_tool = FunctionTool(lambda endpoint, payload: call_openapi(endpoint, payload))
# You can now add these to any agent's tool list if needed
# Example: planning_agent.tools.append(mcp_tool)  # (would require re‑definition of the agent)

print('✅ Missing feature implementations added.')
runner = InMemoryRunner(agent=root_agent)

async def run_demo():
    print("--- Starting Concierge Demo (Type 'exit' to quit) ---")
    # Initialize simple session handling
    session_id = 'default'
    history = session_service.get(session_id)
    if not isinstance(history, list):
        history = []
    
    # Initial complex query
    initial_query = """
    I want to plan a trip to Japan in Autumn. Budget is medium.
    Once you suggest a destination, please check the weather there.
    Also, check if I need a visa (US Citizen).
    Then, find me a hotel and book it.
    Finally, share my plan to Facebook.
    """
    
    # Start with the initial query
    current_query = initial_query
    
    metrics.inc('conversations_started')
    while True:
        print(f"\nUser > {current_query}\n")
        
        # Run the agent
        # We iterate through events to handle output correctly and avoid TypeError
        try:
            metrics.inc('agent_calls')
            compacted = compact_context(history + [current_query])
            await runner.run_debug(compacted[-1])
        except Exception as e:
            print(f"Error during execution: {e}")
            break
            
        # Get next user input
        user_input = input("\nEnter your reply (or 'exit'): ")
        if user_input.lower() in ['exit', 'quit']:
            break
        current_query = user_input

    print("\n--- Demo Completed ---")

# Run the demo (if in an async environment like Jupyter)
# Note: In a real Jupyter environment, `input()` works interactively.
# For automated testing, we might need to mock input or just run the initial query.
asyncio.run(run_demo())
# --- Missing Feature Implementations ---
# 1. Mock MCP Tool (Multi-Component Process)
class MCPTool(FunctionTool):
    def __init__(self, name: str):
        super().__init__(self.run)
        self.name = name
    def run(self, *args, **kwargs):
        # Simulate a multi-step process
        logger.log_step(f'MCP {self.name}', f'args={args}, kwargs={kwargs}')
        return f'MCP {self.name} completed'

# 2. OpenAPI Tool (mock)
def call_openapi(endpoint: str, payload: dict):
    logger.log_step('OpenAPI Call', f'endpoint={endpoint}')
    # In a real scenario you would use requests.post...
    return {'status': 'success', 'data': payload}

# 3. Simple Session Service (in-memory)
class SimpleSessionService:
    def __init__(self):
        self.sessions = {}
    def get(self, session_id):
        return self.sessions.get(session_id, {})
    def set(self, session_id, state):
        self.sessions[session_id] = state
    def clear(self, session_id):
        self.sessions.pop(session_id, None)

session_service = SimpleSessionService()

# 4. Context Compaction (simple token limit)
def compact_context(messages, max_tokens=500):
    # Very naive compaction: keep last N messages
    if len(messages) <= max_tokens:
        return messages
    return messages[-max_tokens:]

# 5. Metrics (simple counters)
class Metrics:
    def __init__(self):
        self.counters = {}
    def inc(self, name, amount=1):
        self.counters[name] = self.counters.get(name, 0) + amount
    def report(self):
        return self.counters

metrics = Metrics()

# 6. Agent Evaluation (simple scoring)
def evaluate_response(response: str) -> float:
    # Placeholder: reward length and presence of keywords
    score = len(response) * 0.01
    for kw in ['success', 'confirmed', 'done']:
        if kw in response.lower():
            score += 0.5
    return min(score, 1.0)

# 7. Register new tools with agents
mcp_tool = MCPTool('example_mcp')
openapi_tool = FunctionTool(lambda endpoint, payload: call_openapi(endpoint, payload))

print('✅ Missing feature implementations added.')
# --- Long‑running operation helpers (pause / resume) ---
import asyncio

# Simple flag‑based pause/resume for agents
class AgentPauseController:
    def __init__(self):
        self.paused = False
    async def pause(self):
        self.paused = True
        print('🛑 Agent execution paused')
    async def resume(self):
        self.paused = False
        print('▶️ Agent execution resumed')
    async def wait_if_paused(self):
        while self.paused:
            await asyncio.sleep(0.5)

# Create a global controller that can be used by any agent
agent_pause_controller = AgentPauseController()

# Expose as FunctionTool so agents can request pause/resume
pause_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.pause()))
resume_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.resume()))
# You can add these tools to any agent's tool list if needed
# Example: planning_agent.tools.append(pause_tool)
#          planning_agent.tools.append(resume_tool)
print('✅ Pause/Resume utilities added')
# --- Long‑running operation helpers (pause / resume) ---
import asyncio

# Simple flag‑based pause/resume for agents
class AgentPauseController:
    def __init__(self):
        self.paused = False
    async def pause(self):
        self.paused = True
        print('🛑 Agent execution paused')
    async def resume(self):
        self.paused = False
        print('▶️ Agent execution resumed')
    async def wait_if_paused(self):
        while self.paused:
            await asyncio.sleep(0.5)

# Create a global controller that can be used by any agent
agent_pause_controller = AgentPauseController()

# Expose as FunctionTool so agents can request pause/resume
pause_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.pause()))
resume_tool = FunctionTool(lambda: asyncio.run(agent_pause_controller.resume()))
# You can add these tools to any agent's tool list if needed
# Example: planning_agent.tools.append(pause_tool)
#          planning_agent.tools.append(resume_tool)
print('✅ Pause/Resume utilities added')
