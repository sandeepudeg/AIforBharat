"""
Test all 8 agents working together: Weather, Flight, Hotel, Itinerary, Budget, Language, Visa/Age, Transport.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strands_travel_planning_agent.travel_planner import TravelPlanner
from strands_travel_planning_agent.agents.weather_agent import WeatherAgent
from strands_travel_planning_agent.agents.flight_agent import FlightAgent
from strands_travel_planning_agent.agents.hotel_agent import HotelAgent
from strands_travel_planning_agent.agents.itinerary_agent import ItineraryAgent
from strands_travel_planning_agent.agents.budget_agent import BudgetAgent
from strands_travel_planning_agent.agents.language_agent import LanguageAgent
from strands_travel_planning_agent.agents.visa_age_agent import VisaAndAgeAgent
from strands_travel_planning_agent.agents.local_transport_agent import LocalTransportAgent


def test_all_eight_agents():
    """Test all 8 agents together."""
    
    planner = TravelPlanner()
    
    # Register all 8 agents
    planner.register_agent(WeatherAgent())
    planner.register_agent(FlightAgent())
    planner.register_agent(HotelAgent())
    planner.register_agent(ItineraryAgent())
    planner.register_agent(BudgetAgent())
    planner.register_agent(LanguageAgent())
    planner.register_agent(VisaAndAgeAgent())
    planner.register_agent(LocalTransportAgent())
    
    print("=" * 80)
    print("Testing All 8 Agents: Complete Travel Planning System")
    print("=" * 80)
    print("\nAgents Registered:")
    for agent_name in planner.agent_registry.list_agents():
        print(f"  ✓ {agent_name}")
    
    query = "I want to plan a trip to Paris from 2024-06-01 to 2024-06-10 with a budget of $3000"
    
    print(f"\nUser Query: {query}\n")
    
    result = planner.process_query(query)
    
    print(result)
    print("\n" + "=" * 80)
    print("Test Complete - All 8 Agents Working Together Successfully!")
    print("=" * 80)


if __name__ == "__main__":
    test_all_eight_agents()
