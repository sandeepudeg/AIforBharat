#!/usr/bin/env python3
"""
Hotel Agent using Strands Framework

This agent handles hotel search, filtering, and recommendations for travel planning.
"""

import logging
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class HotelAgent(Agent):
    """Hotel specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Hotel Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are a hotel booking expert for travel planning. Your responsibilities:
1. Search for available hotels in destinations
2. Filter hotels by budget, amenities, and ratings
3. Provide hotel recommendations based on preferences
4. Compare hotel options and value
5. Provide accommodation booking advice

When users ask about hotels, use the available tools to search for hotels,
analyze options, and provide the best recommendations."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.search_hotels,
                self.filter_by_budget,
                self.filter_by_amenities,
                self.get_recommendations
            ]
        )
    
    def search_hotels(self, destination: str, check_in: str, check_out: str) -> list:
        """
        Search for available hotels.
        
        Args:
            destination: City name
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            
        Returns:
            List of available hotels
        """
        logger.info(f"Searching hotels in {destination} ({check_in} to {check_out})")
        
        hotels = self._get_mock_hotels(destination)
        return hotels
    
    def filter_by_budget(self, hotels: list, max_price_per_night: float) -> list:
        """
        Filter hotels by maximum nightly rate.
        
        Args:
            hotels: List of hotels
            max_price_per_night: Maximum price per night in USD
            
        Returns:
            Filtered list of hotels within budget
        """
        logger.info(f"Filtering hotels with max price ${max_price_per_night}/night")
        
        filtered = [h for h in hotels if h.get("price_per_night", 0) <= max_price_per_night]
        return filtered
    
    def filter_by_amenities(self, hotels: list, required_amenities: list) -> list:
        """
        Filter hotels by required amenities.
        
        Args:
            hotels: List of hotels
            required_amenities: List of required amenities
            
        Returns:
            Filtered list of hotels with required amenities
        """
        logger.info(f"Filtering hotels with amenities: {required_amenities}")
        
        filtered = []
        for hotel in hotels:
            hotel_amenities = hotel.get("amenities", [])
            if all(amenity in hotel_amenities for amenity in required_amenities):
                filtered.append(hotel)
        
        return filtered
    
    def get_recommendations(self, destination: str, budget: float, 
                           preferences: list = None) -> list:
        """
        Get hotel recommendations based on preferences.
        
        Args:
            destination: City name
            budget: Maximum price per night
            preferences: List of preferred amenities
            
        Returns:
            List of recommended hotels
        """
        logger.info(f"Getting hotel recommendations for {destination}")
        
        hotels = self.search_hotels(destination, "", "")
        
        # Filter by budget
        hotels = self.filter_by_budget(hotels, budget)
        
        # Filter by amenities if provided
        if preferences:
            hotels = self.filter_by_amenities(hotels, preferences)
        
        # Sort by rating
        hotels.sort(key=lambda h: h.get("rating", 0), reverse=True)
        
        return hotels[:5]  # Return top 5 recommendations
    
    def _get_mock_hotels(self, destination: str) -> list:
        """Generate mock hotel data."""
        hotel_names = [
            "Grand Plaza Hotel",
            "Riverside Inn",
            "Mountain View Resort",
            "City Center Suites",
            "Beachfront Paradise",
            "Historic Manor House",
            "Modern Comfort Hotel",
            "Luxury Towers"
        ]
        
        amenities_pool = [
            "WiFi",
            "Pool",
            "Gym",
            "Restaurant",
            "Bar",
            "Spa",
            "Parking",
            "Room Service",
            "Concierge",
            "Business Center"
        ]
        
        hotels = []
        for i, name in enumerate(hotel_names):
            hotel = {
                "hotel_id": f"H{i+1000}",
                "name": name,
                "destination": destination,
                "address": f"{100 + i} Main Street",
                "price_per_night": 80 + (i * 40),
                "rating": 3.5 + (i * 0.4),
                "reviews_count": 100 + (i * 50),
                "rooms_available": 5 + (i * 3),
                "amenities": amenities_pool[i:i+4],
                "room_types": ["Single", "Double", "Suite"],
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "cancellation_policy": "Free cancellation up to 48 hours"
            }
            hotels.append(hotel)
        
        return hotels
