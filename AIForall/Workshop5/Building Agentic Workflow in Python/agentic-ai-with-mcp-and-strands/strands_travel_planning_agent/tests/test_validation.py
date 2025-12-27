#!/usr/bin/env python3
"""
Tests for Validation and Error Handling

Tests input validation, error handling, and data consistency.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation import (
    TravelValidator, ErrorHandler, DataConsistencyValidator,
    ValidationResult, ValidationError, ErrorSeverity
)


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(True)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_invalid_result_with_errors(self):
        """Test creating an invalid result with errors."""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(False, errors=errors)
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
    
    def test_result_with_warnings(self):
        """Test result with warnings."""
        warnings = ["Warning 1"]
        result = ValidationResult(True, warnings=warnings)
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult(False, errors=["Error"], warnings=["Warning"])
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert result_dict["error_count"] == 1
        assert result_dict["warning_count"] == 1


class TestDestinationValidation:
    """Tests for destination validation."""
    
    def test_valid_destination(self):
        """Test valid destination."""
        result = TravelValidator.validate_destination("Paris")
        assert result.is_valid is True
    
    def test_empty_destination(self):
        """Test empty destination."""
        result = TravelValidator.validate_destination("")
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_destination_too_short(self):
        """Test destination too short."""
        result = TravelValidator.validate_destination("A")
        assert result.is_valid is False
    
    def test_destination_too_long(self):
        """Test destination too long."""
        long_dest = "A" * 101
        result = TravelValidator.validate_destination(long_dest)
        assert result.is_valid is False
    
    def test_destination_with_invalid_chars(self):
        """Test destination with invalid characters."""
        result = TravelValidator.validate_destination("Paris@#$")
        assert result.is_valid is False
    
    def test_destination_not_string(self):
        """Test destination not a string."""
        result = TravelValidator.validate_destination(123)
        assert result.is_valid is False


class TestDateValidation:
    """Tests for date validation."""
    
    def test_valid_dates(self):
        """Test valid dates."""
        start = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_dates(start, end)
        assert result.is_valid is True
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        result = TravelValidator.validate_dates("2025/06/01", "2025/06/08")
        assert result.is_valid is False
    
    def test_past_dates(self):
        """Test past dates."""
        start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        end = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_dates(start, end)
        assert result.is_valid is False
    
    def test_start_after_end(self):
        """Test start date after end date."""
        start = (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_dates(start, end)
        assert result.is_valid is False
    
    def test_same_start_and_end(self):
        """Test same start and end date."""
        date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_dates(date, date)
        assert result.is_valid is False
    
    def test_trip_too_long(self):
        """Test trip duration exceeds maximum."""
        start = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_dates(start, end)
        assert result.is_valid is False


class TestBudgetValidation:
    """Tests for budget validation."""
    
    def test_valid_budget(self):
        """Test valid budget."""
        result = TravelValidator.validate_budget(2000.0)
        assert result.is_valid is True
    
    def test_budget_too_low(self):
        """Test budget below minimum."""
        result = TravelValidator.validate_budget(50.0)
        assert result.is_valid is False
    
    def test_budget_too_high(self):
        """Test budget above maximum."""
        result = TravelValidator.validate_budget(2000000.0)
        assert result.is_valid is False
    
    def test_negative_budget(self):
        """Test negative budget."""
        result = TravelValidator.validate_budget(-1000.0)
        assert result.is_valid is False
    
    def test_zero_budget(self):
        """Test zero budget."""
        result = TravelValidator.validate_budget(0)
        assert result.is_valid is False
    
    def test_budget_not_number(self):
        """Test budget not a number."""
        result = TravelValidator.validate_budget("2000")
        assert result.is_valid is False


class TestTravelersValidation:
    """Tests for travelers validation."""
    
    def test_valid_travelers(self):
        """Test valid number of travelers."""
        result = TravelValidator.validate_travelers(2)
        assert result.is_valid is True
    
    def test_zero_travelers(self):
        """Test zero travelers."""
        result = TravelValidator.validate_travelers(0)
        assert result.is_valid is False
    
    def test_too_many_travelers(self):
        """Test too many travelers."""
        result = TravelValidator.validate_travelers(101)
        assert result.is_valid is False
    
    def test_large_group_warning(self):
        """Test warning for large group."""
        result = TravelValidator.validate_travelers(15)
        assert result.is_valid is True
        assert len(result.warnings) > 0
    
    def test_travelers_not_integer(self):
        """Test travelers not an integer."""
        result = TravelValidator.validate_travelers(2.5)
        assert result.is_valid is False


class TestCurrencyValidation:
    """Tests for currency validation."""
    
    def test_valid_currency(self):
        """Test valid currency."""
        result = TravelValidator.validate_currency("USD")
        assert result.is_valid is True
    
    def test_lowercase_currency(self):
        """Test lowercase currency."""
        result = TravelValidator.validate_currency("usd")
        assert result.is_valid is True
    
    def test_invalid_currency_length(self):
        """Test invalid currency length."""
        result = TravelValidator.validate_currency("US")
        assert result.is_valid is False
    
    def test_unsupported_currency(self):
        """Test unsupported currency."""
        result = TravelValidator.validate_currency("XYZ")
        assert result.is_valid is True  # Still valid, but with warning
        assert len(result.warnings) > 0
    
    def test_currency_not_string(self):
        """Test currency not a string."""
        result = TravelValidator.validate_currency(123)
        assert result.is_valid is False


class TestTripPlanValidation:
    """Tests for complete trip plan validation."""
    
    def test_valid_trip_plan(self):
        """Test valid trip plan."""
        start = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d")
        
        result = TravelValidator.validate_trip_plan(
            destination="Paris",
            start_date=start,
            end_date=end,
            travelers=2,
            budget=3000.0,
            currency="USD"
        )
        
        assert result.is_valid is True
    
    def test_invalid_trip_plan_multiple_errors(self):
        """Test invalid trip plan with multiple errors."""
        result = TravelValidator.validate_trip_plan(
            destination="",
            start_date="invalid",
            end_date="invalid",
            travelers=0,
            budget=-100,
            currency="INVALID"
        )
        
        assert result.is_valid is False
        assert len(result.errors) > 0


class TestFlightValidation:
    """Tests for flight information validation."""
    
    def test_valid_flight_info(self):
        """Test valid flight information."""
        flight_info = {
            "airline": "Air France",
            "flight_number": "AF100",
            "departure_time": "2025-06-01T10:00:00",
            "arrival_time": "2025-06-01T22:00:00",
            "total_cost": 800.0
        }
        
        result = TravelValidator.validate_flight_info(flight_info)
        assert result.is_valid is True
    
    def test_missing_required_field(self):
        """Test missing required field."""
        flight_info = {
            "airline": "Air France",
            "flight_number": "AF100"
        }
        
        result = TravelValidator.validate_flight_info(flight_info)
        assert result.is_valid is False
    
    def test_negative_flight_cost(self):
        """Test negative flight cost."""
        flight_info = {
            "airline": "Air France",
            "flight_number": "AF100",
            "departure_time": "2025-06-01T10:00:00",
            "arrival_time": "2025-06-01T22:00:00",
            "total_cost": -100.0
        }
        
        result = TravelValidator.validate_flight_info(flight_info)
        assert result.is_valid is False


class TestHotelValidation:
    """Tests for hotel information validation."""
    
    def test_valid_hotel_info(self):
        """Test valid hotel information."""
        hotel_info = {
            "name": "Hotel Le Marais",
            "check_in_date": "2025-06-01",
            "check_out_date": "2025-06-08",
            "address": "123 Rue de Rivoli, Paris",
            "total_cost": 1200.0
        }
        
        result = TravelValidator.validate_hotel_info(hotel_info)
        assert result.is_valid is True
    
    def test_missing_required_field(self):
        """Test missing required field."""
        hotel_info = {
            "name": "Hotel Le Marais",
            "check_in_date": "2025-06-01"
        }
        
        result = TravelValidator.validate_hotel_info(hotel_info)
        assert result.is_valid is False


class TestBudgetBreakdownValidation:
    """Tests for budget breakdown validation."""
    
    def test_valid_budget_breakdown(self):
        """Test valid budget breakdown."""
        breakdown = {
            "flights": 800.0,
            "hotels": 1200.0,
            "activities": 400.0,
            "food": 500.0,
            "total": 2900.0
        }
        
        result = TravelValidator.validate_budget_breakdown(breakdown, 3000.0)
        assert result.is_valid is True
    
    def test_budget_exceeds_total(self):
        """Test budget breakdown exceeds total."""
        breakdown = {
            "flights": 2000.0,
            "hotels": 2000.0,
            "total": 4000.0
        }
        
        result = TravelValidator.validate_budget_breakdown(breakdown, 3000.0)
        assert result.is_valid is True
        assert len(result.warnings) > 0
    
    def test_negative_category(self):
        """Test negative category amount."""
        breakdown = {
            "flights": -100.0,
            "total": -100.0
        }
        
        result = TravelValidator.validate_budget_breakdown(breakdown, 3000.0)
        assert result.is_valid is False


class TestErrorHandler:
    """Tests for error handling."""
    
    def test_get_user_friendly_message(self):
        """Test getting user-friendly error message."""
        message = ErrorHandler.get_user_friendly_message("invalid_destination")
        assert "destination" in message.lower()
    
    def test_handle_validation_error_success(self):
        """Test handling successful validation."""
        result = ValidationResult(True)
        success, message = ErrorHandler.handle_validation_error(result)
        
        assert success is True
    
    def test_handle_validation_error_failure(self):
        """Test handling failed validation."""
        result = ValidationResult(False, errors=["Error 1", "Error 2"])
        success, message = ErrorHandler.handle_validation_error(result)
        
        assert success is False
        assert "Error 1" in message
    
    def test_handle_exception(self):
        """Test handling exception."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_info = ErrorHandler.handle_exception(e, "test_context")
        
        assert error_info["success"] is False
        assert "ValueError" in error_info["error_type"]


