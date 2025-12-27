"""
Test Weather_Agent and Flight_Agent working together through Travel_Planner.
Run this to verify both agents communicate correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strands_travel_planning_agent.travel_planner import TravelPlanner
from strands_travel_planning_agent.agents.weather_agent import WeatherAgent
from strands_travel_planning_agent.agents.flight_agent import FlightAgent


def test_weather_and_flight_agents():
    """Test Weather and Flight agents together."""
    
    # Initialize Travel_Planner
    planner = TravelPlanner()
    
    # Register agents
    weather_agent = WeatherAgent()
    flight_agent = FlightAgent()
    
    planner.register_agent(weather_agent)
    planner.register_agent(flight_agent)
    
    print("=" * 60)
    print("Testing Weather + Flight Agents")
    print("=" * 60)
    
    # Test query
    query = "I want to plan a trip to Paris from 2024-06-01 to 2024-06-10 with a budget of $3000"
    
    print(f"\nUser Query: {query}\n")
    
    # Process the query
    result = planner.process_query(query)
    
    print(result)
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_weather_and_flight_agents()
