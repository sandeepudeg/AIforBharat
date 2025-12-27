#!/usr/bin/env python3
"""
Simplified Streamlit UI for Travel Planning Agent

Single-window interface accepting natural language trip descriptions.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from trip_planner import TripPlanner
from validation import TravelValidator, ErrorHandler

# Page configuration
st.set_page_config(
    page_title="Travel Planner",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, minimal design
st.markdown("""
    <style>
    .main {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
    }
    .stTextArea textarea {
        font-size: 1rem;
        line-height: 1.5;
    }
    .result-box {
        background-color: #ffffff;
        border-left: 4px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .flight-box {
        background-color: #ffffff;
        border-left: 4px solid #2ca02c;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333;
    }
    .hotel-box {
        background-color: #ffffff;
        border-left: 4px solid #d62728;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333;
    }
    .place-box {
        background-color: #ffffff;
        border-left: 4px solid #ff7f0e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333;
    }
    .currency-box {
        background-color: #ffffff;
        border-left: 4px solid #9467bd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333;
    }
    .loading-spinner {
        text-align: center;
        font-size: 1.2rem;
    }
    h3 {
        color: #1f1f1f;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    strong {
        color: #1f1f1f;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "trip_planner" not in st.session_state:
        st.session_state.trip_planner = TripPlanner()
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""


init_session_state()


def parse_natural_language_query(query: str) -> dict:
    """
    Parse natural language query to extract trip details.
    
    Example: "I am planning a trip with my wife and 2 kids from pune to paris 
             from 2024-12-20 to 2024-12-30 suggest the best flight route hotel 
             and conversion rate also suggest the places that can be visited"
    """
    query_lower = query.lower()
    
    # Extract number of travelers
    travelers = 1
    if "wife" in query_lower:
        travelers += 1
    if "husband" in query_lower:
        travelers += 1
    
    # Extract kids/children count
    kids_match = re.search(r'(\d+)\s*kids?', query_lower)
    if kids_match:
        travelers += int(kids_match.group(1))
    
    children_match = re.search(r'(\d+)\s*children', query_lower)
    if children_match:
        travelers += int(children_match.group(1))
    
    # Extract source city
    source = None
    from_match = re.search(r'from\s+([a-zA-Z\s]+?)(?:\s+to|\s+and|\s+on|\s+$)', query_lower)
    if from_match:
        source = from_match.group(1).strip().title()
    
    # Extract destination city
    destination = None
    to_match = re.search(r'to\s+([a-zA-Z\s]+?)(?:\s+from|\s+on|\s+$)', query_lower)
    if to_match:
        destination = to_match.group(1).strip().title()
    
    # Extract dates
    start_date = None
    end_date = None
    
    # Try to find date patterns (YYYY-MM-DD or DD-MM-YYYY)
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})'
    dates = re.findall(date_pattern, query)
    
    if len(dates) >= 2:
        start_date = dates[0]
        end_date = dates[1]
    elif len(dates) == 1:
        start_date = dates[0]
    
    # Extract budget if mentioned
    budget = 3000  # Default budget
    budget_match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
    if budget_match:
        budget = float(budget_match.group(1).replace(',', ''))
    
    # Extract currency preference
    currency = "USD"
    currency_codes = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "MXN"]
    query_upper = query.upper()
    for code in currency_codes:
        if code in query_upper:
            currency = code
            break
    
    return {
        "source": source,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget": budget,
        "currency": currency,
        "raw_query": query
    }


