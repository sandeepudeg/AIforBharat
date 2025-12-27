"""
Test Weather, Flight, Hotel, and Itinerary agents working together.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strands_travel_planning_agent.travel_planner import TravelPlanner
from strands_travel_planning_agent.agents.weather_agent import WeatherAgent
from strands_travel_planning_agent.agents.flight_agent import FlightAgent
from strands_travel_planning_agent.agents.hotel_agent import HotelAgent
from strands_travel_planning_agent.agents.itinerary_agent import ItineraryAgent


def test_all_four_agents():
    """Test all four agents together."""
    
    planner = TravelPlanner()
    
    # Register all agents
    planner.register_agent(WeatherAgent())
    planner.register_agent(FlightAgent())
    planner.register_agent(HotelAgent())
    planner.register_agent(ItineraryAgent())
    
    print("=" * 70)
    print("Testing Weather + Flight + Hotel + Itinerary Agents")
    print("=" * 70)
    
    query = "I want to plan a trip to Paris from 2024-06-01 to 2024-06-10 with a budget of $3000"
    
    print(f"\nUser Query: {query}\n")
    
    result = planner.process_query(query)
    
    print(result)
    print("\n" + "=" * 70)
    print("Test Complete - All 4 Agents Working Together")
    print("=" * 70)


if __name__ == "__main__":
    test_all_four_agents()
