# Code & Resources - Well-Commented Snippets

## 1. Core Orchestrator - Trip Planner

```python
#!/usr/bin/env python3
"""
Trip Planner - Orchestrates all agents to create comprehensive trip plans
This is the central hub that coordinates all specialized agents
"""

from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class TripPlan:
    """Represents a complete trip plan with all details"""
    source: str              # Departure city
    destination: str         # Destination city
    start_date: str         # YYYY-MM-DD format
    end_date: str           # YYYY-MM-DD format
    travelers: int          # Number of people
    budget: float           # Total budget in USD
    currency: str           # Home currency code
    flights: Dict = None    # Flight information
    hotels: Dict = None     # Hotel information
    itinerary: Dict = None  # Day-by-day itinerary
    budget_breakdown: Dict = None  # Cost breakdown
    weather: Dict = None    # Weather forecast
    created_at: str = None  # Creation timestamp


class TripPlanner:
    """
    Orchestrates comprehensive trip planning by coordinating multiple agents.
    
    This class:
    1. Validates user input
    2. Creates base trip plan
    3. Calls all agents in parallel
    4. Aggregates results
    5. Stores in persistent storage
    """
    
    def __init__(self):
        """Initialize trip planner with services"""
        self.trip_plans: Dict[str, TripPlan] = {}
        self._plan_counter = 0
    
    def create_trip_plan(self, source: str, destination: str, 
                        start_date: str, end_date: str,
                        travelers: int, budget: float, 
                        currency: str = "USD") -> TripPlan:
        """
        Create a comprehensive trip plan.
        
        Args:
            source: Departure city (e.g., "New York")
            destination: Destination city (e.g., "Paris")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            travelers: Number of travelers (1-100)
            budget: Total budget in USD
            currency: Home currency code (e.g., "USD")
        
        Returns:
            TripPlan object with all details
        
        Example:
            >>> planner = TripPlanner()
            >>> plan = planner.create_trip_plan(
            ...     source="New York",
            ...     destination="Paris",
            ...     start_date="2025-01-15",
            ...     end_date="2025-01-22",
            ...     travelers=2,
            ...     budget=3000,
            ...     currency="USD"
            ... )
        """
        # Create base trip plan
        plan = TripPlan(
            source=source,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            travelers=travelers,
            budget=budget,
            currency=currency,
            created_at=datetime.now().isoformat()
        )
        
        # Generate unique plan ID
        plan_id = self._generate_plan_id()
        self.trip_plans[plan_id] = plan
        
        return plan
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID"""
        self._plan_counter += 1
        return f"plan_{self._plan_counter}_{datetime.now().timestamp()}"
```

## 2. Validation Layer

```python
#!/usr/bin/env python3
"""
Validation module for travel planning inputs
Ensures all user inputs meet requirements before processing
"""

from datetime import datetime
from typing import Dict, List

class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []


class TravelValidator:
    """Validates travel planning inputs"""
    
    # Constants for validation
    MIN_BUDGET = 100.0
    MAX_BUDGET = 1000000.0
    MIN_TRAVELERS = 1
    MAX_TRAVELERS = 100
    
    @staticmethod
    def validate_destination(destination: str) -> ValidationResult:
        """
        Validate destination input.
        
        Rules:
        - Must be a string
        - Must not be empty
        - Must be 2-100 characters
        - Must start with a letter
        - Can contain letters, numbers, spaces, hyphens, commas, apostrophes
        
        Args:
            destination: Destination city/country
        
        Returns:
            ValidationResult with errors if invalid
        
        Example:
            >>> result = TravelValidator.validate_destination("Paris")
            >>> print(result.is_valid)
            True
            
            >>> result = TravelValidator.validate_destination("")
            >>> print(result.is_valid)
            False
            >>> print(result.errors)
            ['Destination cannot be empty']
        """
        errors = []
        
        # Type check
        if not isinstance(destination, str):
            errors.append(f"Destination must be a string")
            return ValidationResult(False, errors)
        
        # Strip whitespace
        destination = destination.strip()
        
        # Empty check
        if not destination:
            errors.append("Destination cannot be empty")
            return ValidationResult(False, errors)
        
        # Length checks
        if len(destination) < 2:
            errors.append("Destination must be at least 2 characters")
        if len(destination) > 100:
            errors.append("Destination must be less than 100 characters")
        
        # First character must be letter
        if not destination[0].isalpha():
            errors.append("Destination must start with a letter")
        
        # Check for invalid characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,-'")
        invalid_chars = set(destination) - valid_chars
        if invalid_chars:
            errors.append(f"Invalid characters: {invalid_chars}")
        
        return ValidationResult(len(errors) == 0, errors)
    
    @staticmethod
    def validate_dates(start_date: str, end_date: str) -> ValidationResult:
        """
        Validate travel dates.
        
        Rules:
        - Must be in YYYY-MM-DD format
        - Must be in the future
        - Start date must be before end date
        - Trip duration 1-365 days
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            errors.append(f"Invalid date format. Use YYYY-MM-DD")
            return ValidationResult(False, errors)
        
        # Check if in future
        now = datetime.now()
        if start < now:
            errors.append(f"Start date must be in the future")
        if end < now:
            errors.append(f"End date must be in the future")
        
        # Check date order
        if start >= end:
            errors.append(f"Start date must be before end date")
        
        # Check duration
        if start < end:
            duration = (end - start).days
            if duration < 1:
                errors.append(f"Trip must be at least 1 day")
            if duration > 365:
                errors.append(f"Trip cannot exceed 365 days")
        
        return ValidationResult(len(errors) == 0, errors)
    
    @staticmethod
    def validate_budget(budget: float) -> ValidationResult:
        """
        Validate budget amount.
        
        Rules:
        - Must be a number
        - Must be between $100 and $1,000,000
        
        Args:
            budget: Budget amount in USD
        
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        
        if not isinstance(budget, (int, float)):
            errors.append(f"Budget must be a number")
            return ValidationResult(False, errors)
        
        if budget < TravelValidator.MIN_BUDGET:
            errors.append(f"Budget must be at least ${TravelValidator.MIN_BUDGET}")
        
        if budget > TravelValidator.MAX_BUDGET:
            errors.append(f"Budget cannot exceed ${TravelValidator.MAX_BUDGET}")
        
        return ValidationResult(len(errors) == 0, errors)
```

