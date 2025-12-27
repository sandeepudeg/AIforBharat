#!/usr/bin/env python3
"""
Local Transport Agent using Strands Framework

This agent handles local transportation options, airport transfers, and travel logistics.
"""

import logging
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class LocalTransportAgent(Agent):
    """Local transport specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Local Transport Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are a local transportation expert for travel. Your responsibilities:
1. Find local transportation options in destinations
2. Arrange airport transfers
3. Estimate travel costs and times
4. Rate convenience of transport options
5. Provide transportation recommendations

When users ask about local transport, use the available tools to find options,
estimate costs, and provide recommendations."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.search_transport_options,
                self.get_airport_transfer,
                self.estimate_travel_cost,
                self.rate_convenience
            ]
        )
    
    def search_transport_options(self, destination: str, 
                                route_type: str = "general") -> list:
        """
        Search for local transportation options.
        
        Args:
            destination: City name
            route_type: Type of route ("airport", "city", "general")
            
        Returns:
            List of transportation options
        """
        logger.info(f"Searching transport options in {destination}")
        
        options = self._get_mock_transport_options(destination, route_type)
        return options
    
    def get_airport_transfer(self, destination: str, 
                            passengers: int = 1) -> list:
        """
        Get airport transfer options.
        
        Args:
            destination: City name
            passengers: Number of passengers
            
        Returns:
            List of airport transfer options
        """
        logger.info(f"Getting airport transfer options for {destination}")
        
        transfers = [
            {
                "type": "Airport Shuttle",
                "cost_per_person": 15,
                "total_cost": 15 * passengers,
                "duration_minutes": 45,
                "convenience": 3,
                "description": "Shared shuttle service"
            },
            {
                "type": "Taxi",
                "cost_per_person": 40,
                "total_cost": 40 * passengers,
                "duration_minutes": 30,
                "convenience": 4,
                "description": "Direct taxi service"
            },
            {
                "type": "Ride-sharing (Uber/Lyft)",
                "cost_per_person": 25,
                "total_cost": 25 * passengers,
                "duration_minutes": 35,
                "convenience": 4,
                "description": "On-demand ride service"
            },
            {
                "type": "Public Transport",
                "cost_per_person": 3,
                "total_cost": 3 * passengers,
                "duration_minutes": 60,
                "convenience": 2,
                "description": "Metro/bus combination"
            },
            {
                "type": "Private Car Service",
                "cost_per_person": 60,
                "total_cost": 60 * passengers,
                "duration_minutes": 25,
                "convenience": 5,
                "description": "Premium private transfer"
            }
        ]
        
        return transfers
    
    def estimate_travel_cost(self, origin: str, destination: str,
                            transport_mode: str, distance_km: float = None) -> dict:
        """
        Estimate travel cost between locations.
        
        Args:
            origin: Starting location
            destination: Ending location
            transport_mode: Type of transport
            distance_km: Distance in kilometers (optional)
            
        Returns:
            Cost estimation
        """
        logger.info(f"Estimating cost from {origin} to {destination}")
        
        # Mock distance if not provided
        if distance_km is None:
            distance_km = 15
        
        # Cost calculation based on transport mode
        costs = {
            "metro": distance_km * 0.2,
            "bus": distance_km * 0.15,
            "taxi": distance_km * 2.5,
            "ride_sharing": distance_km * 1.8,
            "walking": 0,
            "bicycle": 0
        }
        
        cost = costs.get(transport_mode.lower(), distance_km * 2.0)
        
        return {
            "origin": origin,
            "destination": destination,
            "transport_mode": transport_mode,
            "distance_km": distance_km,
            "estimated_cost": round(cost, 2),
            "currency": "USD",
            "estimated_time_minutes": int(distance_km / 3) if transport_mode != "walking" else int(distance_km * 1.2)
        }
    
    def rate_convenience(self, transport_mode: str) -> dict:
        """
        Rate convenience of a transport mode.
        
        Args:
            transport_mode: Type of transport
            
        Returns:
            Convenience rating and details
        """
        logger.info(f"Rating convenience of {transport_mode}")
        
        ratings = {
            "metro": {
                "convenience": 4,
                "speed": 4,
                "cost": 5,
                "comfort": 3,
                "reliability": 4,
                "pros": ["Fast", "Cheap", "Reliable"],
                "cons": ["Crowded", "Limited routes", "Confusing maps"]
            },
            "bus": {
                "convenience": 3,
                "speed": 2,
                "cost": 5,
                "comfort": 2,
                "reliability": 3,
                "pros": ["Cheap", "Extensive routes", "Scenic"],
                "cons": ["Slow", "Crowded", "Unreliable timing"]
            },
            "taxi": {
                "convenience": 4,
                "speed": 4,
                "cost": 2,
                "comfort": 4,
                "reliability": 4,
                "pros": ["Direct", "Comfortable", "No navigation needed"],
                "cons": ["Expensive", "Traffic dependent", "Language barrier"]
            },
            "ride_sharing": {
                "convenience": 5,
                "speed": 4,
                "cost": 3,
                "comfort": 4,
                "reliability": 4,
                "pros": ["Easy booking", "Transparent pricing", "Comfortable"],
                "cons": ["Surge pricing", "Requires app", "Variable availability"]
            },
            "walking": {
                "convenience": 5,
                "speed": 1,
                "cost": 5,
                "comfort": 3,
                "reliability": 5,
                "pros": ["Free", "Explore city", "Healthy"],
                "cons": ["Slow", "Tiring", "Weather dependent"]
            }
        }
        
        rating = ratings.get(transport_mode.lower(), {
            "convenience": 3,
            "speed": 3,
            "cost": 3,
            "comfort": 3,
            "reliability": 3,
            "pros": ["Available"],
            "cons": ["Variable quality"]
        })
        
        overall_score = (rating["convenience"] + rating["speed"] + 
                        rating["cost"] + rating["comfort"] + rating["reliability"]) / 5
        
        return {
            "transport_mode": transport_mode,
            "overall_score": round(overall_score, 1),
            "ratings": {
                "convenience": rating["convenience"],
                "speed": rating["speed"],
                "cost": rating["cost"],
                "comfort": rating["comfort"],
                "reliability": rating["reliability"]
            },
            "pros": rating["pros"],
            "cons": rating["cons"]
        }
    
    def _get_mock_transport_options(self, destination: str, 
                                   route_type: str) -> list:
        """Generate mock transport options."""
        options = [
            {
                "type": "Metro/Subway",
                "coverage": "Extensive",
                "frequency": "Every 3-5 minutes",
                "cost": "$2-3 per trip",
                "convenience": 4,
                "description": "Fast underground rail system"
            },
            {
                "type": "Bus",
                "coverage": "Comprehensive",
                "frequency": "Every 10-15 minutes",
                "cost": "$1-2 per trip",
                "convenience": 3,
                "description": "Extensive bus network"
            },
            {
                "type": "Taxi",
                "coverage": "City-wide",
                "frequency": "On-demand",
                "cost": "$3-5 per km",
                "convenience": 4,
                "description": "Traditional taxi service"
            },
            {
                "type": "Ride-sharing",
                "coverage": "City-wide",
                "frequency": "On-demand",
                "cost": "$2-4 per km",
                "convenience": 5,
                "description": "Uber/Lyft style service"
            },
            {
                "type": "Bicycle Rental",
                "coverage": "City-wide",
                "frequency": "24/7",
                "cost": "$5-10 per day",
                "convenience": 3,
                "description": "Bike sharing system"
            }
        ]
        
        return options
