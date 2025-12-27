#!/usr/bin/env python3
"""
Validation and Error Handling for Travel Planning Agent

Provides input validation, error handling, and user-friendly error messages.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            errors: List of error messages
            warnings: List of warning messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def __str__(self) -> str:
        """String representation."""
        if self.is_valid:
            return "Validation passed"
        
        msg = "Validation failed:\n"
        for error in self.errors:
            msg += f"  ✗ {error}\n"
        for warning in self.warnings:
            msg += f"  ⚠ {warning}\n"
        return msg


class TravelValidator:
    """Validates travel planning inputs."""
    
    # Constants
    MIN_BUDGET = 100.0
    MAX_BUDGET = 1000000.0
    MIN_TRAVELERS = 1
    MAX_TRAVELERS = 100
    MIN_TRIP_DURATION = 1
    MAX_TRIP_DURATION = 365
    
    VALID_CURRENCIES = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", 
        "INR", "MXN", "BRL", "ZAR", "SGD", "HKD", "NZD", "KRW"
    }
    
    VALID_TRAVEL_STYLES = {"budget", "luxury", "balanced", "adventure"}
    VALID_CLIMATES = {"tropical", "temperate", "cold", "desert", "mixed"}
    
    @staticmethod
    def validate_destination(destination: str) -> ValidationResult:
        """
        Validate destination input.
        
        Args:
            destination: Destination city/country
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(destination, str):
            errors.append(f"Destination must be a string, got {type(destination).__name__}")
            return ValidationResult(False, errors, warnings)
        
        destination = destination.strip()
        
        if not destination:
            errors.append("Destination cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        if len(destination) < 2:
            errors.append("Destination must be at least 2 characters long")
        
        if len(destination) > 100:
            errors.append("Destination must be less than 100 characters")
        
        if not destination[0].isalpha():
            errors.append("Destination must start with a letter")
        
        # Check for invalid characters
        invalid_chars = set(destination) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,-'")
        if invalid_chars:
            errors.append(f"Destination contains invalid characters: {invalid_chars}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_dates(start_date: str, end_date: str) -> ValidationResult:
        """
        Validate travel dates.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check format
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            errors.append(f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")
            return ValidationResult(False, errors, warnings)
        
        # Check if dates are in the future
        now = datetime.now()
        if start < now:
            errors.append(f"Start date must be in the future (provided: {start_date})")
        
        if end < now:
            errors.append(f"End date must be in the future (provided: {end_date})")
        
        # Check date order
        if start >= end:
            errors.append(f"Start date must be before end date (start: {start_date}, end: {end_date})")
        
        # Check trip duration
        if start < end:
            duration = (end - start).days
            if duration < TravelValidator.MIN_TRIP_DURATION:
                errors.append(f"Trip duration must be at least {TravelValidator.MIN_TRIP_DURATION} day")
            if duration > TravelValidator.MAX_TRIP_DURATION:
                errors.append(f"Trip duration cannot exceed {TravelValidator.MAX_TRIP_DURATION} days")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_budget(budget: float, currency: str = "USD") -> ValidationResult:
        """
        Validate budget.
        
        Args:
            budget: Budget amount
            currency: Currency code
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(budget, (int, float)):
            errors.append(f"Budget must be a number, got {type(budget).__name__}")
            return ValidationResult(False, errors, warnings)
        
        if budget < TravelValidator.MIN_BUDGET:
            errors.append(f"Budget must be at least {TravelValidator.MIN_BUDGET} {currency}")
        
        if budget > TravelValidator.MAX_BUDGET:
            errors.append(f"Budget cannot exceed {TravelValidator.MAX_BUDGET} {currency}")
        
        if budget <= 0:
            errors.append("Budget must be greater than 0")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_travelers(travelers: int) -> ValidationResult:
        """
        Validate number of travelers.
        
        Args:
            travelers: Number of travelers
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(travelers, int):
            errors.append(f"Travelers must be an integer, got {type(travelers).__name__}")
            return ValidationResult(False, errors, warnings)
        
        if travelers < TravelValidator.MIN_TRAVELERS:
            errors.append(f"Must have at least {TravelValidator.MIN_TRAVELERS} traveler")
        
        if travelers > TravelValidator.MAX_TRAVELERS:
            errors.append(f"Cannot have more than {TravelValidator.MAX_TRAVELERS} travelers")
        
        if travelers > 10:
            warnings.append(f"Large group ({travelers} travelers) may have limited accommodation options")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_currency(currency: str) -> ValidationResult:
        """
        Validate currency code.
        
        Args:
            currency: Currency code (e.g., USD, EUR)
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(currency, str):
            errors.append(f"Currency must be a string, got {type(currency).__name__}")
            return ValidationResult(False, errors, warnings)
        
        currency = currency.upper()
        
        if len(currency) != 3:
            errors.append(f"Currency code must be 3 characters (e.g., USD), got {currency}")
        
        if currency not in TravelValidator.VALID_CURRENCIES:
            warnings.append(f"Currency {currency} may not be supported. Supported: {', '.join(sorted(TravelValidator.VALID_CURRENCIES))}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_trip_plan(destination: str, start_date: str, end_date: str, 
                          travelers: int, budget: float, currency: str = "USD") -> ValidationResult:
        """
        Validate complete trip plan input.
        
        Args:
            destination: Destination
            start_date: Start date
            end_date: End date
            travelers: Number of travelers
            budget: Budget amount
            currency: Currency code
            
        Returns:
            ValidationResult
        """
        all_errors = []
        all_warnings = []
        
        # Validate each component
        dest_result = TravelValidator.validate_destination(destination)
        all_errors.extend(dest_result.errors)
        all_warnings.extend(dest_result.warnings)
        
        date_result = TravelValidator.validate_dates(start_date, end_date)
        all_errors.extend(date_result.errors)
        all_warnings.extend(date_result.warnings)
        
        travelers_result = TravelValidator.validate_travelers(travelers)
        all_errors.extend(travelers_result.errors)
        all_warnings.extend(travelers_result.warnings)
        
        budget_result = TravelValidator.validate_budget(budget, currency)
        all_errors.extend(budget_result.errors)
        all_warnings.extend(budget_result.warnings)
        
        currency_result = TravelValidator.validate_currency(currency)
        all_errors.extend(currency_result.errors)
        all_warnings.extend(currency_result.warnings)
        
        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)
    
    @staticmethod
    def validate_flight_info(flight_info: Dict) -> ValidationResult:
        """
        Validate flight information.
        
        Args:
            flight_info: Flight information dictionary
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(flight_info, dict):
            errors.append(f"Flight info must be a dictionary, got {type(flight_info).__name__}")
            return ValidationResult(False, errors, warnings)
        
        required_fields = ["airline", "flight_number", "departure_time", "arrival_time"]
        for field in required_fields:
            if field not in flight_info:
                errors.append(f"Missing required field: {field}")
        
        if "total_cost" in flight_info:
            if not isinstance(flight_info["total_cost"], (int, float)):
                errors.append(f"Flight cost must be a number, got {type(flight_info['total_cost']).__name__}")
            elif flight_info["total_cost"] < 0:
                errors.append("Flight cost cannot be negative")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_hotel_info(hotel_info: Dict) -> ValidationResult:
        """
        Validate hotel information.
        
        Args:
            hotel_info: Hotel information dictionary
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(hotel_info, dict):
            errors.append(f"Hotel info must be a dictionary, got {type(hotel_info).__name__}")
            return ValidationResult(False, errors, warnings)
        
        required_fields = ["name", "check_in_date", "check_out_date", "address"]
        for field in required_fields:
            if field not in hotel_info:
                errors.append(f"Missing required field: {field}")
        
        if "total_cost" in hotel_info:
            if not isinstance(hotel_info["total_cost"], (int, float)):
                errors.append(f"Hotel cost must be a number, got {type(hotel_info['total_cost']).__name__}")
            elif hotel_info["total_cost"] < 0:
                errors.append("Hotel cost cannot be negative")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_budget_breakdown(budget_breakdown: Dict, total_budget: float) -> ValidationResult:
        """
        Validate budget breakdown.
        
        Args:
            budget_breakdown: Budget breakdown dictionary
            total_budget: Total budget for comparison
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not isinstance(budget_breakdown, dict):
            errors.append(f"Budget breakdown must be a dictionary, got {type(budget_breakdown).__name__}")
            return ValidationResult(False, errors, warnings)
        
        if "total" not in budget_breakdown:
            errors.append("Budget breakdown must include 'total' field")
            return ValidationResult(False, errors, warnings)
        
        total = budget_breakdown["total"]
        if not isinstance(total, (int, float)):
            errors.append(f"Total budget must be a number, got {type(total).__name__}")
        elif total < 0:
            errors.append("Total budget cannot be negative")
        
        # Check if total exceeds allocated budget
        if total > total_budget:
            warnings.append(f"Estimated cost ({total}) exceeds allocated budget ({total_budget})")
        
        # Validate individual categories
        for category, amount in budget_breakdown.items():
            if category != "total":
                if not isinstance(amount, (int, float)):
                    errors.append(f"Budget category '{category}' must be a number, got {type(amount).__name__}")
                elif amount < 0:
                    errors.append(f"Budget category '{category}' cannot be negative")
        
        return ValidationResult(len(errors) == 0, errors, warnings)


class ErrorHandler:
    """Handles errors and provides user-friendly messages."""
    
    ERROR_MESSAGES = {
        "invalid_destination": "The destination you provided is not valid. Please enter a city or country name.",
        "invalid_dates": "The dates you provided are not valid. Please use YYYY-MM-DD format and ensure start date is before end date.",
        "invalid_budget": "The budget you provided is not valid. Please enter a positive number.",
        "invalid_travelers": "The number of travelers must be between 1 and 100.",
        "api_error": "An error occurred while connecting to the service. Please try again later.",
        "network_error": "A network error occurred. Please check your internet connection.",
        "timeout_error": "The request took too long. Please try again.",
        "data_error": "The data provided is not in the correct format.",
        "not_found": "The requested information was not found.",
        "permission_error": "You don't have permission to perform this action.",
        "unknown_error": "An unexpected error occurred. Please try again."
    }
    
    @staticmethod
    def get_user_friendly_message(error_type: str, details: str = "") -> str:
        """
        Get user-friendly error message.
        
        Args:
            error_type: Type of error
            details: Additional details
            
        Returns:
            User-friendly error message
        """
        message = ErrorHandler.ERROR_MESSAGES.get(error_type, ErrorHandler.ERROR_MESSAGES["unknown_error"])
        
        if details:
            message += f"\n\nDetails: {details}"
        
        return message
    
    @staticmethod
    def handle_validation_error(validation_result: ValidationResult) -> Tuple[bool, str]:
        """
        Handle validation errors.
        
        Args:
            validation_result: ValidationResult object
            
        Returns:
            Tuple of (success, message)
        """
        if validation_result.is_valid:
            return True, "Validation passed"
        
        message = "Validation failed:\n"
        for error in validation_result.errors:
            message += f"  ✗ {error}\n"
        
        if validation_result.warnings:
            message += "\nWarnings:\n"
            for warning in validation_result.warnings:
                message += f"  ⚠ {warning}\n"
        
        return False, message
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> Dict:
        """
        Handle exceptions and return error information.
        
        Args:
            exception: Exception object
            context: Context where error occurred
            
        Returns:
            Error information dictionary
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        logger.error(f"Exception in {context}: {error_type}: {error_message}")
        
        return {
            "success": False,
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "user_message": ErrorHandler.get_user_friendly_message("unknown_error", error_message)
        }


class DataConsistencyValidator:
    """Validates data consistency across services."""
    
    @staticmethod
    def validate_trip_consistency(trip_plan: Dict) -> ValidationResult:
        """
        Validate trip plan data consistency.
        
        Args:
            trip_plan: Trip plan dictionary
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check if all required components are present
        required_fields = ["destination", "start_date", "end_date", "budget"]
        for field in required_fields:
            if field not in trip_plan:
                errors.append(f"Missing required field: {field}")
        
        # Check date consistency
        if "start_date" in trip_plan and "end_date" in trip_plan:
            try:
                start = datetime.strptime(trip_plan["start_date"], "%Y-%m-%d")
                end = datetime.strptime(trip_plan["end_date"], "%Y-%m-%d")
                
                if start >= end:
                    errors.append("Start date must be before end date")
            except ValueError:
                errors.append("Invalid date format in trip plan")
        
        # Check budget consistency
        if "budget" in trip_plan and "budget_breakdown" in trip_plan:
            total_breakdown = trip_plan["budget_breakdown"].get("total", 0)
            if total_breakdown > trip_plan["budget"] * 1.1:  # Allow 10% overage
                warnings.append(f"Budget breakdown ({total_breakdown}) significantly exceeds allocated budget ({trip_plan['budget']})")
        
        # Check calendar events consistency
        if "calendar_events" in trip_plan and trip_plan["calendar_events"]:
            for event in trip_plan["calendar_events"]:
                if "start_time" not in event or "end_time" not in event:
                    errors.append("Calendar event missing start_time or end_time")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_budget_consistency(flights: Dict, hotels: Dict, activities: Dict, 
                                   total_budget: float) -> ValidationResult:
        """
        Validate budget consistency across components.
        
        Args:
            flights: Flight costs
            hotels: Hotel costs
            activities: Activity costs
            total_budget: Total allocated budget
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        total_cost = 0
        
        if flights and "total_cost" in flights:
            total_cost += flights["total_cost"]
        
        if hotels and "total_cost" in hotels:
            total_cost += hotels["total_cost"]
        
        if activities and "total_cost" in activities:
            total_cost += activities["total_cost"]
        
        if total_cost > total_budget:
            overage = total_cost - total_budget
            warnings.append(f"Total cost ({total_cost}) exceeds budget by {overage}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