def gather_all_agent_data(plan):
    """Gather data from all agents with workflow tracking."""
    from datetime import datetime as dt
    
    agents_data = {}
    workflow_steps = []
    
    # Calculate trip days
    try:
        trip_days = (dt.fromisoformat(plan.end_date) - dt.fromisoformat(plan.start_date)).days or 1
    except:
        trip_days = 1
    
    # Step 1: Flights
    workflow_steps.append({"agent": "✈️ Flight Agent", "status": "running", "description": "Searching for flights..."})
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
            workflow_steps[-1]["status"] = "completed"
            workflow_steps[-1]["description"] = f"Found {len(flights_result['round_trips'])} flight options"
    except Exception as e:
        agents_data["flights_error"] = str(e)
        workflow_steps[-1]["status"] = "error"
        workflow_steps[-1]["description"] = f"Error: {str(e)[:50]}"
    
    # Step 2: Weather
    workflow_steps.append({"agent": "🌤️ Weather Agent", "status": "running", "description": "Fetching weather forecast..."})
    try:
        from agents.weather_agent import WeatherAgent
        weather_agent = WeatherAgent()
        weather_data = weather_agent.get_forecast(
            destination=plan.destination,
            start_date=plan.start_date,
            end_date=plan.end_date
        )
        agents_data["weather"] = weather_data
        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["description"] = "Weather forecast retrieved"
    except Exception as e:
        agents_data["weather_error"] = str(e)
        workflow_steps[-1]["status"] = "error"
        workflow_steps[-1]["description"] = f"Error: {str(e)[:50]}"
    
    # Step 3: Hotels
    workflow_steps.append({"agent": "🏨 Hotel Agent", "status": "running", "description": "Searching for hotels..."})
    try:
        from agents.hotel_agent import HotelAgent
        hotel_agent = HotelAgent()
        daily_budget = plan.budget / plan.travelers / trip_days
        
        hotels = hotel_agent.get_recommendations(
            destination=plan.destination,
            budget=daily_budget
        )
        agents_data["hotels"] = hotels
        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["description"] = f"Found {len(hotels)} hotel recommendations"
    except Exception as e:
        agents_data["hotels_error"] = str(e)
        workflow_steps[-1]["status"] = "error"
        workflow_steps[-1]["description"] = f"Error: {str(e)[:50]}"
    
    # Step 4: Itinerary
    workflow_steps.append({"agent": "🗺️ Itinerary Agent", "status": "running", "description": "Creating itinerary..."})
    try:
        from agents.itinerary_agent import ItineraryAgent
        itinerary_agent = ItineraryAgent()
        weather_data = agents_data.get("weather")
        
        itinerary = itinerary_agent.create_itinerary(
            destination=plan.destination,
            start_date=plan.start_date,
            end_date=plan.end_date,
            interests=["culture", "food", "nature"],
            weather_data=weather_data
        )
        agents_data["itinerary"] = itinerary
        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["description"] = f"Created {itinerary.get('total_days', 0)}-day itinerary"
    except Exception as e:
        agents_data["itinerary_error"] = str(e)
        workflow_steps[-1]["status"] = "error"
        workflow_steps[-1]["description"] = f"Error: {str(e)[:50]}"
    
    # Step 5: Budget
    workflow_steps.append({"agent": "💰 Budget Agent", "status": "running", "description": "Analyzing budget..."})
    try:
        from agents.budget_agent import BudgetAgent
        budget_agent = BudgetAgent()
        
        flights_cost = agents_data.get("flights", {}).get("total_cost", 0)
        hotels_cost = agents_data.get("hotels", {}).get("total_cost", 0) if isinstance(agents_data.get("hotels"), dict) else 0
        
        budget_breakdown = budget_agent.get_budget_breakdown(
            total_budget=plan.budget,
            trip_days=trip_days,
            home_currency=plan.currency,
            destination_currency=plan.currency
        )
        agents_data["budget"] = budget_breakdown
        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["description"] = "Budget breakdown calculated"
    except Exception as e:
        agents_data["budget_error"] = str(e)
        workflow_steps[-1]["status"] = "error"
        workflow_steps[-1]["description"] = f"Error: {str(e)[:50]}"
    
    agents_data["workflow"] = workflow_steps
    return agents_data


