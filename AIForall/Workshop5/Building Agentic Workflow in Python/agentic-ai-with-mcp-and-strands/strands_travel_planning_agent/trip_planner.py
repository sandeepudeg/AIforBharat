#!/usr/bin/env python3
"""
Comprehensive Trip Planner - End-to-End Trip Planning Orchestration

Coordinates all agents to create complete trip plans with flights, hotels, itineraries, and budgets.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

from calendar_service import CalendarService
from memory_service import MemoryService, TripRecord
from alerts_service import AlertsService

logger = logging.getLogger(__name__)


@dataclass
class TripPlan:
    """Represents a complete trip plan."""
    source: str  # Departure city
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget: float
    currency: str
    flights: Dict = None
    hotels: Dict = None
    itinerary: Dict = None
    budget_breakdown: Dict = None
    weather: Dict = None
    local_transport: Dict = None
    visa_requirements: Dict = None
    language_guide: Dict = None
    calendar_events: List = None
    alerts: List = None
    created_at: str = None
    
    def to_dict(self) -> Dict:
        """Convert trip plan to dictionary."""
        return {
            "source": self.source,
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "travelers": self.travelers,
            "budget": self.budget,
            "currency": self.currency,
            "flights": self.flights,
            "hotels": self.hotels,
            "itinerary": self.itinerary,
            "budget_breakdown": self.budget_breakdown,
            "weather": self.weather,
            "local_transport": self.local_transport,
            "visa_requirements": self.visa_requirements,
            "language_guide": self.language_guide,
            "calendar_events": self.calendar_events,
            "alerts": self.alerts,
            "created_at": self.created_at
        }


class TripPlanner:
    """Orchestrates comprehensive trip planning."""
    
    def __init__(self):
        """Initialize trip planner."""
        self.calendar_service = CalendarService()
        self.memory_service = MemoryService()
        self.alerts_service = AlertsService()
        self.trip_plans: Dict[str, TripPlan] = {}
        self._plan_counter = 0
        logger.info("Trip Planner initialized")
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID."""
        self._plan_counter += 1
        return f"plan_{self._plan_counter}_{datetime.now().timestamp()}"
    
    def create_trip_plan(self, source: str, destination: str, start_date: str, end_date: str,
                        travelers: int, budget: float, currency: str = "USD",
                        user_id: Optional[str] = None) -> TripPlan:
        """
        Create a comprehensive trip plan.
        
        Args:
            source: Source/departure city
            destination: Destination city/country
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            travelers: Number of travelers
            budget: Total budget
            currency: Currency code
            user_id: Optional user ID for preference tracking
            
        Returns:
            Created TripPlan
        """
        logger.info(f"Creating trip plan from {source} to {destination} ({start_date} to {end_date})")
        
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
        
        plan_id = self._generate_plan_id()
        self.trip_plans[plan_id] = plan
        
        # Store in memory if user_id provided
        if user_id:
            trip_record = TripRecord(
                trip_id=plan_id,
                user_id=user_id,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                rating=0,
                notes=""
            )
            self.memory_service.record_trip(trip_record)
        
        return plan
    
    def add_flights_to_plan(self, plan: TripPlan, flights: Dict) -> TripPlan:
        """
        Add flight information to trip plan.
        
        Args:
            plan: Trip plan to update
            flights: Flight information
                - outbound: Outbound flight details
                - return: Return flight details
                - total_cost: Total flight cost
                - currency: Currency
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding flights to plan for {plan.destination}")
        
        plan.flights = flights
        
        # Add to calendar if flight info available
        if flights.get("outbound"):
            self.calendar_service.add_flight_event(flights["outbound"])
        if flights.get("return"):
            self.calendar_service.add_flight_event(flights["return"])
        
        # Set up flight monitoring for alerts
        if flights.get("outbound"):
            outbound = flights["outbound"]
            self.alerts_service.add_flight_monitor(
                flight_id=outbound.get("flight_number", "unknown"),
                flight_number=outbound.get("flight_number", "unknown"),
                scheduled_departure=datetime.fromisoformat(outbound.get("departure_time", datetime.now().isoformat())),
                scheduled_arrival=datetime.fromisoformat(outbound.get("arrival_time", datetime.now().isoformat())),
                airline=outbound.get("airline", "Unknown")
            )
        
        return plan
    
    def add_hotels_to_plan(self, plan: TripPlan, hotels: Dict) -> TripPlan:
        """
        Add hotel information to trip plan.
        
        Args:
            plan: Trip plan to update
            hotels: Hotel information
                - name: Hotel name
                - check_in_date: Check-in date
                - check_out_date: Check-out date
                - address: Hotel address
                - total_cost: Total hotel cost
                - currency: Currency
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding hotels to plan for {plan.destination}")
        
        plan.hotels = hotels
        
        # Add to calendar if dates are provided
        if hotels and hotels.get("check_in_date") and hotels.get("check_out_date"):
            self.calendar_service.add_hotel_event(hotels)
        
        # Set up price monitoring for alerts
        if hotels.get("name"):
            self.alerts_service.add_price_monitor(
                item_id=f"hotel_{hotels.get('name', 'unknown')}",
                item_type="hotel",
                price=hotels.get("total_cost", 0),
                currency=plan.currency
            )
        
        return plan
    
    def add_itinerary_to_plan(self, plan: TripPlan, itinerary: Dict) -> TripPlan:
        """
        Add itinerary to trip plan.
        
        Args:
            plan: Trip plan to update
            itinerary: Day-by-day itinerary
                - days: List of day plans
                - total_activities: Total activities
                - estimated_cost: Estimated activity cost
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding itinerary to plan for {plan.destination}")
        
        plan.itinerary = itinerary
        
        # Add activities to calendar
        if itinerary.get("days"):
            for day in itinerary["days"]:
                if day.get("activities"):
                    for activity in day["activities"]:
                        self.calendar_service.add_activity_event({
                            "name": activity.get("name", "Activity"),
                            "start_time": activity.get("start_time", datetime.now().isoformat()),
                            "end_time": activity.get("end_time", (datetime.now() + timedelta(hours=2)).isoformat()),
                            "location": activity.get("location", plan.destination),
                            "description": activity.get("description", "")
                        })
        
        return plan
    
    def add_budget_to_plan(self, plan: TripPlan, budget_breakdown: Dict) -> TripPlan:
        """
        Add budget breakdown to trip plan.
        
        Args:
            plan: Trip plan to update
            budget_breakdown: Budget breakdown
                - flights: Flight costs
                - hotels: Hotel costs
                - activities: Activity costs
                - food: Food costs
                - transport: Transport costs
                - total: Total estimated cost
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding budget to plan for {plan.destination}")
        
        plan.budget_breakdown = budget_breakdown
        
        # Check if over budget
        total_cost = budget_breakdown.get("total", 0)
        if total_cost > plan.budget:
            logger.warning(f"Plan exceeds budget: {total_cost} > {plan.budget}")
        
        return plan
    
    def add_weather_to_plan(self, plan: TripPlan, weather: Dict) -> TripPlan:
        """
        Add weather information to trip plan.
        
        Args:
            plan: Trip plan to update
            weather: Weather information
                - forecast: Daily forecast
                - average_temp: Average temperature
                - conditions: Weather conditions
                - packing_tips: Packing recommendations
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding weather to plan for {plan.destination}")
        
        plan.weather = weather
        
        # Set up weather monitoring for alerts
        if weather.get("average_temp"):
            self.alerts_service.add_weather_monitor(
                destination=plan.destination,
                temp=weather.get("average_temp", 20),
                condition=weather.get("conditions", "Unknown"),
                forecast_date=datetime.fromisoformat(plan.start_date)
            )
        
        return plan
    
    def add_local_transport_to_plan(self, plan: TripPlan, transport: Dict) -> TripPlan:
        """
        Add local transport information to plan.
        
        Args:
            plan: Trip plan to update
            transport: Transport information
                - airport_transfer: Airport to hotel transfer
                - public_transit: Public transit options
                - rental_car: Rental car info
                - recommendations: Transport recommendations
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding local transport to plan for {plan.destination}")
        
        plan.local_transport = transport
        
        return plan
    
    def add_visa_requirements_to_plan(self, plan: TripPlan, visa_info: Dict) -> TripPlan:
        """
        Add visa requirements to plan.
        
        Args:
            plan: Trip plan to update
            visa_info: Visa information
                - required: Whether visa is required
                - processing_time: Processing time
                - documents: Required documents
                - cost: Visa cost
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding visa requirements to plan for {plan.destination}")
        
        plan.visa_requirements = visa_info
        
        # Create booking reminder if visa required
        if visa_info.get("required"):
            processing_days = int(visa_info.get("processing_time", "14").split()[0])
            deadline = datetime.fromisoformat(plan.start_date) - timedelta(days=processing_days)
            
            self.alerts_service.create_booking_reminder(
                item_type="visa",
                item_name=f"Visa for {plan.destination}",
                booking_deadline=deadline
            )
        
        return plan
    
    def add_language_guide_to_plan(self, plan: TripPlan, language_guide: Dict) -> TripPlan:
        """
        Add language guide to plan.
        
        Args:
            plan: Trip plan to update
            language_guide: Language guide
                - language: Local language
                - common_phrases: Common phrases
                - emergency_phrases: Emergency phrases
                - cultural_tips: Cultural tips
                
        Returns:
            Updated TripPlan
        """
        logger.info(f"Adding language guide to plan for {plan.destination}")
        
        plan.language_guide = language_guide
        
        return plan
    
    def finalize_plan(self, plan: TripPlan) -> Dict:
        """
        Finalize trip plan and generate summary.
        
        Args:
            plan: Trip plan to finalize
            
        Returns:
            Trip plan summary with all details
        """
        logger.info(f"Finalizing trip plan for {plan.destination}")
        
        # Generate calendar export
        calendar_export = self.calendar_service.export_to_json()
        plan.calendar_events = calendar_export.get("calendar", {}).get("events", [])
        
        # Get alerts summary
        alerts_summary = self.alerts_service.get_summary()
        plan.alerts = alerts_summary
        
        # Generate comprehensive summary
        summary = {
            "trip_plan": plan.to_dict(),
            "calendar": calendar_export,
            "alerts": alerts_summary,
            "booking_links": self._generate_booking_links(plan),
            "checklist": self._generate_checklist(plan),
            "summary_text": self._generate_summary_text(plan)
        }
        
        return summary
    
    def _generate_booking_links(self, plan: TripPlan) -> Dict:
        """Generate booking links for trip components."""
        links = {}
        
        if plan.flights:
            links["flights"] = {
                "provider": "Skyscanner",
                "url": f"https://www.skyscanner.com/transport/flights/{plan.destination}/"
            }
        
        if plan.hotels:
            links["hotels"] = {
                "provider": "Booking.com",
                "url": f"https://www.booking.com/searchresults.html?ss={plan.destination}"
            }
        
        if plan.itinerary:
            links["activities"] = {
                "provider": "Viator",
                "url": f"https://www.viator.com/tours/{plan.destination}"
            }
        
        return links
    
    def _generate_checklist(self, plan: TripPlan) -> List[str]:
        """Generate pre-trip checklist."""
        checklist = [
            "✓ Check passport validity (6+ months)",
            "✓ Book flights",
            "✓ Book accommodations",
            "✓ Purchase travel insurance",
            "✓ Notify bank of travel dates",
            "✓ Check visa requirements",
            "✓ Download offline maps",
            "✓ Make restaurant reservations",
            "✓ Pack luggage",
            "✓ Arrange airport transportation"
        ]
        
        if plan.visa_requirements and plan.visa_requirements.get("required"):
            checklist.insert(2, "✓ Apply for visa")
        
        return checklist
    
    def _generate_summary_text(self, plan: TripPlan) -> str:
        """Generate human-readable trip summary."""
        start = datetime.fromisoformat(plan.start_date)
        end = datetime.fromisoformat(plan.end_date)
        duration = (end - start).days
        
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║                      TRIP SUMMARY                              ║
╚════════════════════════════════════════════════════════════════╝

BASIC INFORMATION
─────────────────
Source:        {plan.source}
Destination:   {plan.destination}
Duration:      {duration} days ({plan.start_date} to {plan.end_date})
Travelers:     {plan.travelers}
Budget:        {plan.budget} {plan.currency}
Created:       {plan.created_at}

FLIGHTS
───────
{self._format_flights(plan.flights) if plan.flights else "Not yet booked"}

ACCOMMODATIONS
──────────────
{self._format_hotels(plan.hotels) if plan.hotels else "Not yet booked"}

ITINERARY
─────────
{self._format_itinerary(plan.itinerary) if plan.itinerary else "Not yet planned"}

BUDGET BREAKDOWN
────────────────
{self._format_budget(plan.budget_breakdown) if plan.budget_breakdown else "Not yet calculated"}

WEATHER FORECAST
────────────────
{self._format_weather(plan.weather) if plan.weather else "Not yet retrieved"}

LOCAL TRANSPORT
───────────────
{self._format_local_transport(plan.local_transport) if plan.local_transport else "Not yet planned"}

VISA REQUIREMENTS
─────────────────
{self._format_visa(plan.visa_requirements) if plan.visa_requirements else "Not yet checked"}

LANGUAGE GUIDE
──────────────
{self._format_language(plan.language_guide) if plan.language_guide else "Not yet provided"}

IMPORTANT NOTES
───────────────
{self._format_important_notes(plan)}

═══════════════════════════════════════════════════════════════════
"""
        return summary
    
    def _format_flights(self, flights: Dict) -> str:
        """Format flights for summary."""
        if not flights:
            return "No flights booked"
        
        text = ""
        if flights.get("outbound"):
            outbound = flights["outbound"]
            text += f"Outbound Flight:\n"
            text += f"  Airline:       {outbound.get('airline', 'N/A')}\n"
            text += f"  Flight Number: {outbound.get('flight_number', 'N/A')}\n"
            text += f"  Route:         {outbound.get('origin', 'N/A')} → {outbound.get('destination', 'N/A')}\n"
            text += f"  Departure:     {outbound.get('departure_time', 'N/A')}\n"
            text += f"  Arrival:       {outbound.get('arrival_time', 'N/A')}\n"
            text += f"  Duration:      {outbound.get('duration_minutes', 'N/A')} minutes\n"
            text += f"  Stops:         {outbound.get('stops', 0)}\n"
            text += f"  Price:         ${outbound.get('price', 'N/A')}\n"
            text += f"  Rating:        {outbound.get('rating', 'N/A')}⭐\n\n"
        
        if flights.get("return"):
            return_flight = flights["return"]
            text += f"Return Flight:\n"
            text += f"  Airline:       {return_flight.get('airline', 'N/A')}\n"
            text += f"  Flight Number: {return_flight.get('flight_number', 'N/A')}\n"
            text += f"  Route:         {return_flight.get('origin', 'N/A')} → {return_flight.get('destination', 'N/A')}\n"
            text += f"  Departure:     {return_flight.get('departure_time', 'N/A')}\n"
            text += f"  Arrival:       {return_flight.get('arrival_time', 'N/A')}\n"
            text += f"  Duration:      {return_flight.get('duration_minutes', 'N/A')} minutes\n"
            text += f"  Stops:         {return_flight.get('stops', 0)}\n"
            text += f"  Price:         ${return_flight.get('price', 'N/A')}\n"
            text += f"  Rating:        {return_flight.get('rating', 'N/A')}⭐\n\n"
        
        if flights.get("total_cost"):
            text += f"Total Flight Cost: ${flights.get('total_cost')} {flights.get('currency', 'USD')}"
        
        return text
    
    def _format_hotels(self, hotels: Dict) -> str:
        """Format hotels for summary."""
        if not hotels:
            return "No hotels booked"
        
        if isinstance(hotels, list):
            # Multiple hotels
            text = ""
            for i, hotel in enumerate(hotels[:3], 1):
                text += f"Hotel {i}: {hotel.get('name', 'Hotel')}\n"
                text += f"  Address:       {hotel.get('address', 'N/A')}\n"
                text += f"  Price/Night:   ${hotel.get('price_per_night', 'N/A')}\n"
                text += f"  Rating:        {hotel.get('rating', 'N/A')}⭐\n"
                text += f"  Amenities:     {', '.join(hotel.get('amenities', []))}\n"
                text += f"  Check-in:      {hotel.get('check_in_time', 'N/A')}\n"
                text += f"  Check-out:     {hotel.get('check_out_time', 'N/A')}\n\n"
            if len(hotels) > 3:
                text += f"... and {len(hotels) - 3} more hotels available"
            return text
        else:
            # Single hotel
            text = f"Hotel: {hotels.get('name', 'Hotel')}\n"
            text += f"  Address:       {hotels.get('address', 'N/A')}\n"
            text += f"  Price/Night:   ${hotels.get('price_per_night', 'N/A')}\n"
            text += f"  Rating:        {hotels.get('rating', 'N/A')}⭐\n"
            text += f"  Amenities:     {', '.join(hotels.get('amenities', []))}\n"
            text += f"  Check-in:      {hotels.get('check_in_time', 'N/A')}\n"
            text += f"  Check-out:     {hotels.get('check_out_time', 'N/A')}\n"
            text += f"  Total Cost:    ${hotels.get('total_cost', 'N/A')} {hotels.get('currency', 'USD')}"
            return text
    
    def _format_itinerary(self, itinerary: Dict) -> str:
        """Format itinerary for summary."""
        if not itinerary:
            return "No itinerary planned"
        
        text = ""
        
        # Handle daily_itinerary format from ItineraryAgent
        if itinerary.get("daily_itinerary"):
            for day_plan in itinerary["daily_itinerary"][:7]:  # Show first 7 days
                text += f"Day {day_plan.get('day', 'N/A')} - {day_plan.get('day_of_week', 'N/A')} ({day_plan.get('date', 'N/A')})\n"
                
                morning = day_plan.get("morning", {})
                text += f"  Morning:   {morning.get('activity', 'N/A')} ({morning.get('time', 'N/A')})\n"
                
                afternoon = day_plan.get("afternoon", {})
                text += f"  Afternoon: {afternoon.get('activity', 'N/A')} ({afternoon.get('time', 'N/A')})\n"
                
                evening = day_plan.get("evening", {})
                text += f"  Evening:   {evening.get('activity', 'N/A')} ({evening.get('time', 'N/A')})\n"
                
                meals = day_plan.get("meals", {})
                text += f"  Meals:     {meals.get('breakfast', 'N/A')} | {meals.get('lunch', 'N/A')} | {meals.get('dinner', 'N/A')}\n"
                text += f"  Cost:      {meals.get('estimated_cost', 'N/A')}\n\n"
            
            if len(itinerary.get("daily_itinerary", [])) > 7:
                text += f"... and {len(itinerary['daily_itinerary']) - 7} more days"
        
        # Handle days format
        elif itinerary.get("days"):
            for i, day in enumerate(itinerary["days"], 1):
                text += f"Day {i}: {day.get('title', 'Day ' + str(i))}\n"
                if day.get("activities"):
                    for activity in day["activities"][:5]:
                        text += f"  - {activity.get('name', 'Activity')} ({activity.get('time', 'N/A')})\n"
                if len(day.get("activities", [])) > 5:
                    text += f"  ... and {len(day['activities']) - 5} more activities\n"
                text += "\n"
        
        return text if text else "No itinerary planned"
    
    def _format_budget(self, budget: Dict) -> str:
        """Format budget for summary."""
        if not budget:
            return "No budget calculated"
        
        text = ""
        
        # Show allocation if available
        if budget.get("allocation"):
            text += "Budget Allocation:\n"
            for category, amount in budget["allocation"].items():
                percentage = budget.get("allocation_percentages", {}).get(category, "0%")
                text += f"  {category.capitalize():15} ${amount:>10,.2f} ({percentage:>4})\n"
            text += "\n"
        
        # Show daily budget
        if budget.get("daily_budget"):
            text += f"Daily Budget:    ${budget['daily_budget']:,.2f}\n"
        
        # Show total budget
        if budget.get("total_budget"):
            text += f"Total Budget:    ${budget['total_budget']:,.2f}\n"
        
        # Show trip days
        if budget.get("trip_days"):
            text += f"Trip Days:       {budget['trip_days']}\n"
        
        # Show currency info
        if budget.get("home_currency"):
            text += f"Currency:        {budget['home_currency']}\n"
        
        # Show destination currency conversion if available
        if budget.get("destination_currency"):
            text += f"\nDestination Currency Conversion:\n"
            text += f"  {budget['destination_currency']} {budget.get('total_budget_destination', 'N/A')}\n"
            text += f"  Exchange Rate: {budget.get('exchange_rate', 'N/A')}"
        
        return text if text else "No budget calculated"
    
    def _format_weather(self, weather: Dict) -> str:
        """Format weather for summary."""
        if not weather:
            return "No weather data available"
        
        text = f"Average Temperature: {weather.get('average_temp', 'N/A')}°C\n"
        text += f"Conditions: {weather.get('conditions', 'N/A')}\n"
        text += f"Packing Tips: {weather.get('packing_tips', 'N/A')}"
        
        return text
    
    def _format_local_transport(self, transport: Dict) -> str:
        """Format local transport for summary."""
        if not transport:
            return "No transport information available"
        
        text = ""
        if transport.get("airport_transfer"):
            text += f"Airport Transfer: {transport['airport_transfer']}\n"
        if transport.get("public_transit"):
            text += f"Public Transit: {transport['public_transit']}\n"
        if transport.get("rental_car"):
            text += f"Rental Car: {transport['rental_car']}\n"
        if transport.get("recommendations"):
            text += f"Recommendations: {transport['recommendations']}"
        
        return text if text else "No transport information available"
    
    def _format_visa(self, visa: Dict) -> str:
        """Format visa requirements for summary."""
        if not visa:
            return "No visa information available"
        
        text = ""
        if visa.get("required"):
            text += f"Visa Required: Yes\n"
            text += f"Processing Time: {visa.get('processing_time', 'N/A')}\n"
            text += f"Cost: {visa.get('cost', 'N/A')}\n"
            if visa.get("documents"):
                text += f"Required Documents: {', '.join(visa['documents'])}"
        else:
            text = "Visa Required: No"
        
        return text
    
    def _format_language(self, language: Dict) -> str:
        """Format language guide for summary."""
        if not language:
            return "No language guide available"
        
        text = f"Local Language: {language.get('language', 'N/A')}\n"
        if language.get("common_phrases"):
            text += f"Common Phrases: {', '.join(language['common_phrases'][:5])}\n"
        if language.get("emergency_phrases"):
            text += f"Emergency Phrases: {', '.join(language['emergency_phrases'][:3])}\n"
        if language.get("cultural_tips"):
            text += f"Cultural Tips: {language['cultural_tips']}"
        
        return text
    
    def _format_important_notes(self, plan: TripPlan) -> str:
        """Format important notes for summary."""
        notes = []
        
        if plan.visa_requirements and plan.visa_requirements.get("required"):
            notes.append(f"Visa required - Processing time: {plan.visa_requirements.get('processing_time')}")
        
        if plan.weather and plan.weather.get("warnings"):
            notes.append(f"Weather warning: {plan.weather['warnings']}")
        
        if plan.budget_breakdown and plan.budget_breakdown.get("total", 0) > plan.budget:
            notes.append(f"Plan exceeds budget by {plan.budget_breakdown['total'] - plan.budget}")
        
        return "\n".join(notes) if notes else "No special notes"
    
    def modify_plan(self, plan: TripPlan, modifications: Dict) -> TripPlan:
        """
        Modify an existing trip plan.
        
        Args:
            plan: Trip plan to modify
            modifications: Dictionary of modifications
                - new_budget: Updated budget
                - new_dates: Updated dates
                - new_destination: Updated destination
                
        Returns:
            Modified TripPlan
        """
        logger.info(f"Modifying trip plan for {plan.destination}")
        
        if "new_budget" in modifications:
            plan.budget = modifications["new_budget"]
        
        if "new_dates" in modifications:
            plan.start_date = modifications["new_dates"].get("start_date", plan.start_date)
            plan.end_date = modifications["new_dates"].get("end_date", plan.end_date)
        
        if "new_destination" in modifications:
            plan.destination = modifications["new_destination"]
        
        # Clear calendar and regenerate
        self.calendar_service.clear_events()
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[TripPlan]:
        """Get a trip plan by ID."""
        return self.trip_plans.get(plan_id)
    
    def list_plans(self) -> List[TripPlan]:
        """List all trip plans."""
        return list(self.trip_plans.values())
    
    def export_plan(self, plan: TripPlan, format: str = "json") -> str:
        """
        Export trip plan in specified format.
        
        Args:
            plan: Trip plan to export
            format: Export format (json, text)
            
        Returns:
            Exported plan as string
        """
        if format == "json":
            return json.dumps(plan.to_dict(), indent=2, default=str)
        elif format == "text":
            return self._generate_summary_text(plan)
        else:
            raise ValueError(f"Unsupported format: {format}")