class TestDataConsistencyValidator:
    """Tests for data consistency validation."""
    
    def test_valid_trip_consistency(self):
        """Test valid trip consistency."""
        trip_plan = {
            "destination": "Paris",
            "start_date": "2025-06-01",
            "end_date": "2025-06-08",
            "budget": 3000.0,
            "budget_breakdown": {"total": 2900.0}
        }
        
        result = DataConsistencyValidator.validate_trip_consistency(trip_plan)
        assert result.is_valid is True
    
    def test_missing_required_field(self):
        """Test missing required field."""
        trip_plan = {
            "destination": "Paris",
            "start_date": "2025-06-01"
        }
        
        result = DataConsistencyValidator.validate_trip_consistency(trip_plan)
        assert result.is_valid is False
    
    def test_budget_consistency(self):
        """Test budget consistency across components."""
        flights = {"total_cost": 800.0}
        hotels = {"total_cost": 1200.0}
        activities = {"total_cost": 400.0}
        
        result = DataConsistencyValidator.validate_budget_consistency(
            flights, hotels, activities, 3000.0
        )
        
        assert result.is_valid is True
    
    def test_budget_exceeds_total(self):
        """Test budget exceeds total."""
        flights = {"total_cost": 2000.0}
        hotels = {"total_cost": 2000.0}
        activities = {"total_cost": 500.0}
        
        result = DataConsistencyValidator.validate_budget_consistency(
            flights, hotels, activities, 3000.0
        )
        
        assert result.is_valid is True
        assert len(result.warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