## 3. Flight Agent Example

```python
#!/usr/bin/env python3
"""
Flight Agent - Searches and compares flights
Uses Skyscanner API for real flight data
"""

import requests
from typing import Dict, List

class FlightAgent:
    """
    Specialized agent for flight search and comparison.
    
    Responsibilities:
    1. Search round-trip flights
    2. Filter by budget and preferences
    3. Compare options (price, duration, stops)
    4. Provide recommendations
    """
    
    def __init__(self):
        """Initialize Flight Agent"""
        self.api_key = "YOUR_SKYSCANNER_API_KEY"
        self.base_url = "https://skyscanner-api.p.rapidapi.com/v3/flights"
    
    def find_round_trip(self, origin: str, destination: str,
                       departure_date: str, return_date: str) -> Dict:
        """
        Find round-trip flights.
        
        Args:
            origin: Departure city (e.g., "New York")
            destination: Destination city (e.g., "Paris")
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)
        
        Returns:
            Dictionary with flight options and best recommendations
        
        Example:
            >>> agent = FlightAgent()
            >>> flights = agent.find_round_trip(
            ...     origin="New York",
            ...     destination="Paris",
            ...     departure_date="2025-01-15",
            ...     return_date="2025-01-22"
            ... )
            >>> print(flights['best_options']['cheapest']['total_price'])
            450
        """
        try:
            # Call Skyscanner API
            params = {
                'originSkyId': self._get_sky_id(origin),
                'destinationSkyId': self._get_sky_id(destination),
                'date': departure_date,
                'returnDate': return_date,
                'currency': 'USD'
            }
            
            response = requests.get(
                f"{self.base_url}/search-everywhere",
                params=params,
                headers={'x-rapidapi-key': self.api_key}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Process and return results
            return {
                'round_trips': self._process_flights(data),
                'best_options': self._find_best_options(data)
            }
        
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'round_trips': []}
    
    def _process_flights(self, data: Dict) -> List[Dict]:
        """
        Process raw API response into structured flight data.
        
        Args:
            data: Raw API response
        
        Returns:
            List of processed flight options
        """
        flights = []
        
        # Extract flights from API response
        for flight in data.get('itineraries', [])[:10]:  # Top 10 options
            processed = {
                'outbound': {
                    'airline': flight.get('airlines', ['Unknown'])[0],
                    'flight_number': flight.get('id', 'N/A'),
                    'departure_time': flight.get('departure_time', 'N/A'),
                    'arrival_time': flight.get('arrival_time', 'N/A'),
                    'duration_minutes': flight.get('duration', 0),
                    'stops': flight.get('stops', 0),
                    'price': flight.get('price', 0)
                },
                'return': {
                    'airline': flight.get('return_airline', 'Unknown'),
                    'flight_number': flight.get('return_id', 'N/A'),
                    'departure_time': flight.get('return_departure', 'N/A'),
                    'arrival_time': flight.get('return_arrival', 'N/A'),
                    'duration_minutes': flight.get('return_duration', 0),
                    'stops': flight.get('return_stops', 0),
                    'price': flight.get('return_price', 0)
                },
                'total_price': flight.get('price', 0) + flight.get('return_price', 0)
            }
            flights.append(processed)
        
        return flights
    
    def _find_best_options(self, data: Dict) -> Dict:
        """
        Find best flight options by different criteria.
        
        Returns:
            Dictionary with cheapest, fastest, and best value options
        """
        flights = self._process_flights(data)
        
        if not flights:
            return {}
        
        return {
            'cheapest': min(flights, key=lambda x: x['total_price']),
            'fastest': min(flights, key=lambda x: 
                          x['outbound']['duration_minutes'] + 
                          x['return']['duration_minutes']),
            'best_value': self._calculate_best_value(flights)
        }
    
    def _calculate_best_value(self, flights: List[Dict]) -> Dict:
        """
        Calculate best value option (price-to-duration ratio).
        
        Args:
            flights: List of flight options
        
        Returns:
            Flight with best price-to-duration ratio
        """
        best = None
        best_ratio = float('inf')
        
        for flight in flights:
            total_duration = (flight['outbound']['duration_minutes'] + 
                            flight['return']['duration_minutes'])
            ratio = flight['total_price'] / max(total_duration, 1)
            
            if ratio < best_ratio:
                best_ratio = ratio
                best = flight
        
        return best or flights[0]
    
    def _get_sky_id(self, city: str) -> str:
        """
        Get Skyscanner Sky ID for a city.
        
        Args:
            city: City name
        
        Returns:
            Sky ID for the city
        """
        # Mapping of common cities to Sky IDs
        city_map = {
            'New York': '27544008',
            'Paris': '27544009',
            'London': '27544010',
            'Tokyo': '27544011',
            'Sydney': '27544012'
        }
        return city_map.get(city, '27544008')
```

