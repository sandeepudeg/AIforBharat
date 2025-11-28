"""
Concierge Agent - ADK Web App Configuration

This file configures the Concierge Agent to run with the ADK web interface.
Run with: adk web --log_level DEBUG
"""

import os
import json
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search
from google.adk.apps.app import App

# Load environment variables
load_dotenv()

# ============================================================================
# TOOL DEFINITIONS
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
# AGENT DEFINITIONS
# ============================================================================

# Planning Agent
planning_agent = Agent(
    name="PlanningAgent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Travel Planner. Use your tools to suggest destinations, create itineraries, and suggest activities.
    IMPORTANT: After using a tool, you MUST provide a text summary of the results to the user. Do not just return the tool output.""",
    tools=[
        FunctionTool(suggest_destinations),
        FunctionTool(create_itinerary),
        FunctionTool(suggest_activities)
    ],
    output_key="planning_output"
)

# Booking Agent
booking_agent = Agent(
    name="BookingAgent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Booking Specialist. Use your tools to search and book flights, hotels, rides, and activities.
    IMPORTANT: After using a tool, you MUST provide a text confirmation or summary of the booking details to the user.""",
    tools=[
        FunctionTool(search_flights),
        FunctionTool(book_flight),
        FunctionTool(search_hotels),
        FunctionTool(book_hotel),
        FunctionTool(book_ride),
        FunctionTool(book_activity)
    ],
    output_key="booking_output"
)

# Utility Agent
utility_agent = Agent(
    name="UtilityAgent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Travel Assistant. Provide info on weather, currency, visa, insurance, emergency contacts, and flight status using your specific tools.
    IMPORTANT: After using a tool, you MUST provide a clear text report of the information to the user.""",
    tools=[
        FunctionTool(get_weather_forecast),
        FunctionTool(convert_currency),
        FunctionTool(translate_text),
        FunctionTool(check_visa_requirements),
        FunctionTool(get_insurance_quote),
        FunctionTool(get_emergency_contacts),
        FunctionTool(get_flight_status),
        FunctionTool(track_expense),
        FunctionTool(get_budget_summary)
    ],
    output_key="utility_output"
)

# Search Agent
search_agent = Agent(
    name="SearchAgent",
    model="gemini-2.0-flash-exp",
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
    model="gemini-2.0-flash-exp",
    instruction="""You handle User Profile and Socials. Update preferences, collect feedback, and share updates.
    IMPORTANT: After using a tool, you MUST provide a text confirmation of the action to the user.""",
    tools=[
        FunctionTool(update_user_preference),
        FunctionTool(get_user_preferences),
        FunctionTool(submit_feedback),
        FunctionTool(share_to_social_media)
    ],
    output_key="social_output"
)

# ============================================================================
# ROOT COORDINATOR AGENT
# ============================================================================

from google.adk.tools import AgentTool

root_agent = Agent(
    name="ConciergeCoordinator",
    model="gemini-2.0-flash-exp",
    instruction="""You are the Head Concierge. Your goal is to assist the user with their travel needs by coordinating with specialized agents.
    - For planning (destinations, itineraries), call `PlanningAgent`.
    - For bookings (flights, hotels, rides), call `BookingAgent`.
    - For utility info (weather, currency, visa), call `UtilityAgent`.
    - For real-time searches (events, news), call `SearchAgent`.
    - For user preferences and social media, call `SocialAgent`.
    
    Always answer the user politely. If a sub-agent returns information, summarize it for the user and ask if they need anything else.""",
    tools=[
        AgentTool(planning_agent),
        AgentTool(booking_agent),
        AgentTool(utility_agent),
        AgentTool(search_agent),
        AgentTool(social_agent)
    ]
)

# ============================================================================
# ADK CLI CONFIGURATION
# ============================================================================

from google.adk.apps.app import App

# Create the App object which ADK CLI likely looks for
app = App(
    name="concierge_agent",
    root_agent=root_agent
)

# Export both agent and app
agent = root_agent
__all__ = ['agent', 'app', 'root_agent']
