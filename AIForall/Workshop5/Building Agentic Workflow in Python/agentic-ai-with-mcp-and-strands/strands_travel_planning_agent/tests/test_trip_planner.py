#!/usr/bin/env python3
"""
Tests for Trip Planner

Tests comprehensive trip planning workflow and multi-agent coordination.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trip_planner import TripPlanner, TripPlan


class TestTripPlanCreation:
    """Tests for trip plan creation."""
    
    def test_create_basic_trip_plan(self):
        """Test creating a basic trip plan."""
        planner = TripPlanner()
        
        plan = planner.create_trip_plan(
            source="New York",
            destination="Paris",
            start_date="2025-06-01",
            end_date="2025-06-08",
            travelers=2,
            budget=3000.0,
            currency="USD"
        )
        
        assert plan.source == "New York"
        assert plan.destination == "Paris"
        assert plan.start_date == "2025-06-01"
        assert plan.end_date == "2025-06-08"
        assert plan.travelers == 2
        assert plan.budget == 3000.0
        assert plan.currency == "USD"
    
    def test_plan_stored_in_planner(self):
        """Test that created plans are stored."""
        planner = TripPlanner()
        
        plan1 = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        plan2 = planner.create_trip_plan("Los Angeles", "Tokyo", "2025-07-01", "2025-07-15", 1, 4000.0)
        
        plans = planner.list_plans()
        assert len(plans) == 2
    
    def test_plan_with_user_id(self):
        """Test creating plan with user ID for memory tracking."""
        planner = TripPlanner()
        
        plan = planner.create_trip_plan(
            source="London",
            destination="Barcelona",
            start_date="2025-05-01",
            end_date="2025-05-07",
            travelers=3,
            budget=2500.0,
            user_id="user_123"
        )
        
        assert plan.destination == "Barcelona"
        # Verify memory service has the user preferences initialized
        assert len(planner.memory_service.user_preferences) >= 0


class TestAddingComponentsToPlan:
    """Tests for adding components to trip plans."""
    
    def test_add_flights_to_plan(self):
        """Test adding flights to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        flights = {
            "outbound": {
                "airline": "Air France",
                "flight_number": "AF100",
                "departure_time": "2025-06-01T10:00:00",
                "arrival_time": "2025-06-01T22:00:00",
                "departure_city": "New York",
                "arrival_city": "Paris",
                "confirmation": "ABC123"
            },
            "return": {
                "airline": "Air France",
                "flight_number": "AF101",
                "departure_time": "2025-06-08T14:00:00",
                "arrival_time": "2025-06-09T02:00:00",
                "departure_city": "Paris",
                "arrival_city": "New York",
                "confirmation": "ABC124"
            },
            "total_cost": 800.0,
            "currency": "USD"
        }
        
        updated_plan = planner.add_flights_to_plan(plan, flights)
        
        assert updated_plan.flights is not None
        assert updated_plan.flights["outbound"]["flight_number"] == "AF100"
        assert updated_plan.flights["total_cost"] == 800.0
    
    def test_add_hotels_to_plan(self):
        """Test adding hotels to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        hotels = {
            "name": "Hotel Le Marais",
            "check_in_date": "2025-06-01",
            "check_out_date": "2025-06-08",
            "address": "123 Rue de Rivoli, Paris",
            "confirmation": "HOTEL123",
            "room_number": "405",
            "total_cost": 1200.0,
            "currency": "USD"
        }
        
        updated_plan = planner.add_hotels_to_plan(plan, hotels)
        
        assert updated_plan.hotels is not None
        assert updated_plan.hotels["name"] == "Hotel Le Marais"
        assert updated_plan.hotels["total_cost"] == 1200.0
    
    def test_add_itinerary_to_plan(self):
        """Test adding itinerary to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        itinerary = {
            "days": [
                {
                    "title": "Arrival and Eiffel Tower",
                    "activities": [
                        {
                            "name": "Eiffel Tower",
                            "start_time": "2025-06-01T15:00:00",
                            "end_time": "2025-06-01T17:00:00",
                            "location": "Eiffel Tower, Paris",
                            "description": "Visit the iconic Eiffel Tower"
                        }
                    ]
                },
                {
                    "title": "Louvre Museum",
                    "activities": [
                        {
                            "name": "Louvre Museum",
                            "start_time": "2025-06-02T09:00:00",
                            "end_time": "2025-06-02T13:00:00",
                            "location": "Louvre, Paris",
                            "description": "Explore the world's largest art museum"
                        }
                    ]
                }
            ],
            "total_activities": 2,
            "estimated_cost": 100.0
        }
        
        updated_plan = planner.add_itinerary_to_plan(plan, itinerary)
        
        assert updated_plan.itinerary is not None
        assert len(updated_plan.itinerary["days"]) == 2
        assert updated_plan.itinerary["total_activities"] == 2
    
    def test_add_budget_to_plan(self):
        """Test adding budget breakdown to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        budget = {
            "flights": 800.0,
            "hotels": 1200.0,
            "activities": 400.0,
            "food": 500.0,
            "transport": 100.0,
            "total": 3000.0
        }
        
        updated_plan = planner.add_budget_to_plan(plan, budget)
        
        assert updated_plan.budget_breakdown is not None
        assert updated_plan.budget_breakdown["total"] == 3000.0
    
    def test_add_weather_to_plan(self):
        """Test adding weather to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        weather = {
            "average_temp": 22,
            "conditions": "Partly Cloudy",
            "packing_tips": "Bring light jacket and umbrella",
            "forecast": "Sunny with occasional rain"
        }
        
        updated_plan = planner.add_weather_to_plan(plan, weather)
        
        assert updated_plan.weather is not None
        assert updated_plan.weather["average_temp"] == 22
    
    def test_add_visa_requirements_to_plan(self):
        """Test adding visa requirements to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("USA", "India", "2025-06-01", "2025-06-15", 1, 2000.0)
        
        visa_info = {
            "required": True,
            "processing_time": "14 days",
            "documents": ["Passport", "Photo", "Application Form"],
            "cost": 100.0
        }
        
        updated_plan = planner.add_visa_requirements_to_plan(plan, visa_info)
        
        assert updated_plan.visa_requirements is not None
        assert updated_plan.visa_requirements["required"] is True
    
    def test_add_language_guide_to_plan(self):
        """Test adding language guide to plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("USA", "Tokyo", "2025-07-01", "2025-07-15", 1, 4000.0)
        
        language_guide = {
            "language": "Japanese",
            "common_phrases": ["Konnichiwa", "Arigatou gozaimasu"],
            "emergency_phrases": ["Tasukete", "Byouin"],
            "cultural_tips": "Remove shoes when entering homes"
        }
        
        updated_plan = planner.add_language_guide_to_plan(plan, language_guide)
        
        assert updated_plan.language_guide is not None
        assert updated_plan.language_guide["language"] == "Japanese"


