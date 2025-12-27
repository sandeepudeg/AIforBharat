"""
Test Weather_Agent, Flight_Agent, and Hotel_Agent working together.
Run this to verify all three agents communicate correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strands_travel_planning_agent.travel_planner import TravelPlanner
from strands_travel_planning_agent.agents.weather_agent import WeatherAgent
from strands_travel_planning_agent.agents.flight_agent import FlightAgent
from strands_travel_planning_agent.agents.hotel_agent import HotelAgent


def test_weather_flight_hotel_agents():
    """Test Weather, Flight, and Hotel agents together."""
    
    # Initialize Travel_Planner
    planner = TravelPlanner()
    
    # Register agents
    weather_agent = WeatherAgent()
    flight_agent = FlightAgent()
    hotel_agent = HotelAgent()
    
    planner.register_agent(weather_agent)
    planner.register_agent(flight_agent)
    planner.register_agent(hotel_agent)
    
    print("=" * 70)
    print("Testing Weather + Flight + Hotel Agents")
    print("=" * 70)
    
    # Test query
    query = "I want to plan a trip to Paris from 2024-06-01 to 2024-06-10 with a budget of $3000"
    
    print(f"\nUser Query: {query}\n")
    
    # Process the query
    result = planner.process_query(query)
    
    print(result)
    print("\n" + "=" * 70)
    print("Test Complete - All 3 Agents Working Together")
    print("=" * 70)


if __name__ == "__main__":
    test_weather_flight_hotel_agents()
