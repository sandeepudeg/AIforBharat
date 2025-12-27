#!/usr/bin/env python3
"""
Calendar Service for Travel Planning Agent

Handles calendar event generation, export to iCal format, and Google Calendar integration.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    event_type: str  # "flight", "hotel", "activity", "meal"
    details: Dict = None
    
    def to_ical_format(self) -> str:
        """Convert event to iCalendar format."""
        # Format times in iCalendar format (YYYYMMDDTHHMMSSZ)
        start = self.start_time.strftime("%Y%m%dT%H%M%SZ")
        end = self.end_time.strftime("%Y%m%dT%H%M%SZ")
        
        # Create unique ID
        uid = f"{self.event_type}_{self.start_time.timestamp()}@travelplanner"
        
        # Use timezone-aware UTC datetime
        from datetime import timezone
        utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        ical = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{utc_now}
DTSTART:{start}
DTEND:{end}
SUMMARY:{self.title}
DESCRIPTION:{self.description}
LOCATION:{self.location}
CATEGORIES:{self.event_type.upper()}
END:VEVENT"""
        return ical


class CalendarService:
    """Service for managing calendar events and exports."""
    
    def __init__(self):
        """Initialize calendar service."""
        self.events: List[CalendarEvent] = []
        logger.info("Calendar service initialized")
    
    def add_flight_event(self, flight_info: Dict) -> CalendarEvent:
        """
        Add a flight event to the calendar.
        
        Args:
            flight_info: Dictionary with flight details
                - airline: Airline name
                - flight_number: Flight number
                - departure_city: Departure city
                - arrival_city: Arrival city
                - departure_time: Departure datetime
                - arrival_time: Arrival datetime
                - confirmation: Booking confirmation number
                
        Returns:
            Created CalendarEvent
        """
        logger.info(f"Adding flight event: {flight_info.get('flight_number')}")
        
        departure = flight_info.get("departure_time")
        arrival = flight_info.get("arrival_time")
        
        if isinstance(departure, str):
            departure = datetime.fromisoformat(departure)
        if isinstance(arrival, str):
            arrival = datetime.fromisoformat(arrival)
        
        event = CalendarEvent(
            title=f"Flight {flight_info.get('flight_number')} - {flight_info.get('departure_city')} to {flight_info.get('arrival_city')}",
            description=f"Airline: {flight_info.get('airline')}\nConfirmation: {flight_info.get('confirmation')}",
            start_time=departure,
            end_time=arrival,
            location=f"{flight_info.get('departure_city')} → {flight_info.get('arrival_city')}",
            event_type="flight",
            details=flight_info
        )
        
        self.events.append(event)
        return event
    
    def add_hotel_event(self, hotel_info: Dict) -> List[CalendarEvent]:
        """
        Add hotel check-in and check-out events.
        
        Args:
            hotel_info: Dictionary with hotel details
                - name: Hotel name
                - check_in_date: Check-in date
                - check_out_date: Check-out date
                - address: Hotel address
                - confirmation: Booking confirmation
                - room_number: Room number (optional)
                
        Returns:
            List of created CalendarEvents (check-in and check-out)
        """
        logger.info(f"Adding hotel events: {hotel_info.get('name')}")
        
        check_in = hotel_info.get("check_in_date")
        check_out = hotel_info.get("check_out_date")
        
        if isinstance(check_in, str):
            check_in = datetime.fromisoformat(check_in)
        if isinstance(check_out, str):
            check_out = datetime.fromisoformat(check_out)
        
        # Check-in event (14:00)
        check_in_time = check_in.replace(hour=14, minute=0)
        check_in_event = CalendarEvent(
            title=f"Hotel Check-in: {hotel_info.get('name')}",
            description=f"Confirmation: {hotel_info.get('confirmation')}\nRoom: {hotel_info.get('room_number', 'TBD')}",
            start_time=check_in_time,
            end_time=check_in_time + timedelta(hours=1),
            location=hotel_info.get("address", ""),
            event_type="hotel",
            details=hotel_info
        )
        
        # Check-out event (11:00)
        check_out_time = check_out.replace(hour=11, minute=0)
        check_out_event = CalendarEvent(
            title=f"Hotel Check-out: {hotel_info.get('name')}",
            description=f"Confirmation: {hotel_info.get('confirmation')}",
            start_time=check_out_time,
            end_time=check_out_time + timedelta(hours=1),
            location=hotel_info.get("address", ""),
            event_type="hotel",
            details=hotel_info
        )
        
        self.events.extend([check_in_event, check_out_event])
        return [check_in_event, check_out_event]
    
    def add_activity_event(self, activity_info: Dict) -> CalendarEvent:
        """
        Add an activity event to the calendar.
        
        Args:
            activity_info: Dictionary with activity details
                - name: Activity name
                - start_time: Start datetime
                - end_time: End datetime
                - location: Activity location
                - description: Activity description
                - category: Activity category (e.g., "museum", "restaurant")
                
        Returns:
            Created CalendarEvent
        """
        logger.info(f"Adding activity event: {activity_info.get('name')}")
        
        start = activity_info.get("start_time")
        end = activity_info.get("end_time")
        
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        
        event = CalendarEvent(
            title=activity_info.get("name"),
            description=activity_info.get("description", ""),
            start_time=start,
            end_time=end,
            location=activity_info.get("location", ""),
            event_type="activity",
            details=activity_info
        )
        
        self.events.append(event)
        return event
    
    def add_meal_event(self, meal_info: Dict) -> CalendarEvent:
        """
        Add a meal/restaurant event to the calendar.
        
        Args:
            meal_info: Dictionary with meal details
                - restaurant: Restaurant name
                - time: Reservation time
                - duration: Duration in minutes
                - address: Restaurant address
                - reservation: Reservation confirmation
                - cuisine: Cuisine type
                
        Returns:
            Created CalendarEvent
        """
        logger.info(f"Adding meal event: {meal_info.get('restaurant')}")
        
        time = meal_info.get("time")
        if isinstance(time, str):
            time = datetime.fromisoformat(time)
        
        duration = meal_info.get("duration", 90)
        
        event = CalendarEvent(
            title=f"Dinner: {meal_info.get('restaurant')}",
            description=f"Cuisine: {meal_info.get('cuisine')}\nReservation: {meal_info.get('reservation')}",
            start_time=time,
            end_time=time + timedelta(minutes=duration),
            location=meal_info.get("address", ""),
            event_type="meal",
            details=meal_info
        )
        
        self.events.append(event)
        return event
    
    def export_to_ical(self, filename: str = "trip.ics") -> str:
        """
        Export all events to iCalendar format.
        
        Args:
            filename: Output filename
            
        Returns:
            iCalendar formatted string
        """
        logger.info(f"Exporting {len(self.events)} events to iCalendar format")
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Travel Planning Agent//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Travel Plan
X-WR-TIMEZONE:UTC
X-WR-CALDESC:Calendar events for your travel plan
"""
        
        # Add all events
        for event in sorted(self.events, key=lambda e: e.start_time):
            ical_content += event.to_ical_format() + "\n"
        
        ical_content += "END:VCALENDAR"
        
        return ical_content
    
    def export_to_json(self) -> Dict:
        """
        Export all events to JSON format.
        
        Returns:
            Dictionary with events in JSON-serializable format
        """
        logger.info(f"Exporting {len(self.events)} events to JSON format")
        
        events_data = []
        for event in sorted(self.events, key=lambda e: e.start_time):
            event_dict = {
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "event_type": event.event_type,
                "details": event.details
            }
            events_data.append(event_dict)
        
        return {
            "calendar": {
                "name": "Travel Plan",
                "event_count": len(events_data),
                "events": events_data
            }
        }
    
    def detect_conflicts(self) -> List[Dict]:
        """
        Detect calendar conflicts (overlapping events).
        
        Returns:
            List of conflict dictionaries with event pairs and overlap details
        """
        logger.info("Detecting calendar conflicts")
        
        conflicts = []
        sorted_events = sorted(self.events, key=lambda e: e.start_time)
        
        for i, event1 in enumerate(sorted_events):
            for event2 in sorted_events[i+1:]:
                # Check if events overlap
                if event1.end_time > event2.start_time and event1.start_time < event2.end_time:
                    overlap_start = max(event1.start_time, event2.start_time)
                    overlap_end = min(event1.end_time, event2.end_time)
                    overlap_duration = (overlap_end - overlap_start).total_seconds() / 60
                    
                    conflicts.append({
                        "event1": event1.title,
                        "event2": event2.title,
                        "overlap_start": overlap_start.isoformat(),
                        "overlap_end": overlap_end.isoformat(),
                        "overlap_minutes": overlap_duration
                    })
        
        return conflicts
    
    def get_events_by_date(self, date: datetime) -> List[CalendarEvent]:
        """
        Get all events for a specific date.
        
        Args:
            date: Date to query
            
        Returns:
            List of events on that date
        """
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        return [
            event for event in self.events
            if event.start_time >= date_start and event.start_time < date_end
        ]
    
    def get_events_by_type(self, event_type: str) -> List[CalendarEvent]:
        """
        Get all events of a specific type.
        
        Args:
            event_type: Type of event ("flight", "hotel", "activity", "meal")
            
        Returns:
            List of events of that type
        """
        return [event for event in self.events if event.event_type == event_type]
    
    def clear_events(self):
        """Clear all events from the calendar."""
        logger.info("Clearing all calendar events")
        self.events = []
    
    def get_summary(self) -> Dict:
        """
        Get a summary of calendar events.
        
        Returns:
            Dictionary with event counts and date range
        """
        if not self.events:
            return {
                "total_events": 0,
                "event_types": {},
                "date_range": None
            }
        
        sorted_events = sorted(self.events, key=lambda e: e.start_time)
        
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        return {
            "total_events": len(self.events),
            "event_types": event_types,
            "date_range": {
                "start": sorted_events[0].start_time.isoformat(),
                "end": sorted_events[-1].end_time.isoformat()
            }
        }