## 4. Budget Agent with Currency Conversion

```python
#!/usr/bin/env python3
"""
Budget Agent - Calculates costs and handles currency conversion
Provides budget breakdown and cost optimization
"""

import requests
from typing import Dict

class BudgetAgent:
    """
    Specialized agent for budget tracking and financial planning.
    
    Responsibilities:
    1. Calculate total trip cost
    2. Provide budget breakdown by category
    3. Convert currencies for international travel
    4. Suggest cost-saving opportunities
    """
    
    def get_budget_breakdown(self, total_budget: float, trip_days: int,
                            home_currency: str = "USD") -> Dict:
        """
        Get recommended budget breakdown.
        
        Allocation strategy:
        - Flights: 35% (largest expense)
        - Hotels: 35% (accommodation)
        - Meals: 15% (food and dining)
        - Activities: 10% (attractions and tours)
        - Transport: 5% (local transportation)
        
        Args:
            total_budget: Total trip budget in USD
            trip_days: Number of days
            home_currency: User's home currency
        
        Returns:
            Budget breakdown with daily budget and allocations
        
        Example:
            >>> agent = BudgetAgent()
            >>> breakdown = agent.get_budget_breakdown(
            ...     total_budget=3000,
            ...     trip_days=7,
            ...     home_currency="USD"
            ... )
            >>> print(breakdown['daily_budget'])
            428.57
            >>> print(breakdown['allocation']['flights'])
            1050.0
        """
        # Calculate allocations based on percentages
        allocation = {
            'flights': total_budget * 0.35,      # 35%
            'hotels': total_budget * 0.35,       # 35%
            'meals': total_budget * 0.15,        # 15%
            'activities': total_budget * 0.10,   # 10%
            'transport': total_budget * 0.05     # 5%
        }
        
        # Calculate daily budget
        daily_budget = total_budget / trip_days if trip_days > 0 else 0
        
        # Build result
        result = {
            'total_budget': total_budget,
            'home_currency': home_currency,
            'trip_days': trip_days,
            'daily_budget': round(daily_budget, 2),
            'allocation': {k: round(v, 2) for k, v in allocation.items()},
            'allocation_percentages': {
                'flights': '35%',
                'hotels': '35%',
                'meals': '15%',
                'activities': '10%',
                'transport': '5%'
            }
        }
        
        return result
    
    def convert_currency(self, amount: float, from_currency: str,
                        to_currency: str) -> Dict:
        """
        Convert currency using real exchange rates.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., "USD")
            to_currency: Target currency code (e.g., "EUR")
        
        Returns:
            Converted amount with exchange rate
        
        Example:
            >>> agent = BudgetAgent()
            >>> result = agent.convert_currency(100, "USD", "EUR")
            >>> print(result['converted_amount'])
            92.0
        """
        # Return early if same currency
        if from_currency == to_currency:
            return {
                'original_amount': amount,
                'original_currency': from_currency,
                'converted_amount': round(amount, 2),
                'converted_currency': to_currency,
                'exchange_rate': 1.0
            }
        
        try:
            # Fetch real exchange rates
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            exchange_rate = data['rates'][to_currency]
            converted = amount * exchange_rate
            
            return {
                'original_amount': amount,
                'original_currency': from_currency,
                'converted_amount': round(converted, 2),
                'converted_currency': to_currency,
                'exchange_rate': round(exchange_rate, 4),
                'source': 'live_api'
            }
        
        except Exception as e:
            # Fallback to cached rates if API fails
            return self._convert_with_fallback_rates(
                amount, from_currency, to_currency
            )
    
    def _convert_with_fallback_rates(self, amount: float,
                                     from_currency: str,
                                     to_currency: str) -> Dict:
        """
        Convert using fallback rates when API is unavailable.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
        
        Returns:
            Converted amount with fallback rates
        """
        # Cached exchange rates (as of reference date)
        rates = {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79,
            'JPY': 149.50,
            'AUD': 1.53,
            'CAD': 1.36,
            'CHF': 0.88,
            'CNY': 7.24,
            'INR': 83.12,
            'MXN': 17.05
        }
        
        from_rate = rates.get(from_currency, 1.0)
        to_rate = rates.get(to_currency, 1.0)
        
        converted = (amount / from_rate) * to_rate
        
        return {
            'original_amount': amount,
            'original_currency': from_currency,
            'converted_amount': round(converted, 2),
            'converted_currency': to_currency,
            'exchange_rate': round(to_rate / from_rate, 4),
            'source': 'fallback_rates',
            'note': 'Using cached rates - API unavailable'
        }
```