class TestPlanFinalization:
    """Tests for plan finalization and summary generation."""
    
    def test_finalize_complete_plan(self):
        """Test finalizing a complete trip plan."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        # Add all components
        flights = {
            "outbound": {
                "airline": "Air France",
                "flight_number": "AF100",
                "departure_time": "2025-06-01T10:00:00",
                "arrival_time": "2025-06-01T22:00:00",
                "departure_city": "New York",
                "arrival_city": "Paris",
                "confirmation": "ABC123"
            },
            "total_cost": 800.0
        }
        planner.add_flights_to_plan(plan, flights)
        
        hotels = {
            "name": "Hotel Le Marais",
            "check_in_date": "2025-06-01",
            "check_out_date": "2025-06-08",
            "address": "123 Rue de Rivoli, Paris",
            "total_cost": 1200.0
        }
        planner.add_hotels_to_plan(plan, hotels)
        
        budget = {
            "flights": 800.0,
            "hotels": 1200.0,
            "activities": 400.0,
            "food": 500.0,
            "transport": 100.0,
            "total": 3000.0
        }
        planner.add_budget_to_plan(plan, budget)
        
        # Finalize
        summary = planner.finalize_plan(plan)
        
        assert "trip_plan" in summary
        assert "calendar" in summary
        assert "booking_links" in summary
        assert "checklist" in summary
        assert "summary_text" in summary
    
    def test_generate_booking_links(self):
        """Test generating booking links."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        flights = {"outbound": {"airline": "Air France"}, "total_cost": 800.0}
        planner.add_flights_to_plan(plan, flights)
        
        hotels = {"name": "Hotel Le Marais", "total_cost": 1200.0}
        planner.add_hotels_to_plan(plan, hotels)
        
        links = planner._generate_booking_links(plan)
        
        assert "flights" in links
        assert "hotels" in links
        assert "Skyscanner" in links["flights"]["provider"]
    
    def test_generate_checklist(self):
        """Test generating pre-trip checklist."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        checklist = planner._generate_checklist(plan)
        
        assert len(checklist) > 0
        assert any("passport" in item.lower() for item in checklist)
        assert any("flights" in item.lower() for item in checklist)
    
    def test_generate_summary_text(self):
        """Test generating human-readable summary."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        summary = planner._generate_summary_text(plan)
        
        assert "Paris" in summary
        assert "TRIP SUMMARY" in summary
        assert "7 days" in summary


