"""
Data models for the Travel Planning Agent.

Defines all data structures used throughout the travel planning system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Flight:
    """Represents a flight option."""
    flight_id: str
    airline: str
    origin: str  # Departure city
    destination: str  # Arrival city
    departure_time: str  # ISO8601
    arrival_time: str  # ISO8601
    duration_minutes: int
    stops: int
    price: float
    currency: str
    booking_url: str
    flight_number: str = ""
    seats_available: int = 0
    rating: float = 0.0


@dataclass
class Hotel:
    """Represents a hotel accommodation option."""
    hotel_id: str
    name: str
    location: str
    check_in: str  # YYYY-MM-DD
    check_out: str  # YYYY-MM-DD
    nights: int
    price_per_night: float
    total_price: float
    amenities: List[str]
    rating: float
    booking_url: str


@dataclass
class Activity:
    """Represents a single activity or attraction."""
    name: str
    activity_type: str  # attraction|restaurant|activity
    location: str
    time: str  # HH:MM
    duration_minutes: int
    cost: float
    description: str
    rating: float


@dataclass
class DayPlan:
    """Represents a day's itinerary."""
    day: int
    date: str  # YYYY-MM-DD
    activities: List[Activity] = field(default_factory=list)
    meals: List[str] = field(default_factory=list)
    travel_time: int = 0  # minutes
    estimated_cost: float = 0.0


@dataclass
class Budget:
    """Represents trip budget and spending."""
    total_budget: float
    home_currency: str  # ISO 4217
    destination_currency: str  # ISO 4217
    exchange_rate: float
    flights_budget: float
    hotels_budget: float
    activities_budget: float
    food_budget: float
    transport_budget: float
    actual_spending: Dict[str, float] = field(default_factory=lambda: {
        "flights": 0.0,
        "hotels": 0.0,
        "activities": 0.0,
        "food": 0.0,
        "transport": 0.0
    })
    remaining: float = 0.0
    home_currency_total: float = 0.0
    home_currency_remaining: float = 0.0


@dataclass
class UserPreferences:
    """Represents user travel preferences."""
    user_id: str
    age: int
    home_country: str
    home_currency: str  # ISO 4217
    preferred_climate: str  # tropical|temperate|cold|desert
    travel_style: str  # luxury|budget|adventure|cultural
    interests: List[str] = field(default_factory=list)
    budget_range: Dict[str, float] = field(default_factory=lambda: {"min": 0.0, "max": 10000.0})
    preferred_airlines: List[str] = field(default_factory=list)
    hotel_preferences: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    language_preference: str = "en"
    accessibility_needs: List[str] = field(default_factory=list)
    mobility_level: str = "full"  # full|limited|wheelchair
    preferred_local_transport: List[str] = field(default_factory=list)


@dataclass
class VisaRequirement:
    """Represents visa requirements for a destination."""
    origin_country: str
    destination_country: str
    visa_required: bool
    visa_type: str
    processing_time_days: int
    validity_days: int
    cost: float
    required_documents: List[str] = field(default_factory=list)
    application_url: str = ""
    notes: str = ""


@dataclass
class ActivityAgeRestriction:
    """Represents age restrictions for an activity."""
    activity_id: str
    activity_name: str
    minimum_age: int
    maximum_age: Optional[int]
    restrictions: str
    parental_consent_required: bool = False


@dataclass
class LocalTransportOption:
    """Represents a local transportation option."""
    transport_type: str  # taxi|public_transit|rental_car|ride_share|walking
    name: str
    estimated_cost: float
    estimated_time_minutes: int
    convenience_rating: float  # 1-5
    availability: str  # 24/7|daytime|scheduled
    booking_url: str = ""
    description: str = ""


@dataclass
class Trip:
    """Represents a complete trip plan."""
    trip_id: str
    user_id: str
    source: str  # Departure city
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    duration_days: int
    flights: List[Flight] = field(default_factory=list)
    hotels: List[Hotel] = field(default_factory=list)
    itinerary: List[DayPlan] = field(default_factory=list)
    budget: Optional[Budget] = None
    preferences: Optional[UserPreferences] = None
    local_transport_options: List[LocalTransportOption] = field(default_factory=list)
    visa_requirements: Optional[VisaRequirement] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "planning"  # planning|booked|completed