def display_workflow(workflow_steps):
    """Display agent workflow as a visual timeline."""
    st.markdown("### 🔄 Agent Workflow")
    
    for i, step in enumerate(workflow_steps):
        agent = step["agent"]
        status = step["status"]
        description = step["description"]
        
        # Status icon
        if status == "completed":
            icon = "✅"
            color = "#2ca02c"
        elif status == "running":
            icon = "⏳"
            color = "#ff7f0e"
        else:  # error
            icon = "❌"
            color = "#d62728"
        
        # Display step
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 0.5rem 0; padding: 0.75rem; background-color: #f9f9f9; border-radius: 0.5rem; border-left: 4px solid {color};">
            <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
            <div style="flex: 1;">
                <strong style="color: #1f1f1f;">{agent}</strong><br>
                <span style="color: #666666; font-size: 0.9rem;">{description}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add arrow between steps (except for last step)
        if i < len(workflow_steps) - 1:
            st.markdown("""
            <div style="text-align: center; color: #cccccc; font-size: 1.2rem; margin: 0.25rem 0;">↓</div>
            """, unsafe_allow_html=True)


def display_results(agents_data, plan):
    """Display all results in organized sections."""
    
    # Display workflow first
    if "workflow" in agents_data:
        display_workflow(agents_data["workflow"])
        st.divider()
    
    # Flights Section
    if "flights" in agents_data:
        st.markdown("### ✈️ Flight Recommendations")
        flights = agents_data["flights"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="flight-box">
            <strong>Outbound Flight</strong><br>
            {flights['outbound'].get('airline', 'N/A')}<br>
            {flights['outbound'].get('departure_time', 'N/A')} → {flights['outbound'].get('arrival_time', 'N/A')}<br>
            Duration: {flights['outbound'].get('duration_minutes', 0)} min<br>
            Price: ${flights['outbound'].get('price', 0):.2f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="flight-box">
            <strong>Return Flight</strong><br>
            {flights['return'].get('airline', 'N/A')}<br>
            {flights['return'].get('departure_time', 'N/A')} → {flights['return'].get('arrival_time', 'N/A')}<br>
            Duration: {flights['return'].get('duration_minutes', 0)} min<br>
            Price: ${flights['return'].get('price', 0):.2f}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Total Flight Cost:** ${flights['total_cost']:.2f} {flights['currency']}")
    
    # Hotels Section
    if "hotels" in agents_data:
        hotels = agents_data["hotels"]
        if isinstance(hotels, list) and len(hotels) > 0:
            st.markdown("### 🏨 Hotel Recommendations")
            for hotel in hotels[:3]:  # Show top 3
                amenities_str = ", ".join(hotel.get('amenities', [])) if isinstance(hotel.get('amenities'), list) else str(hotel.get('amenities', 'Standard amenities'))
                st.markdown(f"""
                <div class="hotel-box">
                <strong>{hotel.get('name', 'Hotel')}</strong><br>
                ⭐ {hotel.get('rating', 'N/A')} | {hotel.get('address', 'N/A')}<br>
                ${hotel.get('price_per_night', 0):.2f}/night<br>
                Amenities: {amenities_str}
                </div>
                """, unsafe_allow_html=True)
    
    # Places to Visit Section
    if "itinerary" in agents_data:
        st.markdown("### 🗺️ Places to Visit & Itinerary")
        itinerary = agents_data["itinerary"]
        
        if isinstance(itinerary, dict):
            daily_itinerary = itinerary.get("daily_itinerary", [])
            if daily_itinerary:
                for day_plan in daily_itinerary[:3]:  # Show first 3 days
                    day_num = day_plan.get("day", "")
                    date_str = day_plan.get("date", "")
                    day_of_week = day_plan.get("day_of_week", "")
                    
                    st.markdown(f"**Day {day_num} - {day_of_week} ({date_str})**")
                    
                    # Morning activity
                    morning = day_plan.get("morning", {})
                    if morning:
                        st.markdown(f"""
                        <div class="place-box">
                        🌅 Morning ({morning.get('time', '')}): {morning.get('activity', 'Rest')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Afternoon activity
                    afternoon = day_plan.get("afternoon", {})
                    if afternoon:
                        st.markdown(f"""
                        <div class="place-box">
                        ☀️ Afternoon ({afternoon.get('time', '')}): {afternoon.get('activity', 'Explore')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Evening activity
                    evening = day_plan.get("evening", {})
                    if evening:
                        st.markdown(f"""
                        <div class="place-box">
                        🌙 Evening ({evening.get('time', '')}): {evening.get('activity', 'Dinner')}
                        </div>
                        """, unsafe_allow_html=True)
    
    # Currency Conversion Section
    if "budget" in agents_data:
        st.markdown("### 💱 Budget & Currency Conversion")
        budget = agents_data["budget"]
        
        from datetime import datetime as dt
        trip_days = (dt.fromisoformat(plan.end_date) - dt.fromisoformat(plan.start_date)).days or 1
        
        st.markdown(f"""
        <div class="currency-box">
        <strong>Total Budget:</strong> {plan.currency} {budget.get('total_budget', 0):.2f}<br>
        <strong>Daily Budget:</strong> {plan.currency} {budget.get('daily_budget', 0):.2f}<br>
        <strong>Travelers:</strong> {plan.travelers}<br>
        <strong>Trip Duration:</strong> {trip_days} days
        </div>
        """, unsafe_allow_html=True)
    
    # Weather Section
    if "weather" in agents_data:
        st.markdown("### 🌤️ Weather Forecast")
        weather = agents_data["weather"]
        if isinstance(weather, dict):
            st.info(f"Expected weather: {weather.get('summary', 'Check weather forecast')}")


def main():
    """Main application."""
    init_session_state()
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>✈️ Travel Planner</h1>
        <p style="font-size: 1.1rem; color: #666;">
            Describe your trip in natural language and get complete travel recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main input area
    st.markdown("### 📝 Describe Your Trip")
    
    user_query = st.text_area(
        "Tell us about your trip:",
        placeholder="""Example: I am planning a trip with my wife and 2 kids from Pune to Paris 
from 2024-12-20 to 2024-12-30. Suggest the best flight route, hotel, 
and conversion rate. Also suggest the places that can be visited during that time.""",
        height=120,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        submit_button = st.button("🔍 Plan My Trip", use_container_width=True)
    
    # Process query
    if submit_button and user_query:
        st.session_state.last_query = user_query
        
        with st.spinner("🔄 Planning your trip..."):
            # Parse natural language
            parsed_data = parse_natural_language_query(user_query)
            
            # Validate parsed data
            if not parsed_data["source"] or not parsed_data["destination"]:
                st.error("❌ Could not extract source and destination from your query. Please include 'from [city]' and 'to [city]'.")
                st.info("Example: 'I want to travel from Pune to Paris'")
                return
            
            if not parsed_data["start_date"] or not parsed_data["end_date"]:
                st.error("❌ Could not extract dates from your query. Please include dates in YYYY-MM-DD format.")
                st.info("Example: 'from 2024-12-20 to 2024-12-30'")
                return
            
            # Create trip plan
            try:
                plan = st.session_state.trip_planner.create_trip_plan(
                    source=parsed_data["source"],
                    destination=parsed_data["destination"],
                    start_date=parsed_data["start_date"],
                    end_date=parsed_data["end_date"],
                    travelers=parsed_data["travelers"],
                    budget=parsed_data["budget"],
                    currency=parsed_data["currency"],
                    user_id="user_default"
                )
                
                st.session_state.current_plan = plan
                
                # Gather all agent data
                agents_data = gather_all_agent_data(plan)
                
                # Display results
                st.success("✅ Trip plan created successfully!")
                st.divider()
                
                display_results(agents_data, plan)
                
            except Exception as e:
                error_info = ErrorHandler.handle_exception(e, "create_trip_plan")
                st.error(f"❌ Error: {error_info['user_message']}")
    
    # Show last query if available
    if st.session_state.last_query and not submit_button:
        st.divider()
        st.markdown("### 📋 Last Query")
        st.text(st.session_state.last_query)


if __name__ == "__main__":
    main()