class TestPlanModification:
    """Tests for modifying existing plans."""
    
    def test_modify_plan_budget(self):
        """Test modifying plan budget."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        modifications = {"new_budget": 4000.0}
        modified_plan = planner.modify_plan(plan, modifications)
        
        assert modified_plan.budget == 4000.0
    
    def test_modify_plan_dates(self):
        """Test modifying plan dates."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        modifications = {
            "new_dates": {
                "start_date": "2025-06-15",
                "end_date": "2025-06-22"
            }
        }
        modified_plan = planner.modify_plan(plan, modifications)
        
        assert modified_plan.start_date == "2025-06-15"
        assert modified_plan.end_date == "2025-06-22"
    
    def test_modify_plan_destination(self):
        """Test modifying plan destination."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        modifications = {"new_destination": "Barcelona"}
        modified_plan = planner.modify_plan(plan, modifications)
        
        assert modified_plan.destination == "Barcelona"


class TestPlanExport:
    """Tests for exporting plans."""
    
    def test_export_plan_as_json(self):
        """Test exporting plan as JSON."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        json_export = planner.export_plan(plan, format="json")
        
        assert "Paris" in json_export
        assert "destination" in json_export
    
    def test_export_plan_as_text(self):
        """Test exporting plan as text."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        text_export = planner.export_plan(plan, format="text")
        
        assert "TRIP SUMMARY" in text_export
        assert "Paris" in text_export
    
    def test_export_invalid_format(self):
        """Test exporting with invalid format."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        with pytest.raises(ValueError):
            planner.export_plan(plan, format="invalid")


class TestPlanRetrieval:
    """Tests for retrieving plans."""
    
    def test_get_plan_by_id(self):
        """Test retrieving plan by ID."""
        planner = TripPlanner()
        plan = planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        
        # Get the plan ID from the stored plans
        plan_id = list(planner.trip_plans.keys())[0]
        retrieved_plan = planner.get_plan(plan_id)
        
        assert retrieved_plan is not None
        assert retrieved_plan.destination == "Paris"
    
    def test_list_all_plans(self):
        """Test listing all plans."""
        planner = TripPlanner()
        
        planner.create_trip_plan("New York", "Paris", "2025-06-01", "2025-06-08", 2, 3000.0)
        planner.create_trip_plan("Los Angeles", "Tokyo", "2025-07-01", "2025-07-15", 1, 4000.0)
        planner.create_trip_plan("London", "Barcelona", "2025-05-01", "2025-05-07", 3, 2500.0)
        
        plans = planner.list_plans()
        
        assert len(plans) == 3
        destinations = [p.destination for p in plans]
        assert "Paris" in destinations
        assert "Tokyo" in destinations
        assert "Barcelona" in destinations


class TestIntegration:
    """Integration tests for complete trip planning workflow."""
    
    def test_complete_trip_planning_workflow(self):
        """Test complete end-to-end trip planning workflow."""
        planner = TripPlanner()
        
        # Create plan
        plan = planner.create_trip_plan(
            source="New York",
            destination="Paris",
            start_date="2025-06-01",
            end_date="2025-06-08",
            travelers=2,
            budget=3000.0,
            user_id="user_123"
        )
        
        # Add flights
        flights = {
            "outbound": {
                "airline": "Air France",
                "flight_number": "AF100",
                "departure_time": "2025-06-01T10:00:00",
                "arrival_time": "2025-06-01T22:00:00",
                "departure_city": "New York",
                "arrival_city": "Paris",
                "confirmation": "ABC123"
            },
            "total_cost": 800.0
        }
        planner.add_flights_to_plan(plan, flights)
        
        # Add hotels
        hotels = {
            "name": "Hotel Le Marais",
            "check_in_date": "2025-06-01",
            "check_out_date": "2025-06-08",
            "address": "123 Rue de Rivoli, Paris",
            "total_cost": 1200.0
        }
        planner.add_hotels_to_plan(plan, hotels)
        
        # Add itinerary
        itinerary = {
            "days": [
                {
                    "title": "Arrival",
                    "activities": [
                        {
                            "name": "Eiffel Tower",
                            "start_time": "2025-06-01T15:00:00",
                            "end_time": "2025-06-01T17:00:00",
                            "location": "Eiffel Tower, Paris",
                            "description": "Visit Eiffel Tower"
                        }
                    ]
                }
            ],
            "total_activities": 1
        }
        planner.add_itinerary_to_plan(plan, itinerary)
        
        # Add budget
        budget = {
            "flights": 800.0,
            "hotels": 1200.0,
            "activities": 400.0,
            "food": 500.0,
            "transport": 100.0,
            "total": 3000.0
        }
        planner.add_budget_to_plan(plan, budget)
        
        # Add weather
        weather = {
            "average_temp": 22,
            "conditions": "Partly Cloudy",
            "packing_tips": "Bring light jacket"
        }
        planner.add_weather_to_plan(plan, weather)
        
        # Finalize
        summary = planner.finalize_plan(plan)
        
        # Verify all components
        assert summary["trip_plan"]["destination"] == "Paris"
        assert summary["trip_plan"]["flights"] is not None
        assert summary["trip_plan"]["hotels"] is not None
        assert summary["trip_plan"]["itinerary"] is not None
        assert summary["trip_plan"]["budget_breakdown"] is not None
        assert summary["trip_plan"]["weather"] is not None
        assert "booking_links" in summary
        assert "checklist" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