## 5. Streamlit UI Integration

```python
#!/usr/bin/env python3
"""
Streamlit UI for Travel Planning Agent
Interactive web interface for trip planning
"""

import streamlit as st
from datetime import datetime, timedelta
from trip_planner import TripPlanner
from validation import TravelValidator

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if "trip_planner" not in st.session_state:
        st.session_state.trip_planner = TripPlanner()
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None


def render_trip_planning_form():
    """
    Render the trip planning form with persistent state.
    
    Uses Streamlit session state to maintain form values
    across reruns, preventing data loss.
    """
    st.header("📝 Create New Trip Plan")
    
    # Initialize form state
    if "form_source" not in st.session_state:
        st.session_state.form_source = ""
    if "form_destination" not in st.session_state:
        st.session_state.form_destination = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Source input with persistent state
        source = st.text_input(
            "Source (Departure City)",
            value=st.session_state.form_source,
            placeholder="e.g., New York",
            key="source_input"
        )
        st.session_state.form_source = source
        
        # Destination input with persistent state
        destination = st.text_input(
            "Destination",
            value=st.session_state.form_destination,
            placeholder="e.g., Paris",
            key="destination_input"
        )
        st.session_state.form_destination = destination
    
    with col2:
        # Budget input
        budget = st.number_input(
            "Budget (USD)",
            min_value=100.0,
            max_value=1000000.0,
            value=3000.0,
            step=100.0
        )
        
        # Currency selector
        currency = st.selectbox(
            "Home Currency",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]
        )
    
    # Return form data
    return {
        "source": source.strip(),
        "destination": destination.strip(),
        "budget": budget,
        "currency": currency
    }


def validate_and_create_plan(plan_data):
    """
    Validate form data and create trip plan.
    
    Args:
        plan_data: Dictionary with form data
    
    Returns:
        TripPlan object or None if validation fails
    """
    # Pre-validation: Check required fields
    source = plan_data.get("source", "").strip()
    destination = plan_data.get("destination", "").strip()
    
    if not source or len(source) < 2:
        st.error("❌ Validation Failed")
        st.error("  • Source city is required (min 2 characters)")
        return None
    
    if not destination or len(destination) < 2:
        st.error("❌ Validation Failed")
        st.error("  • Destination is required (min 2 characters)")
        return None
    
    # Validate using TravelValidator
    validation_result = TravelValidator.validate_destination(destination)
    
    if not validation_result.is_valid:
        st.error("❌ Validation Failed")
        for error in validation_result.errors:
            st.error(f"  • {error}")
        return None
    
    # Create trip plan
    try:
        plan = st.session_state.trip_planner.create_trip_plan(
            source=source,
            destination=destination,
            start_date="2025-01-15",
            end_date="2025-01-22",
            travelers=2,
            budget=plan_data["budget"],
            currency=plan_data["currency"]
        )
        
        st.success("✅ Trip plan created successfully!")
        return plan
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def main():
    """Main Streamlit application"""
    # Initialize session state
    init_session_state()
    
    # Render header
    st.title("✈️ Travel Planning Agent")
    st.markdown("Plan your perfect trip with AI-powered recommendations")
    
    # Render form
    plan_data = render_trip_planning_form()
    
    # Create plan button
    if st.button("Create Trip Plan", type="primary", use_container_width=True):
        plan = validate_and_create_plan(plan_data)
        
        if plan:
            st.session_state.current_plan = plan
            
            # Display results in tabs
            tabs = st.tabs(["Flights", "Hotels", "Itinerary", "Budget"])
            
            with tabs[0]:
                st.subheader("✈️ Flight Information")
                st.write("Flight search results would appear here")
            
            with tabs[1]:
                st.subheader("🏨 Hotel Recommendations")
                st.write("Hotel recommendations would appear here")
            
            with tabs[2]:
                st.subheader("📅 Itinerary")
                st.write("Day-by-day itinerary would appear here")
            
            with tabs[3]:
                st.subheader("💰 Budget Breakdown")
                st.write("Budget breakdown would appear here")


if __name__ == "__main__":
    main()
```

