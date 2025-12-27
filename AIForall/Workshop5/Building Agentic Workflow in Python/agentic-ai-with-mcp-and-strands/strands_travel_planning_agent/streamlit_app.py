#!/usr/bin/env python3
"""
Streamlit UI for Travel Planning Agent

Interactive web interface for trip planning with all specialized agents.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from trip_planner import TripPlanner
from validation import TravelValidator, ErrorHandler
from calendar_service import CalendarService
from memory_service import MemoryService
from alerts_service import AlertsService
from mock_data import (
    get_mock_flights, get_mock_hotels, get_mock_weather,
    get_mock_itinerary, get_mock_budget, get_mock_visa,
    get_mock_language, get_mock_local_transport
)

# Page configuration
st.set_page_config(
    page_title="Travel Planning Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if "trip_planner" not in st.session_state:
        st.session_state.trip_planner = TripPlanner()
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = "user_default"
    if "plans_history" not in st.session_state:
        st.session_state.plans_history = []


init_session_state()


def render_header():
    """Render application header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("✈️ Travel Planning Agent")
        st.markdown("Plan your perfect trip with AI-powered recommendations")
    with col2:
        st.markdown("### 🌍 Multi-Agent System")


def render_sidebar():
    """Render sidebar with navigation and settings."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # User ID
        user_id = st.text_input(
            "User ID",
            value=st.session_state.user_id,
            help="Your unique identifier for saving preferences"
        )
        st.session_state.user_id = user_id
        
        st.divider()
        
        # Navigation
        st.header("📋 Navigation")
        page = st.radio(
            "Select Page",
            ["Plan Trip", "View Plans", "Preferences", "Alerts", "Help"]
        )
        
        return page


def render_trip_planning_form():
    """Render trip planning form."""
    st.header("📝 Create New Trip Plan")
    
    # Initialize session state for form fields if not present
    if "form_source" not in st.session_state:
        st.session_state.form_source = ""
    if "form_destination" not in st.session_state:
        st.session_state.form_destination = ""
    if "form_start_date" not in st.session_state:
        st.session_state.form_start_date = datetime.now() + timedelta(days=10)
    if "form_end_date" not in st.session_state:
        st.session_state.form_end_date = datetime.now() + timedelta(days=17)
    if "form_travelers" not in st.session_state:
        st.session_state.form_travelers = 1
    if "form_budget" not in st.session_state:
        st.session_state.form_budget = 3000.0
    if "form_currency" not in st.session_state:
        st.session_state.form_currency = "USD"
    
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.text_input(
            "Source (Departure City)",
            value=st.session_state.form_source,
            placeholder="e.g., New York, London, Tokyo",
            help="City or country you're traveling from",
            key="source_input"
        )
        st.session_state.form_source = source
        
        destination = st.text_input(
            "Destination",
            value=st.session_state.form_destination,
            placeholder="e.g., Paris, Tokyo, New York",
            help="City or country you want to visit",
            key="destination_input"
        )
        st.session_state.form_destination = destination
        
        start_date = st.date_input(
            "Start Date",
            value=st.session_state.form_start_date,
            min_value=datetime.now(),
            key="start_date_input"
        )
        st.session_state.form_start_date = start_date
        
        travelers = st.number_input(
            "Number of Travelers",
            min_value=1,
            max_value=100,
            value=st.session_state.form_travelers,
            help="How many people are traveling?",
            key="travelers_input"
        )
        st.session_state.form_travelers = int(travelers)
    
    with col2:
        budget = st.number_input(
            "Budget (USD)",
            min_value=100.0,
            max_value=1000000.0,
            value=st.session_state.form_budget,
            step=100.0,
            help="Total budget for the trip",
            key="budget_input"
        )
        st.session_state.form_budget = float(budget)
        
        end_date = st.date_input(
            "End Date",
            value=st.session_state.form_end_date,
            min_value=datetime.now(),
            key="end_date_input"
        )
        st.session_state.form_end_date = end_date
        
        currency = st.selectbox(
            "Home Currency",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "MXN"],
            index=["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "MXN"].index(st.session_state.form_currency),
            help="Your home currency for cost conversion",
            key="currency_input"
        )
        st.session_state.form_currency = currency
    
    return {
        "source": source.strip(),
        "destination": destination.strip(),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "travelers": int(travelers),
        "budget": float(budget),
        "currency": currency
    }


def validate_and_create_plan(plan_data):
    """Validate and create trip plan."""
    # Pre-validation: Check required fields are not empty
    source = plan_data.get("source", "").strip()
    destination = plan_data.get("destination", "").strip()
    
    if not source or len(source) < 2:
        st.error("❌ Validation Failed")
        st.error("  • Source city is required and must be at least 2 characters")
        st.error(f"    (Received: '{plan_data.get('source', '')}')")
        return None
    
    if not destination or len(destination) < 2:
        st.error("❌ Validation Failed")
        st.error("  • Destination is required and must be at least 2 characters")
        st.error(f"    (Received: '{plan_data.get('destination', '')}')")
        return None
    
    # Validate input
    validation_result = TravelValidator.validate_trip_plan(
        destination=destination,
        start_date=plan_data["start_date"],
        end_date=plan_data["end_date"],
        travelers=plan_data["travelers"],
        budget=plan_data["budget"],
        currency=plan_data["currency"]
    )
    
    if not validation_result.is_valid:
        st.error("❌ Validation Failed")
        for error in validation_result.errors:
            st.error(f"  • {error}")
        return None
    
    if validation_result.warnings:
        st.warning("⚠️ Warnings")
        for warning in validation_result.warnings:
            st.warning(f"  • {warning}")
    
    # Create plan
    try:
        plan = st.session_state.trip_planner.create_trip_plan(
            source=plan_data["source"],
            destination=plan_data["destination"],
            start_date=plan_data["start_date"],
            end_date=plan_data["end_date"],
            travelers=plan_data["travelers"],
            budget=plan_data["budget"],
            currency=plan_data["currency"],
            user_id=st.session_state.user_id
        )
        
        st.session_state.current_plan = plan
        st.session_state.plans_history.append(plan)
        
        st.success("✅ Trip plan created successfully!")
        return plan
    
    except Exception as e:
        error_info = ErrorHandler.handle_exception(e, "create_trip_plan")
        st.error(f"❌ Error: {error_info['user_message']}")
        return None


def gather_all_agent_data(plan):
    """Automatically gather data from all agents."""
    agents_data = {}
    
    # Flights
    try:
        from agents.flight_agent import FlightAgent
        flight_agent = FlightAgent()
        flights_result = flight_agent.find_round_trip(
            origin=plan.source,
            destination=plan.destination,
            departure_date=plan.start_date,
            return_date=plan.end_date
        )
        if flights_result.get("round_trips") and len(flights_result["round_trips"]) > 0:
            best_trip = flights_result["round_trips"][0]
            agents_data["flights"] = {
                "outbound": best_trip["outbound"],
                "return": best_trip["return"],
                "total_cost": best_trip["total_price"],
                "currency": plan.currency
            }
    except Exception as e:
        agents_data["flights_error"] = str(e)
    
    # Weather
    try:
        from agents.weather_agent import WeatherAgent
        weather_agent = WeatherAgent()
        weather_data = weather_agent.get_forecast(
            destination=plan.destination,
            start_date=plan.start_date,
            end_date=plan.end_date
        )
        agents_data["weather"] = weather_data
    except Exception as e:
        agents_data["weather_error"] = str(e)
    
    # Hotels
    try:
        from agents.hotel_agent import HotelAgent
        hotel_agent = HotelAgent()
        hotels = hotel_agent.get_recommendations(
            destination=plan.destination,
            budget=plan.budget / plan.travelers / ((datetime.fromisoformat(plan.end_date) - datetime.fromisoformat(plan.start_date)).days or 1)
        )
        agents_data["hotels"] = hotels
    except Exception as e:
        agents_data["hotels_error"] = str(e)
    
    # Itinerary (with weather-aware planning if weather data available)
    try:
        from agents.itinerary_agent import ItineraryAgent
        itinerary_agent = ItineraryAgent()
        
        # Pass weather data if available for weather-aware itinerary
        weather_data = agents_data.get("weather")
        itinerary = itinerary_agent.create_itinerary(
            destination=plan.destination,
            start_date=plan.start_date,
            end_date=plan.end_date,
            interests=["culture", "food", "nature"],
            weather_data=weather_data  # Pass weather data for weather-aware planning
        )
        agents_data["itinerary"] = itinerary
    except Exception as e:
        agents_data["itinerary_error"] = str(e)
    
    # Budget
    try:
        from agents.budget_agent import BudgetAgent
        budget_agent = BudgetAgent()
        budget_breakdown = budget_agent.get_budget_breakdown(
            total_budget=plan.budget,
            trip_days=(datetime.fromisoformat(plan.end_date) - datetime.fromisoformat(plan.start_date)).days + 1,
            home_currency=plan.currency
        )
        agents_data["budget"] = budget_breakdown
    except Exception as e:
        agents_data["budget_error"] = str(e)
    
    # Visa & Age Requirements
    try:
        from agents.visa_age_agent import VisaAgeAgent
        visa_agent = VisaAgeAgent()
        visa_data = visa_agent.check_visa_requirement(
            origin_country="USA",
            destination_country=plan.destination
        )
        visa_app_info = visa_agent.get_visa_application_info(plan.destination)
        agents_data["visa"] = {
            "requirement": visa_data,
            "application_info": visa_app_info
        }
    except Exception as e:
        agents_data["visa_error"] = str(e)
    
    # Language Guide
    try:
        from agents.language_agent import LanguageAgent
        language_agent = LanguageAgent()
        language_guide = language_agent.get_language_guide(plan.destination)
        common_phrases = language_agent.get_common_phrases(
            destination=plan.destination,
            language=language_guide.get("primary_language", "English")
        )
        agents_data["language"] = {
            "guide": language_guide,
            "common_phrases": common_phrases
        }
    except Exception as e:
        agents_data["language_error"] = str(e)
    
    return agents_data


def render_plan_trip_page():
    """Render trip planning page."""
    st.header("🗺️ Plan Your Trip")
    
    # Trip planning form
    plan_data = render_trip_planning_form()
    
    # Debug: Show form data
    with st.expander("Debug: Form Data", expanded=False):
        st.json(plan_data)
    
    if st.button("Create Trip Plan", type="primary", use_container_width=True):
        plan = validate_and_create_plan(plan_data)
        
        if plan:
            st.divider()
            
            # Display plan summary
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Source", plan_data.get("source", "N/A"))
            with col2:
                st.metric("Destination", plan.destination)
            with col3:
                st.metric("Duration", f"{(datetime.fromisoformat(plan.end_date) - datetime.fromisoformat(plan.start_date)).days} days")
            with col4:
                st.metric("Travelers", plan.travelers)
            with col5:
                st.metric("Budget", f"${plan.budget:,.0f}")
            
            st.divider()
            
            # Automatically gather all agent data
            st.subheader("🤖 Gathering Travel Information...")
            with st.spinner("Searching flights, weather, hotels, and creating itinerary..."):
                agents_data = gather_all_agent_data(plan)
            
            st.success("✅ Travel information gathered!")
            st.divider()
            
            # Display tabs with all information
            tabs = st.tabs(["Flights", "Hotels", "Itinerary", "Budget", "Weather", "Visa", "Language", "Suggestions"])
            
            with tabs[0]:
                st.subheader("✈️ Flight Information")
                if "flights" in agents_data:
                    flights = agents_data["flights"]
                    
                    # Display best options if available
                    if "best_options" in flights:
                        best_options = flights["best_options"]
                        
                        st.write("### 🎯 Best Flight Options")
                        
                        # Cheapest option
                        if best_options.get("cheapest"):
                            with st.expander("💰 **Cheapest Option** - Lowest Total Price", expanded=True):
                                cheapest = best_options["cheapest"]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Outbound Flight**")
                                    outbound = cheapest.get("outbound", {})
                                    st.write(f"• **Airline:** {outbound.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {outbound.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {outbound.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {outbound.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {outbound.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${outbound.get('price', 'N/A')}")
                                
                                with col2:
                                    st.write("**Return Flight**")
                                    return_flight = cheapest.get("return", {})
                                    st.write(f"• **Airline:** {return_flight.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {return_flight.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {return_flight.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {return_flight.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {return_flight.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${return_flight.get('price', 'N/A')}")
                                
                                st.metric("Total Cost", f"${cheapest.get('total_price', 0)}")
                        
                        # Fastest option
                        if best_options.get("fastest"):
                            with st.expander("⚡ **Fastest Option** - Shortest Travel Time"):
                                fastest = best_options["fastest"]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Outbound Flight**")
                                    outbound = fastest.get("outbound", {})
                                    st.write(f"• **Airline:** {outbound.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {outbound.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {outbound.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {outbound.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {outbound.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${outbound.get('price', 'N/A')}")
                                
                                with col2:
                                    st.write("**Return Flight**")
                                    return_flight = fastest.get("return", {})
                                    st.write(f"• **Airline:** {return_flight.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {return_flight.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {return_flight.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {return_flight.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {return_flight.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${return_flight.get('price', 'N/A')}")
                                
                                st.metric("Total Duration", f"{fastest.get('total_duration', 0)} minutes")
                        
                        # Best value option
                        if best_options.get("best_value"):
                            with st.expander("⭐ **Best Value** - Best Price-to-Duration Ratio"):
                                best_value = best_options["best_value"]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Outbound Flight**")
                                    outbound = best_value.get("outbound", {})
                                    st.write(f"• **Airline:** {outbound.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {outbound.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {outbound.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {outbound.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {outbound.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${outbound.get('price', 'N/A')}")
                                
                                with col2:
                                    st.write("**Return Flight**")
                                    return_flight = best_value.get("return", {})
                                    st.write(f"• **Airline:** {return_flight.get('airline', 'N/A')}")
                                    st.write(f"• **Flight:** {return_flight.get('flight_number', 'N/A')}")
                                    st.write(f"• **Departure:** {return_flight.get('departure_time', 'N/A')}")
                                    st.write(f"• **Arrival:** {return_flight.get('arrival_time', 'N/A')}")
                                    st.write(f"• **Duration:** {return_flight.get('duration_minutes', 'N/A')} min")
                                    st.write(f"• **Price:** ${return_flight.get('price', 'N/A')}")
                                
                                st.metric("Total Cost", f"${best_value.get('total_price', 0)}")
                    
                    else:
                        # Fallback for old format
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Outbound Flight")
                            outbound = flights.get("outbound", {})
                            st.write(f"**Airline:** {outbound.get('airline', 'N/A')}")
                            st.write(f"**Flight Number:** {outbound.get('flight_number', 'N/A')}")
                            st.write(f"**Route:** {outbound.get('origin', 'N/A')} → {outbound.get('destination', 'N/A')}")
                            st.write(f"**Departure:** {outbound.get('departure_time', 'N/A')}")
                            st.write(f"**Arrival:** {outbound.get('arrival_time', 'N/A')}")
                            st.write(f"**Duration:** {outbound.get('duration_minutes', 'N/A')} minutes")
                            st.write(f"**Price:** ${outbound.get('price', 'N/A')}")
                        
                        with col2:
                            st.subheader("Return Flight")
                            return_flight = flights.get("return", {})
                            st.write(f"**Airline:** {return_flight.get('airline', 'N/A')}")
                            st.write(f"**Flight Number:** {return_flight.get('flight_number', 'N/A')}")
                            st.write(f"**Route:** {return_flight.get('origin', 'N/A')} → {return_flight.get('destination', 'N/A')}")
                            st.write(f"**Departure:** {return_flight.get('departure_time', 'N/A')}")
                            st.write(f"**Arrival:** {return_flight.get('arrival_time', 'N/A')}")
                            st.write(f"**Duration:** {return_flight.get('duration_minutes', 'N/A')} minutes")
                            st.write(f"**Price:** ${return_flight.get('price', 'N/A')}")
                        
                        st.divider()
                        st.metric("Total Cost", f"${flights.get('total_cost', 0)} {flights.get('currency', 'USD')}")
                else:
                    st.warning(f"⚠️ Could not fetch flights: {agents_data.get('flights_error', 'Unknown error')}")
            
            with tabs[1]:
                st.subheader("🏨 Hotel Recommendations")
                if "hotels" in agents_data:
                    hotels = agents_data["hotels"]
                    for hotel in hotels[:3]:
                        with st.expander(f"{hotel.get('name')} - ${hotel.get('price_per_night')}/night"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Rating:** {hotel.get('rating', 'N/A')} ⭐")
                                st.write(f"**Address:** {hotel.get('address', 'N/A')}")
                                st.write(f"**Rooms Available:** {hotel.get('rooms_available', 'N/A')}")
                            with col2:
                                st.write(f"**Amenities:** {', '.join(hotel.get('amenities', []))}")
                                st.write(f"**Check-in:** {hotel.get('check_in_time', 'N/A')}")
                                st.write(f"**Check-out:** {hotel.get('check_out_time', 'N/A')}")
                else:
                    st.warning(f"⚠️ Could not fetch hotels: {agents_data.get('hotels_error', 'Unknown error')}")
            
            with tabs[2]:
                st.subheader("📅 Itinerary")
                if "itinerary" in agents_data:
                    itinerary = agents_data["itinerary"]
                    
                    # Show if weather-aware
                    if itinerary.get("weather_aware"):
                        st.info("🌤️ This itinerary is weather-aware and activities are adapted to forecasted conditions")
                    
                    for day_plan in itinerary.get("daily_itinerary", []):
                        # Build expander title with weather info if available
                        title = f"Day {day_plan.get('day')} - {day_plan.get('day_of_week')} ({day_plan.get('date')})"
                        if day_plan.get("weather"):
                            weather = day_plan["weather"]
                            title += f" | {weather.get('condition', 'N/A')} {weather.get('high_temp', 'N/A')}°C"
                        
                        with st.expander(title):
                            # Weather section if available
                            if day_plan.get("weather"):
                                weather = day_plan["weather"]
                                st.markdown("**🌤️ Weather Forecast**")
                                col_w1, col_w2, col_w3, col_w4 = st.columns(4)
                                with col_w1:
                                    st.metric("Condition", weather.get('condition', 'N/A'))
                                with col_w2:
                                    st.metric("High Temp", f"{weather.get('high_temp', 'N/A')}°C")
                                with col_w3:
                                    st.metric("Precipitation", f"{weather.get('precipitation_chance', 0):.0f}%")
                                with col_w4:
                                    st.metric("Humidity", f"{weather.get('humidity', 0):.0f}%")
                                st.divider()
                            
                            # Activities section
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**🌅 Morning**")
                                morning = day_plan.get('morning', {})
                                st.write(f"**{morning.get('activity', 'N/A')}**")
                                st.write(f"*{morning.get('time', 'N/A')}*")
                                if morning.get('reason'):
                                    st.caption(f"💡 {morning.get('reason')}")
                            with col2:
                                st.write("**☀️ Afternoon**")
                                afternoon = day_plan.get('afternoon', {})
                                st.write(f"**{afternoon.get('activity', 'N/A')}**")
                                st.write(f"*{afternoon.get('time', 'N/A')}*")
                                if afternoon.get('reason'):
                                    st.caption(f"💡 {afternoon.get('reason')}")
                            with col3:
                                st.write("**🌙 Evening**")
                                evening = day_plan.get('evening', {})
                                st.write(f"**{evening.get('activity', 'N/A')}**")
                                st.write(f"*{evening.get('time', 'N/A')}*")
                                if evening.get('reason'):
                                    st.caption(f"💡 {evening.get('reason')}")
                            
                            st.divider()
                            
                            # Meals section
                            st.markdown("**🍽️ Meals**")
                            meals = day_plan.get("meals", {})
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.write(f"**Breakfast:** {meals.get('breakfast', 'N/A')}")
                            with col_m2:
                                st.write(f"**Lunch:** {meals.get('lunch', 'N/A')}")
                            with col_m3:
                                st.write(f"**Dinner:** {meals.get('dinner', 'N/A')}")
                            
                            # Warnings section if available
                            if day_plan.get("warnings"):
                                st.divider()
                                st.markdown("**⚠️ Weather Warnings & Tips**")
                                for warning in day_plan.get("warnings", []):
                                    st.warning(warning)
                            
                            # Notes
                            if day_plan.get("notes"):
                                st.caption(f"📝 {day_plan.get('notes')}")
                else:
                    st.warning(f"⚠️ Could not generate itinerary: {agents_data.get('itinerary_error', 'Unknown error')}")
            
            with tabs[3]:
                st.subheader("💰 Budget Breakdown")
                if "budget" in agents_data:
                    budget = agents_data["budget"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Budget", f"${budget.get('total_budget', 0)}")
                        st.metric("Daily Budget", f"${budget.get('daily_budget', 0)}")
                    with col2:
                        st.metric("Trip Days", budget.get('trip_days', 0))
                    
                    st.divider()
                    st.write("**Budget Allocation:**")
                    allocation = budget.get("allocation", {})
                    for category, amount in allocation.items():
                        percentage = budget.get("allocation_percentages", {}).get(category, "0%")
                        st.write(f"• {category.capitalize()}: ${amount} ({percentage})")
                else:
                    st.warning(f"⚠️ Could not calculate budget: {agents_data.get('budget_error', 'Unknown error')}")
            
            with tabs[4]:
                st.subheader("🌤️ Weather Forecast")
                if "weather" in agents_data:
                    weather = agents_data["weather"]
                    for day_forecast in weather.get("daily_forecasts", [])[:3]:
                        with st.expander(f"{day_forecast.get('date')} - {day_forecast.get('day_of_week')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Condition:** {day_forecast.get('condition', 'N/A')}")
                                st.write(f"**High:** {day_forecast.get('high_temp', 'N/A')}°C")
                                st.write(f"**Low:** {day_forecast.get('low_temp', 'N/A')}°C")
                            with col2:
                                st.write(f"**Precipitation:** {day_forecast.get('precipitation_chance', 'N/A')}%")
                                st.write(f"**Wind:** {day_forecast.get('wind_speed', 'N/A')} km/h")
                                st.write(f"**Humidity:** {day_forecast.get('humidity', 'N/A')}%")
                            with col3:
                                st.write("**Packing Tips:**")
                                if day_forecast.get('precipitation_chance', 0) > 50:
                                    st.write("• Bring umbrella")
                                if day_forecast.get('high_temp', 0) > 25:
                                    st.write("• Light clothing")
                                if day_forecast.get('low_temp', 0) < 15:
                                    st.write("• Bring jacket")
                else:
                    st.warning(f"⚠️ Could not fetch weather: {agents_data.get('weather_error', 'Unknown error')}")
            
            with tabs[5]:
                st.subheader("📋 Visa & Travel Requirements")
                if "visa" in agents_data:
                    visa = agents_data["visa"]
                    requirement = visa.get("requirement", {})
                    app_info = visa.get("application_info", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Visa Requirement:**")
                        st.write(f"• **Required:** {'Yes' if requirement.get('visa_required') else 'No'}")
                        st.write(f"• **Type:** {requirement.get('visa_type', 'N/A')}")
                        if requirement.get('visa_free_days'):
                            st.write(f"• **Visa-Free Days:** {requirement.get('visa_free_days')}")
                        if requirement.get('processing_days'):
                            st.write(f"• **Processing Days:** {requirement.get('processing_days')}")
                    
                    with col2:
                        st.write("**Application Info:**")
                        st.write(f"• **Processing Time:** {app_info.get('processing_time', 'N/A')}")
                        st.write(f"• **Validity:** {app_info.get('validity', 'N/A')}")
                        st.write(f"• **Cost:** {app_info.get('cost', 'N/A')}")
                    
                    st.divider()
                    st.write("**Required Documents:**")
                    for doc in app_info.get('required_documents', []):
                        st.write(f"• {doc}")
                    
                    st.divider()
                    st.write(f"**Application Method:** {app_info.get('application_method', 'N/A')}")
                    st.write(f"**Official Website:** {app_info.get('website', 'N/A')}")
                else:
                    st.warning(f"⚠️ Could not fetch visa info: {agents_data.get('visa_error', 'Unknown error')}")
            
            with tabs[6]:
                st.subheader("🌍 Language Guide")
                if "language" in agents_data:
                    language = agents_data["language"]
                    guide = language.get("guide", {})
                    phrases = language.get("common_phrases", [])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Language Information:**")
                        st.write(f"• **Primary Language:** {guide.get('primary_language', 'N/A')}")
                        st.write(f"• **English Spoken:** {guide.get('english_spoken', 'N/A')}")
                    
                    with col2:
                        st.write("**Tips:**")
                        for tip in guide.get('tips', []):
                            st.write(f"• {tip}")
                    
                    st.divider()
                    st.write("**Common Phrases:**")
                    for phrase in phrases[:5]:
                        st.write(f"• **{phrase.get('english')}** → {phrase.get('local')} ({phrase.get('pronunciation')})")
                else:
                    st.warning(f"⚠️ Could not fetch language guide: {agents_data.get('language_error', 'Unknown error')}")
            
            with tabs[7]:
                st.subheader("💡 AI Suggestions & Recommendations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Flight Tips:**")
                    if "flights" in agents_data:
                        flights = agents_data["flights"]
                        st.write(f"✈️ Best option: {flights.get('outbound', {}).get('airline')} - ${flights.get('outbound', {}).get('price')}")
                        st.write("💡 Book early for better prices")
                        st.write("💡 Consider flexible dates for savings")
                    
                    st.write("**Hotel Tips:**")
                    if "hotels" in agents_data:
                        hotels = agents_data["hotels"]
                        if hotels:
                            st.write(f"🏨 Top rated: {hotels[0].get('name')} ({hotels[0].get('rating')}⭐)")
                            st.write("💡 Book 2-3 weeks in advance")
                            st.write("💡 Check for package deals")
                
                with col2:
                    st.write("**Budget Tips:**")
                    if "budget" in agents_data:
                        budget = agents_data["budget"]
                        st.write(f"💰 Daily budget: ${budget.get('daily_budget', 0)}")
                        st.write("💡 Eat at local restaurants")
                        st.write("💡 Use public transportation")
                    
                    st.write("**Weather Tips:**")
                    if "weather" in agents_data:
                        weather = agents_data["weather"]
                        forecasts = weather.get("daily_forecasts", [])
                        if forecasts:
                            avg_temp = sum(f.get('high_temp', 0) for f in forecasts) / len(forecasts)
                            st.write(f"🌡️ Average temp: {avg_temp:.0f}°C")
                            st.write("💡 Pack layers for comfort")
                            st.write("💡 Bring sunscreen")


def render_view_plans_page():
    """Render view plans page."""
    st.header("📚 Your Trip Plans")
    
    if not st.session_state.plans_history:
        st.info("No trip plans created yet. Go to 'Plan Trip' to create one.")
        return
    
    for i, plan in enumerate(st.session_state.plans_history):
        with st.expander(f"📍 {plan.destination} ({plan.start_date} to {plan.end_date})"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Travelers", plan.travelers)
            with col2:
                st.metric("Budget", f"${plan.budget:,.0f}")
            with col3:
                duration = (datetime.fromisoformat(plan.end_date) - datetime.fromisoformat(plan.start_date)).days
                st.metric("Duration", f"{duration} days")
            with col4:
                st.metric("Currency", plan.currency)
            
            st.divider()
            
            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                json_export = st.session_state.trip_planner.export_plan(plan, format="json")
                st.download_button(
                    label="📥 Download JSON",
                    data=json_export,
                    file_name=f"trip_{plan.destination}_{plan.start_date}.json",
                    mime="application/json",
                    key=f"json_download_{i}"
                )
            
            with col2:
                text_export = st.session_state.trip_planner.export_plan(plan, format="text")
                st.download_button(
                    label="📄 Download Text",
                    data=text_export,
                    file_name=f"trip_{plan.destination}_{plan.start_date}.txt",
                    mime="text/plain",
                    key=f"text_download_{i}"
                )
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.plans_history.pop(i)
                    st.rerun()


def render_preferences_page():
    """Render preferences page."""
    st.header("⚙️ Travel Preferences")
    
    memory_service = st.session_state.trip_planner.memory_service
    
    # Get or create preferences
    preferences = memory_service.get_user_preferences(st.session_state.user_id)
    if not preferences:
        preferences = memory_service.create_user_preferences(st.session_state.user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        travel_style = st.selectbox(
            "Travel Style",
            ["budget", "luxury", "balanced", "adventure"],
            index=["budget", "luxury", "balanced", "adventure"].index(preferences.preferred_travel_style)
        )
        
        climate = st.selectbox(
            "Preferred Climate",
            ["tropical", "temperate", "cold", "desert", "mixed"],
            index=["tropical", "temperate", "cold", "desert", "mixed"].index(preferences.preferred_climate)
        )
        
        home_currency = st.selectbox(
            "Home Currency",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "MXN"],
            index=["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "MXN"].index(preferences.home_currency)
        )
    
    with col2:
        home_country = st.text_input("Home Country", value=preferences.home_country)
        
        travel_companions = st.selectbox(
            "Travel Companions",
            ["solo", "couple", "family", "group"],
            index=["solo", "couple", "family", "group"].index(preferences.travel_companions)
        )
        
        budget_min = st.number_input("Min Budget", value=float(preferences.preferred_budget_range["min"]), step=100.0)
        budget_max = st.number_input("Max Budget", value=float(preferences.preferred_budget_range["max"]), step=100.0)
    
    # Activities and cuisines
    st.subheader("Interests")
    col1, col2 = st.columns(2)
    
    with col1:
        activities_input = st.text_area(
            "Preferred Activities (comma-separated)",
            value=", ".join(preferences.preferred_activities),
            help="e.g., hiking, museums, beaches, food tours"
        )
    
    with col2:
        cuisines_input = st.text_area(
            "Preferred Cuisines (comma-separated)",
            value=", ".join(preferences.preferred_cuisines),
            help="e.g., Italian, Japanese, Thai, Mexican"
        )
    
    # Save preferences
    if st.button("💾 Save Preferences", type="primary", use_container_width=True):
        updates = {
            "preferred_travel_style": travel_style,
            "preferred_climate": climate,
            "home_currency": home_currency,
            "home_country": home_country,
            "travel_companions": travel_companions,
            "preferred_budget_range": {"min": budget_min, "max": budget_max},
            "preferred_activities": [a.strip() for a in activities_input.split(",") if a.strip()],
            "preferred_cuisines": [c.strip() for c in cuisines_input.split(",") if c.strip()]
        }
        
        memory_service.update_user_preferences(st.session_state.user_id, updates)
        st.success("✅ Preferences saved successfully!")


def render_alerts_page():
    """Render alerts page."""
    st.header("🔔 Alerts & Monitoring")
    
    alerts_service = st.session_state.trip_planner.alerts_service
    
    # Alerts summary
    summary = alerts_service.get_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alerts", summary["total_alerts"])
    with col2:
        st.metric("Price Monitors", summary["price_monitors"])
    with col3:
        st.metric("Flight Monitors", summary["flight_monitors"])
    with col4:
        st.metric("Weather Monitors", summary["weather_monitors"])
    
    st.divider()
    
    # Alert types
    if summary["alert_types"]:
        st.subheader("Alert Types")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(summary["alert_types"])
        with col2:
            st.bar_chart(summary["severities"])
    
    st.divider()
    
    # Recent alerts
    st.subheader("Recent Alerts")
    unread_alerts = alerts_service.get_unread_alerts()
    
    if unread_alerts:
        for alert in unread_alerts[:10]:
            with st.expander(f"🔔 {alert.title} ({alert.severity.value})"):
                st.write(f"**Message:** {alert.message}")
                st.write(f"**Type:** {alert.alert_type.value}")
                st.write(f"**Created:** {alert.created_at.isoformat()}")
                
                if st.button("Mark as Read", key=f"mark_read_{alert.alert_id}"):
                    alerts_service.mark_alert_as_read(alert.alert_id)
                    st.rerun()
    else:
        st.info("No unread alerts")


def render_help_page():
    """Render help page."""
    st.header("❓ Help & Documentation")
    
    tabs = st.tabs(["Getting Started", "Features", "FAQ", "About"])
    
    with tabs[0]:
        st.subheader("Getting Started")
        st.markdown("""
        1. **Create a Trip Plan**: Go to "Plan Trip" and fill in your travel details
        2. **View Your Plans**: Check "View Plans" to see all your created trips
        3. **Manage Preferences**: Set your travel preferences in "Preferences"
        4. **Monitor Alerts**: Track price changes and flight updates in "Alerts"
        5. **Export Plans**: Download your plans as JSON or text
        """)
    
    with tabs[1]:
        st.subheader("Features")
        st.markdown("""
        - **Multi-Agent System**: Specialized agents for weather, flights, hotels, itineraries, budgets, and more
        - **Real-Time Alerts**: Monitor price changes, flight delays, and weather updates
        - **Calendar Integration**: Export your plans to calendar formats
        - **Budget Tracking**: Comprehensive budget breakdown and currency conversion
        - **Preference Management**: Save your travel preferences for personalized recommendations
        - **Data Validation**: Comprehensive input validation and error handling
        """)
    
    with tabs[2]:
        st.subheader("Frequently Asked Questions")
        
        with st.expander("How do I create a trip plan?"):
            st.write("Go to the 'Plan Trip' tab, fill in your destination, dates, budget, and number of travelers, then click 'Create Trip Plan'.")
        
        with st.expander("Can I modify my trip plan?"):
            st.write("Yes, you can create multiple plans and compare them. Each plan is saved in your history.")
        
        with st.expander("How do alerts work?"):
            st.write("Alerts monitor price changes, flight delays, and weather updates. You can view them in the 'Alerts' tab.")
        
        with st.expander("Can I export my plans?"):
            st.write("Yes, you can download your plans as JSON or text files from the 'View Plans' tab.")
    
    with tabs[3]:
        st.subheader("About Travel Planning Agent")
        st.markdown("""
        The Travel Planning Agent is an AI-powered system that helps you plan complete trips by coordinating specialized agents for:
        
        - 🌤️ **Weather Analysis**: Get forecasts and packing recommendations
        - ✈️ **Flight Search**: Find and compare flights
        - 🏨 **Hotel Recommendations**: Discover accommodations
        - 📅 **Itinerary Planning**: Create day-by-day plans
        - 💰 **Budget Optimization**: Track and optimize costs
        - 🌍 **Multi-Language Support**: Get translations and local phrases
        - 📋 **Visa & Age Requirements**: Check eligibility
        - 🚕 **Local Transport**: Find transportation options
        
        Built with Strands framework and powered by AWS Bedrock.
        """)


def main():
    """Main application."""
    render_header()
    
    page = render_sidebar()
    
    if page == "Plan Trip":
        render_plan_trip_page()
    elif page == "View Plans":
        render_view_plans_page()
    elif page == "Preferences":
        render_preferences_page()
    elif page == "Alerts":
        render_alerts_page()
    elif page == "Help":
        render_help_page()


if __name__ == "__main__":
    main()
