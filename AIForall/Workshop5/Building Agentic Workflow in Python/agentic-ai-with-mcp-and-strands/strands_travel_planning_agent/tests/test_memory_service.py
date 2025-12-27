#!/usr/bin/env python3
"""
Property-Based Tests for Memory Service

Feature: travel-planning-agent
Property 7: User Preference Persistence

Validates: Requirements 8.3, 8.4
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_service import MemoryService, UserPreferences, TripRecord


class TestMemoryService:
    """Test suite for memory service functionality."""
    
    @pytest.fixture
    def memory_service(self):
        """Create a fresh memory service for each test."""
        return MemoryService()
    
    def test_create_user_preferences(self, memory_service):
        """Test creating user preferences."""
        user_id = "user123"
        preferences = memory_service.create_user_preferences(user_id)
        
        assert preferences.user_id == user_id
        assert preferences.preferred_travel_style == "balanced"
        assert preferences.home_currency == "USD"
        assert len(memory_service.user_preferences) == 1
    
    def test_get_user_preferences(self, memory_service):
        """Test retrieving user preferences."""
        user_id = "user123"
        created = memory_service.create_user_preferences(user_id)
        retrieved = memory_service.get_user_preferences(user_id)
        
        assert retrieved is not None
        assert retrieved.user_id == created.user_id
        assert retrieved.home_currency == created.home_currency
    
    def test_update_user_preferences(self, memory_service):
        """Test updating user preferences."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        
        updates = {
            "preferred_travel_style": "luxury",
            "home_currency": "EUR",
            "preferred_activities": ["hiking", "museums"]
        }
        
        updated = memory_service.update_user_preferences(user_id, updates)
        
        assert updated.preferred_travel_style == "luxury"
        assert updated.home_currency == "EUR"
        assert "hiking" in updated.preferred_activities
    
    def test_add_activity_preference(self, memory_service):
        """Test adding activity preferences."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        
        memory_service.add_activity_preference(user_id, "hiking")
        memory_service.add_activity_preference(user_id, "museums")
        
        preferences = memory_service.get_user_preferences(user_id)
        assert "hiking" in preferences.preferred_activities
        assert "museums" in preferences.preferred_activities
        assert len(preferences.preferred_activities) == 2
    
    def test_add_cuisine_preference(self, memory_service):
        """Test adding cuisine preferences."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        
        memory_service.add_cuisine_preference(user_id, "Italian")
        memory_service.add_cuisine_preference(user_id, "Japanese")
        
        preferences = memory_service.get_user_preferences(user_id)
        assert "Italian" in preferences.preferred_cuisines
        assert "Japanese" in preferences.preferred_cuisines
    
    def test_record_trip(self, memory_service):
        """Test recording a trip."""
        user_id = "user123"
        trip = TripRecord(
            trip_id="trip1",
            user_id=user_id,
            destination="Paris",
            start_date="2025-06-01",
            end_date="2025-06-05",
            budget=3000,
            actual_cost=2800,
            rating=4.5
        )
        
        memory_service.record_trip(trip)
        history = memory_service.get_trip_history(user_id)
        
        assert len(history) == 1
        assert history[0].destination == "Paris"
        assert history[0].actual_cost == 2800
    
    def test_get_favorite_destinations(self, memory_service):
        """Test getting favorite destinations."""
        user_id = "user123"
        
        # Record multiple trips
        for i, dest in enumerate(["Paris", "Paris", "Tokyo", "Paris", "Tokyo"]):
            trip = TripRecord(
                trip_id=f"trip{i}",
                user_id=user_id,
                destination=dest,
                start_date="2025-06-01",
                end_date="2025-06-05",
                budget=3000
            )
            memory_service.record_trip(trip)
        
        favorites = memory_service.get_favorite_destinations(user_id)
        
        assert favorites[0] == "Paris"  # Most visited
        assert favorites[1] == "Tokyo"
        assert len(favorites) == 2
    
    def test_get_average_trip_cost(self, memory_service):
        """Test calculating average trip cost."""
        user_id = "user123"
        
        costs = [2000, 3000, 2500]
        for i, cost in enumerate(costs):
            trip = TripRecord(
                trip_id=f"trip{i}",
                user_id=user_id,
                destination="Paris",
                start_date="2025-06-01",
                end_date="2025-06-05",
                budget=3000,
                actual_cost=cost
            )
            memory_service.record_trip(trip)
        
        avg_cost = memory_service.get_average_trip_cost(user_id)
        
        assert avg_cost == 2500  # (2000 + 3000 + 2500) / 3
    
    def test_get_trip_rating_average(self, memory_service):
        """Test calculating average trip rating."""
        user_id = "user123"
        
        ratings = [4.0, 5.0, 3.5]
        for i, rating in enumerate(ratings):
            trip = TripRecord(
                trip_id=f"trip{i}",
                user_id=user_id,
                destination="Paris",
                start_date="2025-06-01",
                end_date="2025-06-05",
                budget=3000,
                rating=rating
            )
            memory_service.record_trip(trip)
        
        avg_rating = memory_service.get_trip_rating_average(user_id)
        
        assert abs(avg_rating - 4.167) < 0.01  # (4.0 + 5.0 + 3.5) / 3
    
    def test_export_preferences_to_json(self, memory_service):
        """Test exporting preferences to JSON."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        memory_service.add_activity_preference(user_id, "hiking")
        
        json_str = memory_service.export_preferences_to_json(user_id)
        data = json.loads(json_str)
        
        assert data["user_id"] == user_id
        assert "hiking" in data["preferred_activities"]
    
    def test_import_preferences_from_json(self, memory_service):
        """Test importing preferences from JSON."""
        user_id = "user123"
        
        json_data = {
            "user_id": user_id,
            "preferred_budget_range": {"min": 2000, "max": 4000},
            "preferred_travel_style": "adventure",
            "preferred_climate": "tropical",
            "preferred_activities": ["diving", "hiking"],
            "preferred_cuisines": ["Thai", "Vietnamese"],
            "preferred_airlines": [],
            "preferred_hotel_chains": [],
            "home_currency": "GBP",
            "home_country": "UK",
            "languages_spoken": ["English"],
            "accessibility_needs": [],
            "travel_companions": "couple",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        json_str = json.dumps(json_data)
        imported = memory_service.import_preferences_from_json(user_id, json_str)
        
        assert imported.user_id == user_id
        assert imported.preferred_travel_style == "adventure"
        assert imported.home_currency == "GBP"
    
    def test_get_recommendations_based_on_history(self, memory_service):
        """Test generating recommendations from history."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        memory_service.add_activity_preference(user_id, "hiking")
        
        # Record trips
        for i in range(3):
            trip = TripRecord(
                trip_id=f"trip{i}",
                user_id=user_id,
                destination="Paris",
                start_date="2025-06-01",
                end_date="2025-06-05",
                budget=3000,
                actual_cost=2800,
                rating=4.5
            )
            memory_service.record_trip(trip)
        
        recommendations = memory_service.get_recommendations_based_on_history(user_id)
        
        assert recommendations["total_trips"] == 3
        assert "Paris" in recommendations["favorite_destinations"]
        assert recommendations["average_trip_cost"] == 2800
    
    def test_clear_user_data(self, memory_service):
        """Test clearing user data (GDPR compliance)."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        
        trip = TripRecord(
            trip_id="trip1",
            user_id=user_id,
            destination="Paris",
            start_date="2025-06-01",
            end_date="2025-06-05",
            budget=3000
        )
        memory_service.record_trip(trip)
        
        memory_service.clear_user_data(user_id)
        
        assert memory_service.get_user_preferences(user_id) is None
        assert len(memory_service.get_trip_history(user_id)) == 0
    
    def test_get_user_summary(self, memory_service):
        """Test getting user summary."""
        user_id = "user123"
        memory_service.create_user_preferences(user_id)
        
        trip = TripRecord(
            trip_id="trip1",
            user_id=user_id,
            destination="Paris",
            start_date="2025-06-01",
            end_date="2025-06-05",
            budget=3000,
            actual_cost=2800,
            rating=4.5
        )
        memory_service.record_trip(trip)
        
        summary = memory_service.get_user_summary(user_id)
        
        assert summary["user_id"] == user_id
        assert summary["total_trips"] == 1
        assert "Paris" in summary["favorite_destinations"]
    
    @given(
        num_trips=st.integers(min_value=1, max_value=20),
        num_activities=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_preference_persistence(self, num_trips, num_activities):
        """
        Property 7: User Preference Persistence
        
        For any user with preferences and trip history, the preferences and
        history should persist and be retrievable without loss of data.
        
        Validates: Requirements 8.3, 8.4
        """
        memory_service = MemoryService()
        user_id = "test_user"
        
        # Create preferences
        memory_service.create_user_preferences(user_id)
        
        # Add activities
        activities = [f"activity_{i}" for i in range(num_activities)]
        for activity in activities:
            memory_service.add_activity_preference(user_id, activity)
        
        # Record trips
        for i in range(num_trips):
            trip = TripRecord(
                trip_id=f"trip_{i}",
                user_id=user_id,
                destination=f"destination_{i % 3}",
                start_date="2025-06-01",
                end_date="2025-06-05",
                budget=3000,
                actual_cost=2800 + i * 100,
                rating=4.0 + (i % 2) * 0.5
            )
            memory_service.record_trip(trip)
        
        # Verify persistence
        retrieved_prefs = memory_service.get_user_preferences(user_id)
        assert retrieved_prefs is not None
        assert len(retrieved_prefs.preferred_activities) == num_activities
        
        # Verify all activities are present
        for activity in activities:
            assert activity in retrieved_prefs.preferred_activities
        
        # Verify trip history
        history = memory_service.get_trip_history(user_id)
        assert len(history) == num_trips
        
        # Verify all trips are retrievable
        for i in range(num_trips):
            assert any(t.trip_id == f"trip_{i}" for t in history)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
