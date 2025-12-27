#!/usr/bin/env python3
"""
Property-Based Tests for Calendar Integration

Feature: travel-planning-agent
Property 12: Calendar Event Completeness

Validates: Requirements 13.1, 13.2
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from calendar_service import CalendarService, CalendarEvent


class TestCalendarIntegration:
    """Test suite for calendar integration functionality."""
    
    @pytest.fixture
    def calendar_service(self):
        """Create a fresh calendar service for each test."""
        return CalendarService()
    
    def test_add_flight_event(self, calendar_service):
        """Test adding a flight event to the calendar."""
        flight_info = {
            "airline": "United Airlines",
            "flight_number": "UA123",
            "departure_city": "New York",
            "arrival_city": "Paris",
            "departure_time": datetime(2025, 6, 1, 10, 0),
            "arrival_time": datetime(2025, 6, 1, 22, 0),
            "confirmation": "ABC123"
        }
        
        event = calendar_service.add_flight_event(flight_info)
        
        assert event.title == "Flight UA123 - New York to Paris"
        assert event.event_type == "flight"
        assert event.start_time == datetime(2025, 6, 1, 10, 0)
        assert event.end_time == datetime(2025, 6, 1, 22, 0)
        assert len(calendar_service.events) == 1
    
    def test_add_hotel_events(self, calendar_service):
        """Test adding hotel check-in and check-out events."""
        hotel_info = {
            "name": "Hotel Paris",
            "check_in_date": datetime(2025, 6, 1),
            "check_out_date": datetime(2025, 6, 5),
            "address": "123 Rue de Paris",
            "confirmation": "HOTEL123",
            "room_number": "501"
        }
        
        events = calendar_service.add_hotel_event(hotel_info)
        
        assert len(events) == 2
        assert events[0].title == "Hotel Check-in: Hotel Paris"
        assert events[1].title == "Hotel Check-out: Hotel Paris"
        assert events[0].event_type == "hotel"
        assert events[1].event_type == "hotel"
        assert len(calendar_service.events) == 2
    
    def test_add_activity_event(self, calendar_service):
        """Test adding an activity event."""
        activity_info = {
            "name": "Louvre Museum",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 12, 0),
            "location": "Paris, France",
            "description": "Visit the Louvre Museum",
            "category": "museum"
        }
        
        event = calendar_service.add_activity_event(activity_info)
        
        assert event.title == "Louvre Museum"
        assert event.event_type == "activity"
        assert event.start_time == datetime(2025, 6, 2, 9, 0)
        assert len(calendar_service.events) == 1
    
    def test_add_meal_event(self, calendar_service):
        """Test adding a meal/restaurant event."""
        meal_info = {
            "restaurant": "Le Bernardin",
            "time": datetime(2025, 6, 2, 19, 0),
            "duration": 120,
            "address": "155 West 51st Street, New York",
            "reservation": "RES123",
            "cuisine": "French"
        }
        
        event = calendar_service.add_meal_event(meal_info)
        
        assert event.title == "Dinner: Le Bernardin"
        assert event.event_type == "meal"
        assert event.start_time == datetime(2025, 6, 2, 19, 0)
        assert event.end_time == datetime(2025, 6, 2, 21, 0)
        assert len(calendar_service.events) == 1
    
    def test_export_to_ical(self, calendar_service):
        """Test exporting events to iCalendar format."""
        # Add some events
        flight_info = {
            "airline": "United",
            "flight_number": "UA123",
            "departure_city": "NYC",
            "arrival_city": "Paris",
            "departure_time": datetime(2025, 6, 1, 10, 0),
            "arrival_time": datetime(2025, 6, 1, 22, 0),
            "confirmation": "ABC123"
        }
        calendar_service.add_flight_event(flight_info)
        
        ical_content = calendar_service.export_to_ical()
        
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        assert "BEGIN:VEVENT" in ical_content
        assert "END:VEVENT" in ical_content
        assert "Flight UA123" in ical_content
    
    def test_export_to_json(self, calendar_service):
        """Test exporting events to JSON format."""
        activity_info = {
            "name": "Museum Visit",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 12, 0),
            "location": "Paris",
            "description": "Visit museum",
            "category": "museum"
        }
        calendar_service.add_activity_event(activity_info)
        
        json_data = calendar_service.export_to_json()
        
        assert "calendar" in json_data
        assert json_data["calendar"]["event_count"] == 1
        assert len(json_data["calendar"]["events"]) == 1
        assert json_data["calendar"]["events"][0]["title"] == "Museum Visit"
    
    def test_detect_conflicts(self, calendar_service):
        """Test detecting calendar conflicts."""
        # Add overlapping events
        activity1 = {
            "name": "Activity 1",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 11, 0),
            "location": "Paris",
            "description": "Activity 1"
        }
        activity2 = {
            "name": "Activity 2",
            "start_time": datetime(2025, 6, 2, 10, 0),
            "end_time": datetime(2025, 6, 2, 12, 0),
            "location": "Paris",
            "description": "Activity 2"
        }
        
        calendar_service.add_activity_event(activity1)
        calendar_service.add_activity_event(activity2)
        
        conflicts = calendar_service.detect_conflicts()
        
        assert len(conflicts) == 1
        assert conflicts[0]["event1"] == "Activity 1"
        assert conflicts[0]["event2"] == "Activity 2"
        assert conflicts[0]["overlap_minutes"] == 60
    
    def test_get_events_by_date(self, calendar_service):
        """Test retrieving events by date."""
        # Add events on different dates
        activity1 = {
            "name": "Activity 1",
            "start_time": datetime(2025, 6, 1, 9, 0),
            "end_time": datetime(2025, 6, 1, 11, 0),
            "location": "Paris",
            "description": "Activity 1"
        }
        activity2 = {
            "name": "Activity 2",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 11, 0),
            "location": "Paris",
            "description": "Activity 2"
        }
        
        calendar_service.add_activity_event(activity1)
        calendar_service.add_activity_event(activity2)
        
        events_june1 = calendar_service.get_events_by_date(datetime(2025, 6, 1))
        events_june2 = calendar_service.get_events_by_date(datetime(2025, 6, 2))
        
        assert len(events_june1) == 1
        assert len(events_june2) == 1
        assert events_june1[0].title == "Activity 1"
        assert events_june2[0].title == "Activity 2"
    
    def test_get_events_by_type(self, calendar_service):
        """Test retrieving events by type."""
        flight_info = {
            "airline": "United",
            "flight_number": "UA123",
            "departure_city": "NYC",
            "arrival_city": "Paris",
            "departure_time": datetime(2025, 6, 1, 10, 0),
            "arrival_time": datetime(2025, 6, 1, 22, 0),
            "confirmation": "ABC123"
        }
        activity_info = {
            "name": "Museum",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 12, 0),
            "location": "Paris",
            "description": "Museum visit"
        }
        
        calendar_service.add_flight_event(flight_info)
        calendar_service.add_activity_event(activity_info)
        
        flights = calendar_service.get_events_by_type("flight")
        activities = calendar_service.get_events_by_type("activity")
        
        assert len(flights) == 1
        assert len(activities) == 1
        assert flights[0].event_type == "flight"
        assert activities[0].event_type == "activity"
    
    def test_get_summary(self, calendar_service):
        """Test getting calendar summary."""
        flight_info = {
            "airline": "United",
            "flight_number": "UA123",
            "departure_city": "NYC",
            "arrival_city": "Paris",
            "departure_time": datetime(2025, 6, 1, 10, 0),
            "arrival_time": datetime(2025, 6, 1, 22, 0),
            "confirmation": "ABC123"
        }
        activity_info = {
            "name": "Museum",
            "start_time": datetime(2025, 6, 2, 9, 0),
            "end_time": datetime(2025, 6, 2, 12, 0),
            "location": "Paris",
            "description": "Museum visit"
        }
        
        calendar_service.add_flight_event(flight_info)
        calendar_service.add_activity_event(activity_info)
        
        summary = calendar_service.get_summary()
        
        assert summary["total_events"] == 2
        assert summary["event_types"]["flight"] == 1
        assert summary["event_types"]["activity"] == 1
        assert "date_range" in summary
    
    @given(
        num_events=st.integers(min_value=1, max_value=10),
        days_span=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_calendar_event_completeness(self, num_events, days_span):
        """
        Property 12: Calendar Event Completeness
        
        For any trip with flights, hotels, and activities, the exported calendar
        should contain events for all flights, hotel check-ins/check-outs, and
        scheduled activities.
        
        Validates: Requirements 13.1, 13.2
        """
        calendar_service = CalendarService()
        base_date = datetime(2025, 6, 1)
        
        # Add flight
        flight_info = {
            "airline": "United",
            "flight_number": "UA123",
            "departure_city": "NYC",
            "arrival_city": "Paris",
            "departure_time": base_date,
            "arrival_time": base_date + timedelta(hours=12),
            "confirmation": "ABC123"
        }
        calendar_service.add_flight_event(flight_info)
        
        # Add hotel
        hotel_info = {
            "name": "Hotel Paris",
            "check_in_date": base_date,
            "check_out_date": base_date + timedelta(days=days_span),
            "address": "123 Rue de Paris",
            "confirmation": "HOTEL123"
        }
        calendar_service.add_hotel_event(hotel_info)
        
        # Add activities
        for i in range(num_events):
            activity_info = {
                "name": f"Activity {i+1}",
                "start_time": base_date + timedelta(days=i+1, hours=9),
                "end_time": base_date + timedelta(days=i+1, hours=12),
                "location": "Paris",
                "description": f"Activity {i+1}"
            }
            calendar_service.add_activity_event(activity_info)
        
        # Export to iCal and verify all events are present
        ical_content = calendar_service.export_to_ical()
        
        # Verify flight is in calendar
        assert "Flight UA123" in ical_content
        
        # Verify hotel events are in calendar
        assert "Hotel Check-in" in ical_content
        assert "Hotel Check-out" in ical_content
        
        # Verify all activities are in calendar
        for i in range(num_events):
            assert f"Activity {i+1}" in ical_content
        
        # Verify event count
        event_count = ical_content.count("BEGIN:VEVENT")
        expected_count = 1 + 2 + num_events  # flight + hotel (check-in/out) + activities
        assert event_count == expected_count


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
