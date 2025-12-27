#!/usr/bin/env python3
"""
Travel Planner - Orchestrator for Travel Planning Agents

This module coordinates all specialized Strands agents to create comprehensive travel plans.
Follows the exact pattern from english_assistant.py in strands_multi_agent_example.
"""

import logging
from strands import Agent, tool
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

from .agents import (
    WeatherAgent,
    FlightAgent,
    HotelAgent,
    ItineraryAgent,
    BudgetAgent,
    LanguageAgent,
    VisaAgeAgent,
    LocalTransportAgent
)
from .alerts_service import AlertsService, AlertType, AlertSeverity

logger = logging.getLogger(__name__)

# System prompts for each specialized agent
WEATHER_SYSTEM_PROMPT = """You are a weather expert assistant for travel planning. Your responsibilities:
1. Provide accurate weather forecasts for destinations
2. Analyze climate patterns and seasonal weather
3. Give packing recommendations based on weather conditions
4. Identify the best days for outdoor activities
5. Provide weather-related travel advice"""

FLIGHT_SYSTEM_PROMPT = """You are a flight booking expert for travel planning. Your responsibilities:
1. Search for available flights between destinations
2. Filter flights by budget, duration, and preferences
3. Compare flight options and provide recommendations
4. Handle round-trip flight combinations
5. Provide flight booking advice and tips"""

HOTEL_SYSTEM_PROMPT = """You are a hotel booking expert for travel planning. Your responsibilities:
1. Search for available hotels in destinations
2. Filter hotels by budget, amenities, and ratings
3. Provide hotel recommendations based on preferences
4. Compare hotel options and value
5. Provide accommodation booking advice"""

ITINERARY_SYSTEM_PROMPT = """You are an itinerary planning expert for travel. Your responsibilities:
1. Create day-by-day itineraries for trips
2. Recommend attractions and activities
3. Suggest meal options and restaurants
4. Calculate travel times between locations
5. Optimize daily schedules for maximum enjoyment"""

BUDGET_SYSTEM_PROMPT = """You are a travel budget expert. Your responsibilities:
1. Track and manage travel expenses
2. Provide budget breakdowns by category
3. Convert currencies for international travel
4. Suggest cost-saving opportunities
5. Provide financial planning advice"""

LANGUAGE_SYSTEM_PROMPT = """You are a travel language expert. Your responsibilities:
1. Translate text between languages
2. Provide common travel phrases
3. Create language guides for destinations
4. Offer pronunciation guidance
5. Provide cultural communication tips"""

VISA_AGE_SYSTEM_PROMPT = """You are a travel documentation and eligibility expert. Your responsibilities:
1. Check visa requirements for destinations
2. Verify age restrictions for activities
3. Filter activities based on age
4. Provide visa application guidance
5. Offer travel eligibility advice"""

TRANSPORT_SYSTEM_PROMPT = """You are a local transportation expert for travel. Your responsibilities:
1. Find local transportation options in destinations
2. Arrange airport transfers
3. Estimate travel costs and times
4. Rate convenience of transport options
5. Provide transportation recommendations"""

TRAVEL_PLANNER_SYSTEM_PROMPT = """You are TravelAssist, an intelligent travel planning orchestrator powered by Strands.

Your role is to:
1. Understand user travel requirements and preferences
2. Coordinate with specialized agents to gather information:
   - Weather Agent: Climate, forecasts, best travel times
   - Flight Agent: Flight search and recommendations
   - Hotel Agent: Accommodation options
   - Itinerary Agent: Day-by-day activity planning
   - Budget Agent: Cost analysis and optimization
   - Language Agent: Translation and local communication
   - Visa and Age Agent: Travel eligibility and requirements
   - Local Transport Agent: Local transportation options

3. Synthesize information from multiple agents into cohesive travel plans
4. Provide personalized recommendations based on user preferences
5. Create comprehensive trip packages with all necessary details

When planning a trip, gather information from relevant agents and present
a complete, well-organized travel plan."""


# Initialize specialized agents as module-level instances
_weather_agent = None
_flight_agent = None
_hotel_agent = None
_itinerary_agent = None
_budget_agent = None
_language_agent = None
_visa_age_agent = None
_transport_agent = None
_alerts_service = None


def _init_agents(session_manager=None):
    """Initialize all specialized agents."""
    global _weather_agent, _flight_agent, _hotel_agent, _itinerary_agent
    global _budget_agent, _language_agent, _visa_age_agent, _transport_agent
    global _alerts_service
    
    _weather_agent = WeatherAgent(session_manager=session_manager)
    _flight_agent = FlightAgent(session_manager=session_manager)
    _hotel_agent = HotelAgent(session_manager=session_manager)
    _itinerary_agent = ItineraryAgent(session_manager=session_manager)
    _budget_agent = BudgetAgent(session_manager=session_manager)
    _language_agent = LanguageAgent(session_manager=session_manager)
    _visa_age_agent = VisaAgeAgent(session_manager=session_manager)
    _transport_agent = LocalTransportAgent(session_manager=session_manager)
    _alerts_service = AlertsService()
    
    logger.info("All specialized agents initialized")


# Define tools using @tool decorator (Strands pattern from english_assistant.py)

