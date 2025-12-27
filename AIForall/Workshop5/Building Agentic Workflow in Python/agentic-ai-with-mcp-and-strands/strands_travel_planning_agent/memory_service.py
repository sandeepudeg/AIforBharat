#!/usr/bin/env python3
"""
Memory Service for Travel Planning Agent

Handles user preferences, trip history, and memory persistence using Bedrock Memory.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User travel preferences."""
    user_id: str
    preferred_budget_range: Dict[str, float] = field(default_factory=lambda: {"min": 1000, "max": 5000})
    preferred_travel_style: str = "balanced"  # "budget", "luxury", "balanced", "adventure"
    preferred_climate: str = "temperate"  # "tropical", "temperate", "cold", "desert"
    preferred_activities: List[str] = field(default_factory=list)
    preferred_cuisines: List[str] = field(default_factory=list)
    preferred_airlines: List[str] = field(default_factory=list)
    preferred_hotel_chains: List[str] = field(default_factory=list)
    home_currency: str = "USD"
    home_country: str = "USA"
    languages_spoken: List[str] = field(default_factory=lambda: ["English"])
    accessibility_needs: List[str] = field(default_factory=list)
    travel_companions: str = "solo"  # "solo", "couple", "family", "group"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TripRecord:
    """Record of a completed or planned trip."""
    trip_id: str
    user_id: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    actual_cost: Optional[float] = None
    rating: Optional[float] = None  # 1-5 stars
    notes: str = ""
    highlights: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class MemoryService:
    """Service for managing user preferences and trip history."""
    
    def __init__(self):
        """Initialize memory service."""
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.trip_history: Dict[str, List[TripRecord]] = {}
        logger.info("Memory service initialized")
    
    def create_user_preferences(self, user_id: str) -> UserPreferences:
        """
        Create default preferences for a new user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Created UserPreferences object
        """
        logger.info(f"Creating preferences for user: {user_id}")
        
        preferences = UserPreferences(user_id=user_id)
        self.user_preferences[user_id] = preferences
        
        return preferences
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Retrieve user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences or None if not found
        """
        return self.user_preferences.get(user_id)
    
    def update_user_preferences(self, user_id: str, updates: Dict[str, Any]) -> UserPreferences:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            updates: Dictionary of preference updates
            
        Returns:
            Updated UserPreferences object
        """
        logger.info(f"Updating preferences for user: {user_id}")
        
        if user_id not in self.user_preferences:
            self.create_user_preferences(user_id)
        
        preferences = self.user_preferences[user_id]
        
        # Update allowed fields
        allowed_fields = {
            "preferred_budget_range", "preferred_travel_style", "preferred_climate",
            "preferred_activities", "preferred_cuisines", "preferred_airlines",
            "preferred_hotel_chains", "home_currency", "home_country",
            "languages_spoken", "accessibility_needs", "travel_companions"
        }
        
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(preferences, key, value)
        
        preferences.updated_at = datetime.now().isoformat()
        return preferences
    
    def add_activity_preference(self, user_id: str, activity: str):
        """
        Add an activity to user's preferred activities.
        
        Args:
            user_id: User identifier
            activity: Activity name
        """
        logger.info(f"Adding activity preference for user {user_id}: {activity}")
        
        if user_id not in self.user_preferences:
            self.create_user_preferences(user_id)
        
        preferences = self.user_preferences[user_id]
        if activity not in preferences.preferred_activities:
            preferences.preferred_activities.append(activity)
            preferences.updated_at = datetime.now().isoformat()
    
    def add_cuisine_preference(self, user_id: str, cuisine: str):
        """
        Add a cuisine to user's preferred cuisines.
        
        Args:
            user_id: User identifier
            cuisine: Cuisine type
        """
        logger.info(f"Adding cuisine preference for user {user_id}: {cuisine}")
        
        if user_id not in self.user_preferences:
            self.create_user_preferences(user_id)
        
        preferences = self.user_preferences[user_id]
        if cuisine not in preferences.preferred_cuisines:
            preferences.preferred_cuisines.append(cuisine)
            preferences.updated_at = datetime.now().isoformat()
    
    def record_trip(self, trip_record: TripRecord):
        """
        Record a trip in user's history.
        
        Args:
            trip_record: TripRecord object
        """
        logger.info(f"Recording trip for user {trip_record.user_id}: {trip_record.destination}")
        
        user_id = trip_record.user_id
        if user_id not in self.trip_history:
            self.trip_history[user_id] = []
        
        self.trip_history[user_id].append(trip_record)
    
    def get_trip_history(self, user_id: str) -> List[TripRecord]:
        """
        Get user's trip history.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of TripRecord objects
        """
        return self.trip_history.get(user_id, [])
    
    def get_favorite_destinations(self, user_id: str) -> List[str]:
        """
        Get user's most visited destinations.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of destination names sorted by frequency
        """
        trips = self.get_trip_history(user_id)
        
        destination_counts = {}
        for trip in trips:
            destination_counts[trip.destination] = destination_counts.get(trip.destination, 0) + 1
        
        # Sort by count (descending)
        sorted_destinations = sorted(destination_counts.items(), key=lambda x: x[1], reverse=True)
        return [dest for dest, count in sorted_destinations]
    
    def get_average_trip_cost(self, user_id: str) -> Optional[float]:
        """
        Calculate average trip cost for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Average cost or None if no completed trips
        """
        trips = self.get_trip_history(user_id)
        completed_trips = [t for t in trips if t.actual_cost is not None]
        
        if not completed_trips:
            return None
        
        total_cost = sum(t.actual_cost for t in completed_trips)
        return total_cost / len(completed_trips)
    
    def get_trip_rating_average(self, user_id: str) -> Optional[float]:
        """
        Calculate average rating for user's trips.
        
        Args:
            user_id: User identifier
            
        Returns:
            Average rating or None if no rated trips
        """
        trips = self.get_trip_history(user_id)
        rated_trips = [t for t in trips if t.rating is not None]
        
        if not rated_trips:
            return None
        
        total_rating = sum(t.rating for t in rated_trips)
        return total_rating / len(rated_trips)
    
    def get_recommendations_based_on_history(self, user_id: str) -> Dict[str, Any]:
        """
        Generate recommendations based on user's trip history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with recommendations
        """
        logger.info(f"Generating recommendations for user: {user_id}")
        
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return {}
        
        trips = self.get_trip_history(user_id)
        
        recommendations = {
            "favorite_destinations": self.get_favorite_destinations(user_id),
            "average_trip_cost": self.get_average_trip_cost(user_id),
            "average_trip_rating": self.get_trip_rating_average(user_id),
            "total_trips": len(trips),
            "preferred_travel_style": preferences.preferred_travel_style,
            "suggested_budget": preferences.preferred_budget_range,
            "suggested_activities": preferences.preferred_activities,
            "suggested_cuisines": preferences.preferred_cuisines
        }
        
        return recommendations
    
    def export_preferences_to_json(self, user_id: str) -> str:
        """
        Export user preferences to JSON format.
        
        Args:
            user_id: User identifier
            
        Returns:
            JSON string of preferences
        """
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return "{}"
        
        return json.dumps(asdict(preferences), indent=2)
    
    def import_preferences_from_json(self, user_id: str, json_str: str) -> UserPreferences:
        """
        Import user preferences from JSON format.
        
        Args:
            user_id: User identifier
            json_str: JSON string of preferences
            
        Returns:
            Imported UserPreferences object
        """
        logger.info(f"Importing preferences for user: {user_id}")
        
        data = json.loads(json_str)
        preferences = UserPreferences(**data)
        self.user_preferences[user_id] = preferences
        
        return preferences
    
    def clear_user_data(self, user_id: str):
        """
        Clear all data for a user (GDPR compliance).
        
        Args:
            user_id: User identifier
        """
        logger.info(f"Clearing all data for user: {user_id}")
        
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
        if user_id in self.trip_history:
            del self.trip_history[user_id]
    
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of user's profile and history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user summary
        """
        preferences = self.get_user_preferences(user_id)
        trips = self.get_trip_history(user_id)
        
        if not preferences:
            return {"error": "User not found"}
        
        return {
            "user_id": user_id,
            "travel_style": preferences.preferred_travel_style,
            "home_country": preferences.home_country,
            "home_currency": preferences.home_currency,
            "total_trips": len(trips),
            "favorite_destinations": self.get_favorite_destinations(user_id)[:5],
            "average_trip_cost": self.get_average_trip_cost(user_id),
            "average_trip_rating": self.get_trip_rating_average(user_id),
            "preferred_activities": preferences.preferred_activities,
            "preferred_cuisines": preferences.preferred_cuisines,
            "member_since": preferences.created_at
        }
