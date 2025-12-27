#!/usr/bin/env python3
"""
Tests for Streamlit UI application

Validates that all Streamlit components can be imported and initialized correctly.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trip_planner import TripPlanner
from validation import TravelValidator, ErrorHandler
from calendar_service import CalendarService
from memory_service import MemoryService
from alerts_service import AlertsService


def test_imports():
    """Test that all required modules can be imported."""
    try:
        import streamlit as st
        assert st is not None
        print("✓ Streamlit import successful")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        raise


def test_trip_planner_initialization():
    """Test TripPlanner initialization."""
    planner = TripPlanner()
    assert planner is not None
    assert hasattr(planner, 'create_trip_plan')
    assert hasattr(planner, 'export_plan')
    assert hasattr(planner, 'memory_service')
    assert hasattr(planner, 'alerts_service')
    print("✓ TripPlanner initialization successful")


def test_validation_service():
    """Test validation service."""
    result = TravelValidator.validate_trip_plan(
        destination="Paris",
        start_date="2026-01-04",
        end_date="2026-01-11",
        travelers=1,
        budget=3000.0,
        currency="USD"
    )
    assert result.is_valid
    print("✓ Validation service working")


def test_memory_service():
    """Test memory service."""
    planner = TripPlanner()
    memory = planner.memory_service
    
    # Create preferences
    prefs = memory.create_user_preferences("test_user")
    assert prefs is not None
    assert prefs.user_id == "test_user"
    
    # Get preferences
    retrieved = memory.get_user_preferences("test_user")
    assert retrieved is not None
    
    print("✓ Memory service working")


def test_alerts_service():
    """Test alerts service."""
    planner = TripPlanner()
    alerts = planner.alerts_service
    
    # Get summary
    summary = alerts.get_summary()
    assert "total_alerts" in summary
    assert "price_monitors" in summary
    assert "flight_monitors" in summary
    assert "weather_monitors" in summary
    
    print("✓ Alerts service working")


def test_calendar_service():
    """Test calendar service."""
    calendar = CalendarService()
    
    # Add flight event
    flight_info = {
        "airline": "Air France",
        "flight_number": "AF123",
        "departure_city": "New York",
        "arrival_city": "Paris",
        "departure_time": datetime.now() + timedelta(days=10),
        "arrival_time": datetime.now() + timedelta(days=10, hours=8),
        "confirmation": "ABC123"
    }
    event = calendar.add_flight_event(flight_info)
    assert event is not None
    
    # Get events
    events = calendar.events
    assert len(events) > 0
    
    print("✓ Calendar service working")


def test_trip_plan_creation():
    """Test trip plan creation."""
    planner = TripPlanner()
    
    plan = planner.create_trip_plan(
        source="New York",
        destination="Paris",
        start_date="2026-01-04",
        end_date="2026-01-11",
        travelers=1,
        budget=3000.0,
        currency="USD",
        user_id="test_user"
    )
    
    assert plan is not None
    assert plan.source == "New York"
    assert plan.destination == "Paris"
    assert plan.travelers == 1
    assert plan.budget == 3000.0
    assert plan.currency == "USD"
    
    print("✓ Trip plan creation successful")


def test_plan_export():
    """Test plan export functionality."""
    planner = TripPlanner()
    
    plan = planner.create_trip_plan(
        source="New York",
        destination="Paris",
        start_date="2026-01-04",
        end_date="2026-01-11",
        travelers=1,
        budget=3000.0,
        currency="USD",
        user_id="test_user"
    )
    
    # Export as JSON
    json_export = planner.export_plan(plan, format="json")
    assert json_export is not None
    assert isinstance(json_export, str)
    
    # Verify it's valid JSON
    parsed = json.loads(json_export)
    assert parsed["destination"] == "Paris"
    assert parsed["source"] == "New York"
    
    # Export as text
    text_export = planner.export_plan(plan, format="text")
    assert text_export is not None
    assert isinstance(text_export, str)
    assert "Paris" in text_export
    assert "New York" in text_export
    
    print("✓ Plan export working")


def test_error_handling():
    """Test error handling."""
    # Test invalid destination
    result = TravelValidator.validate_trip_plan(
        destination="",
        start_date="2026-01-04",
        end_date="2026-01-11",
        travelers=1,
        budget=3000.0,
        currency="USD"
    )
    assert not result.is_valid
    assert len(result.errors) > 0
    
    # Test invalid dates
    result = TravelValidator.validate_trip_plan(
        destination="Paris",
        start_date="2026-01-11",
        end_date="2026-01-04",
        travelers=1,
        budget=3000.0,
        currency="USD"
    )
    assert not result.is_valid
    
    # Test invalid budget
    result = TravelValidator.validate_trip_plan(
        destination="Paris",
        start_date="2026-01-04",
        end_date="2026-01-11",
        travelers=1,
        budget=50.0,
        currency="USD"
    )
    assert not result.is_valid
    
    print("✓ Error handling working")


def test_preferences_management():
    """Test preferences management."""
    planner = TripPlanner()
    memory = planner.memory_service
    
    # Create preferences
    prefs = memory.create_user_preferences("test_user_2")
    
    # Update preferences
    updates = {
        "preferred_travel_style": "luxury",
        "preferred_climate": "tropical",
        "home_currency": "EUR"
    }
    memory.update_user_preferences("test_user_2", updates)
    
    # Verify updates
    updated = memory.get_user_preferences("test_user_2")
    assert updated.preferred_travel_style == "luxury"
    assert updated.preferred_climate == "tropical"
    assert updated.home_currency == "EUR"
    
    print("✓ Preferences management working")


def test_alerts_monitoring():
    """Test alerts monitoring."""
    planner = TripPlanner()
    alerts = planner.alerts_service
    
    # Add price monitor
    alerts.add_price_monitor(
        item_id="flight_123",
        item_type="flight",
        price=1500.0,
        currency="USD",
        threshold_percent=5.0
    )
    
    # Get unread alerts
    unread = alerts.get_unread_alerts()
    assert isinstance(unread, list)
    
    # Get summary
    summary = alerts.get_summary()
    assert summary["price_monitors"] >= 1
    
    print("✓ Alerts monitoring working")


def test_calendar_export():
    """Test calendar export."""
    calendar = CalendarService()
    
    # Add flight event
    flight_info = {
        "airline": "Air France",
        "flight_number": "AF123",
        "departure_city": "New York",
        "arrival_city": "Paris",
        "departure_time": datetime.now() + timedelta(days=10),
        "arrival_time": datetime.now() + timedelta(days=10, hours=8),
        "confirmation": "ABC123"
    }
    calendar.add_flight_event(flight_info)
    
    # Export to iCal
    ical_export = calendar.export_to_ical()
    assert ical_export is not None
    assert "BEGIN:VCALENDAR" in ical_export
    assert "AF123" in ical_export
    
    # Export to JSON
    json_export = calendar.export_to_json()
    assert json_export is not None
    assert isinstance(json_export, dict)
    assert len(json_export) > 0
    
    print("✓ Calendar export working")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("STREAMLIT APP COMPONENT TESTS")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("TripPlanner Initialization", test_trip_planner_initialization),
        ("Validation Service", test_validation_service),
        ("Memory Service", test_memory_service),
        ("Alerts Service", test_alerts_service),
        ("Calendar Service", test_calendar_service),
        ("Trip Plan Creation", test_trip_plan_creation),
        ("Plan Export", test_plan_export),
        ("Error Handling", test_error_handling),
        ("Preferences Management", test_preferences_management),
        ("Alerts Monitoring", test_alerts_monitoring),
        ("Calendar Export", test_calendar_export),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTesting: {test_name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