@tool
def weather_assistant(query: str) -> str:
    """
    Process and respond to weather-related travel queries.
    
    Args:
        query: The user's weather or climate question
        
    Returns:
        A helpful response addressing weather-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel weather question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Weather Assistant")
        
        weather_agent = Agent(
            system_prompt=WEATHER_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = weather_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your weather question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your weather query: {str(e)}"


@tool
def flight_assistant(query: str) -> str:
    """
    Process and respond to flight-related travel queries.
    
    Args:
        query: The user's flight or booking question
        
    Returns:
        A helpful response addressing flight-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel flight question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Flight Assistant")
        
        flight_agent = Agent(
            system_prompt=FLIGHT_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = flight_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your flight question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your flight query: {str(e)}"


@tool
def hotel_assistant(query: str) -> str:
    """
    Process and respond to hotel-related travel queries.
    
    Args:
        query: The user's hotel or accommodation question
        
    Returns:
        A helpful response addressing hotel-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel hotel question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Hotel Assistant")
        
        hotel_agent = Agent(
            system_prompt=HOTEL_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = hotel_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your hotel question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your hotel query: {str(e)}"


@tool
def itinerary_assistant(query: str) -> str:
    """
    Process and respond to itinerary-related travel queries.
    
    Args:
        query: The user's itinerary or activity question
        
    Returns:
        A helpful response addressing itinerary-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel itinerary question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Itinerary Assistant")
        
        itinerary_agent = Agent(
            system_prompt=ITINERARY_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = itinerary_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your itinerary question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your itinerary query: {str(e)}"


@tool
def budget_assistant(query: str) -> str:
    """
    Process and respond to budget-related travel queries.
    
    Args:
        query: The user's budget or cost question
        
    Returns:
        A helpful response addressing budget-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel budget question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Budget Assistant")
        
        budget_agent = Agent(
            system_prompt=BUDGET_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = budget_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your budget question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your budget query: {str(e)}"


@tool
def language_assistant(query: str) -> str:
    """
    Process and respond to language-related travel queries.
    
    Args:
        query: The user's language or translation question
        
    Returns:
        A helpful response addressing language-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel language question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Language Assistant")
        
        language_agent = Agent(
            system_prompt=LANGUAGE_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = language_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your language question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your language query: {str(e)}"


@tool
def visa_age_assistant(query: str) -> str:
    """
    Process and respond to visa and age-related travel queries.
    
    Args:
        query: The user's visa or age restriction question
        
    Returns:
        A helpful response addressing visa and age-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel visa/age question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Visa and Age Assistant")
        
        visa_agent = Agent(
            system_prompt=VISA_AGE_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = visa_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your visa/age question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your visa/age query: {str(e)}"


@tool
def transport_assistant(query: str) -> str:
    """
    Process and respond to transport-related travel queries.
    
    Args:
        query: The user's transport or logistics question
        
    Returns:
        A helpful response addressing transport-related travel concepts
    """
    formatted_query = f"Analyze and respond to this travel transport question, providing clear explanations with examples: {query}"
    
    try:
        logger.info("Routed to Transport Assistant")
        
        transport_agent = Agent(
            system_prompt=TRANSPORT_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = transport_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your transport question. Could you please rephrase?"
    except Exception as e:
        return f"Error processing your transport query: {str(e)}"


@tool
def alerts_assistant(query: str) -> str:
    """
    Process and respond to alerts and monitoring queries.
    
    Args:
        query: The user's query about alerts, price monitoring, or flight status
        
    Returns:
        A helpful response about alerts and monitoring
    """
    try:
        logger.info("Routed to Alerts Assistant")
        
        if _alerts_service is None:
            return "Alerts service not initialized. Please try again."
        
        # Get alerts summary
        summary = _alerts_service.get_summary()
        unread = _alerts_service.get_unread_alerts()
        
        response = f"""Current Alerts Status:
- Total Alerts: {summary['total_alerts']}
- Unread Alerts: {len(unread)}
- Price Monitors: {summary['price_monitors']}
- Flight Monitors: {summary['flight_monitors']}
- Weather Monitors: {summary['weather_monitors']}

Alert Types:
{chr(10).join([f"  - {k}: {v}" for k, v in summary['alert_types'].items()])}

Severity Levels:
{chr(10).join([f"  - {k}: {v}" for k, v in summary['severities'].items()])}

You can ask me to:
1. Monitor prices for flights or hotels
2. Track flight status for delays
3. Monitor weather changes at your destination
4. Set booking reminders
5. View recent alerts"""
        
        return response
    except Exception as e:
        return f"Error processing your alerts query: {str(e)}"


def create_travel_planner(session_manager: S3SessionManager = None) -> Agent:
    """
    Create and return a Travel Planner agent.
    
    Args:
        session_manager: Optional S3SessionManager for persistence
        
    Returns:
        Configured Travel Planner Agent
    """
    model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        temperature=0.3
    )
    
    # Create agent with tools using @tool decorator pattern (from english_assistant.py)
    travel_planner = Agent(
        model=model,
        system_prompt=TRAVEL_PLANNER_SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=[
            weather_assistant,
            flight_assistant,
            hotel_assistant,
            itinerary_assistant,
            budget_assistant,
            language_assistant,
            visa_age_assistant,
            transport_assistant,
            alerts_assistant
        ]
    )
    
    logger.info("Travel Planner created with all specialized assistant tools")
    return travel_planner
