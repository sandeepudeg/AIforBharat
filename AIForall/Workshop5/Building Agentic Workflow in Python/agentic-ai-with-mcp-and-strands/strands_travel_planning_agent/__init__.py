"""
Travel Planning Agent - Multi-agent system for comprehensive trip planning.

This module provides a sophisticated travel planning system that coordinates
specialized agents for weather analysis, flight recommendations, hotel suggestions,
itinerary creation, budget optimization, visa requirements, and local transportation.
"""

__version__ = "1.0.0"
__author__ = "Travel Planning Team"

from .core import (
    AgentRequest,
    AgentResponse,
    BaseAgent,
    TravelPlannerInterface,
    AgentRegistry,
    MessageBroker,
    ErrorHandler,
    ValidationHelper,
    CurrencyConverter,
    MemoryService
)

from .travel_planner import create_travel_planner

from .models import (
    Trip,
    Flight,
    Hotel,
    DayPlan,
    Activity,
    Budget,
    UserPreferences,
    VisaRequirement,
    ActivityAgeRestriction,
    LocalTransportOption,
)

__all__ = [
    # Core classes
    "AgentRequest",
    "AgentResponse",
    "BaseAgent",
    "TravelPlannerInterface",
    "AgentRegistry",
    "MessageBroker",
    "ErrorHandler",
    "ValidationHelper",
    "CurrencyConverter",
    "MemoryService",
    # Travel Planner
    "create_travel_planner",
    # Models
    "Trip",
    "Flight",
    "Hotel",
    "DayPlan",
    "Activity",
    "Budget",
    "UserPreferences",
    "VisaRequirement",
    "ActivityAgeRestriction",
    "LocalTransportOption",
]