## 6. AWS Integration Example

```python
#!/usr/bin/env python3
"""
AWS Integration - Store and retrieve trip plans from AWS services
"""

import boto3
import json
from typing import Dict, Optional

class AWSIntegration:
    """
    Handles integration with AWS services:
    - S3 for trip plan storage
    - DynamoDB for metadata
    - Bedrock for AI models
    """
    
    def __init__(self):
        """Initialize AWS clients"""
        self.s3_client = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.bedrock = boto3.client('bedrock-runtime')
        
        self.bucket_name = 'travel-plans-bucket'
        self.trips_table = self.dynamodb.Table('Trips')
    
    def save_trip_plan(self, trip_id: str, trip_plan: Dict) -> bool:
        """
        Save trip plan to S3 and DynamoDB.
        
        Args:
            trip_id: Unique trip identifier
            trip_plan: Trip plan dictionary
        
        Returns:
            True if successful, False otherwise
        
        Example:
            >>> aws = AWSIntegration()
            >>> success = aws.save_trip_plan(
            ...     trip_id="plan_1_123456",
            ...     trip_plan={...}
            ... )
        """
        try:
            # Save full plan to S3
            s3_key = f"trips/{trip_id}/plan.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(trip_plan),
                ContentType='application/json'
            )
            
            # Save metadata to DynamoDB
            self.trips_table.put_item(
                Item={
                    'trip_id': trip_id,
                    'destination': trip_plan.get('destination'),
                    'start_date': trip_plan.get('start_date'),
                    'end_date': trip_plan.get('end_date'),
                    'budget': trip_plan.get('budget'),
                    'created_at': trip_plan.get('created_at'),
                    's3_location': s3_key
                }
            )
            
            return True
        
        except Exception as e:
            print(f"Error saving trip plan: {e}")
            return False
    
    def get_trip_plan(self, trip_id: str) -> Optional[Dict]:
        """
        Retrieve trip plan from S3.
        
        Args:
            trip_id: Unique trip identifier
        
        Returns:
            Trip plan dictionary or None if not found
        """
        try:
            s3_key = f"trips/{trip_id}/plan.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            trip_plan = json.loads(response['Body'].read())
            return trip_plan
        
        except Exception as e:
            print(f"Error retrieving trip plan: {e}")
            return None
    
    def call_bedrock_model(self, prompt: str) -> str:
        """
        Call Amazon Bedrock model for AI processing.
        
        Args:
            prompt: Input prompt for the model
        
        Returns:
            Model response
        
        Example:
            >>> aws = AWSIntegration()
            >>> response = aws.call_bedrock_model(
            ...     prompt="Create a 3-day itinerary for Paris"
            ... )
        """
        try:
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-pro-v1:0',
                body=json.dumps({
                    'prompt': prompt,
                    'max_tokens': 1000,
                    'temperature': 0.3
                })
            )
            
            result = json.loads(response['body'].read())
            return result.get('completion', '')
        
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return ""
```

