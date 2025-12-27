#!/usr/bin/env python3
"""
Alerts Service for Travel Planning Agent

Handles real-time monitoring for price changes, flight delays, and weather alerts.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts."""
    PRICE_DROP = "price_drop"
    PRICE_INCREASE = "price_increase"
    FLIGHT_DELAY = "flight_delay"
    WEATHER_CHANGE = "weather_change"
    BOOKING_REMINDER = "booking_reminder"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert."""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    created_at: datetime
    triggered_at: Optional[datetime] = None
    is_read: bool = False
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "is_read": self.is_read,
            "metadata": self.metadata
        }


@dataclass
class PriceMonitor:
    """Monitors price changes for flights and hotels."""
    item_id: str
    item_type: str  # "flight" or "hotel"
    original_price: float
    current_price: float
    currency: str
    threshold_percent: float = 5.0  # Alert if price changes by this percentage
    last_checked: datetime = field(default_factory=datetime.now)
    
    def check_price_change(self, new_price: float) -> Optional[Dict]:
        """
        Check if price has changed significantly.
        
        Args:
            new_price: New price to check
            
        Returns:
            Dictionary with change info if threshold exceeded, None otherwise
        """
        price_change = ((new_price - self.current_price) / self.current_price) * 100
        
        if abs(price_change) >= self.threshold_percent:
            self.current_price = new_price
            self.last_checked = datetime.now()
            
            return {
                "price_change_percent": price_change,
                "old_price": self.current_price,
                "new_price": new_price,
                "savings": self.current_price - new_price if new_price < self.current_price else 0
            }
        
        self.last_checked = datetime.now()
        return None


@dataclass
class FlightMonitor:
    """Monitors flight status for delays."""
    flight_id: str
    flight_number: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    airline: str
    last_status_check: datetime = field(default_factory=datetime.now)
    current_status: str = "on_time"
    delay_minutes: int = 0
    
    def update_status(self, new_status: str, delay_minutes: int = 0) -> Optional[Dict]:
        """
        Update flight status and check for delays.
        
        Args:
            new_status: New flight status
            delay_minutes: Delay in minutes if delayed
            
        Returns:
            Dictionary with delay info if status changed, None otherwise
        """
        status_changed = new_status != self.current_status
        
        if status_changed or delay_minutes != self.delay_minutes:
            old_status = self.current_status
            old_delay = self.delay_minutes
            
            self.current_status = new_status
            self.delay_minutes = delay_minutes
            self.last_status_check = datetime.now()
            
            return {
                "old_status": old_status,
                "new_status": new_status,
                "old_delay_minutes": old_delay,
                "new_delay_minutes": delay_minutes,
                "status_changed": status_changed
            }
        
        self.last_status_check = datetime.now()
        return None


@dataclass
class WeatherMonitor:
    """Monitors weather changes for destination."""
    destination: str
    current_temp: float
    current_condition: str
    forecast_date: datetime
    last_checked: datetime = field(default_factory=datetime.now)
    temp_change_threshold: float = 10.0  # Alert if temp changes by this much
    
    def update_weather(self, new_temp: float, new_condition: str) -> Optional[Dict]:
        """
        Update weather and check for significant changes.
        
        Args:
            new_temp: New temperature
            new_condition: New weather condition
            
        Returns:
            Dictionary with weather change info if significant, None otherwise
        """
        temp_change = abs(new_temp - self.current_temp)
        condition_changed = new_condition != self.current_condition
        
        if temp_change >= self.temp_change_threshold or condition_changed:
            old_temp = self.current_temp
            old_condition = self.current_condition
            
            self.current_temp = new_temp
            self.current_condition = new_condition
            self.last_checked = datetime.now()
            
            return {
                "old_temp": old_temp,
                "new_temp": new_temp,
                "temp_change": temp_change,
                "old_condition": old_condition,
                "new_condition": new_condition,
                "condition_changed": condition_changed
            }
        
        self.last_checked = datetime.now()
        return None


class AlertsService:
    """Service for managing real-time alerts."""
    
    def __init__(self):
        """Initialize alerts service."""
        self.alerts: List[Alert] = []
        self.price_monitors: Dict[str, PriceMonitor] = {}
        self.flight_monitors: Dict[str, FlightMonitor] = {}
        self.weather_monitors: Dict[str, WeatherMonitor] = {}
        self.alert_callbacks: List[Callable] = []
        self._alert_counter = 0
        logger.info("Alerts service initialized")
    
    def register_alert_callback(self, callback: Callable):
        """
        Register a callback to be called when alerts are triggered.
        
        Args:
            callback: Function to call with alert as parameter
        """
        self.alert_callbacks.append(callback)
        logger.info(f"Registered alert callback: {callback.__name__}")
    
    def _trigger_alert(self, alert: Alert):
        """Trigger an alert and call registered callbacks."""
        alert.triggered_at = datetime.now()
        self.alerts.append(alert)
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error calling alert callback: {e}")
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        self._alert_counter += 1
        return f"alert_{self._alert_counter}_{datetime.now().timestamp()}"
    
    # Price Monitoring
    
    def add_price_monitor(self, item_id: str, item_type: str, price: float, 
                         currency: str, threshold_percent: float = 5.0):
        """
        Add a price monitor for a flight or hotel.
        
        Args:
            item_id: Unique identifier for the item
            item_type: "flight" or "hotel"
            price: Current price
            currency: Currency code
            threshold_percent: Alert threshold percentage
        """
        monitor = PriceMonitor(
            item_id=item_id,
            item_type=item_type,
            original_price=price,
            current_price=price,
            currency=currency,
            threshold_percent=threshold_percent
        )
        self.price_monitors[item_id] = monitor
        logger.info(f"Added price monitor for {item_type} {item_id}")
    
    def check_price_update(self, item_id: str, new_price: float) -> Optional[Alert]:
        """
        Check for price changes and create alert if needed.
        
        Args:
            item_id: Item identifier
            new_price: New price
            
        Returns:
            Alert if price changed significantly, None otherwise
        """
        if item_id not in self.price_monitors:
            logger.warning(f"No price monitor found for {item_id}")
            return None
        
        monitor = self.price_monitors[item_id]
        change_info = monitor.check_price_change(new_price)
        
        if change_info is None:
            return None
        
        # Determine alert type and severity
        if change_info["price_change_percent"] < 0:
            alert_type = AlertType.PRICE_DROP
            severity = AlertSeverity.HIGH if abs(change_info["price_change_percent"]) > 10 else AlertSeverity.MEDIUM
            title = f"Price Drop: {monitor.item_type.capitalize()}"
            message = f"Price dropped by {abs(change_info['price_change_percent']):.1f}%! Save {change_info['savings']:.2f} {monitor.currency}"
        else:
            alert_type = AlertType.PRICE_INCREASE
            severity = AlertSeverity.MEDIUM
            title = f"Price Increase: {monitor.item_type.capitalize()}"
            message = f"Price increased by {change_info['price_change_percent']:.1f}%"
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            created_at=datetime.now(),
            metadata={
                "item_id": item_id,
                "item_type": monitor.item_type,
                "old_price": change_info["old_price"],
                "new_price": change_info["new_price"],
                "currency": monitor.currency,
                "price_change_percent": change_info["price_change_percent"]
            }
        )
        
        self._trigger_alert(alert)
        return alert
    
    # Flight Monitoring
    
    def add_flight_monitor(self, flight_id: str, flight_number: str, 
                          scheduled_departure: datetime, scheduled_arrival: datetime,
                          airline: str):
        """
        Add a flight monitor for delay tracking.
        
        Args:
            flight_id: Unique flight identifier
            flight_number: Flight number
            scheduled_departure: Scheduled departure time
            scheduled_arrival: Scheduled arrival time
            airline: Airline name
        """
        monitor = FlightMonitor(
            flight_id=flight_id,
            flight_number=flight_number,
            scheduled_departure=scheduled_departure,
            scheduled_arrival=scheduled_arrival,
            airline=airline
        )
        self.flight_monitors[flight_id] = monitor
        logger.info(f"Added flight monitor for {flight_number}")
    
    def check_flight_status(self, flight_id: str, status: str, 
                           delay_minutes: int = 0) -> Optional[Alert]:
        """
        Check flight status and create alert if delayed.
        
        Args:
            flight_id: Flight identifier
            status: Flight status (on_time, delayed, cancelled, boarding, etc.)
            delay_minutes: Delay in minutes if delayed
            
        Returns:
            Alert if status changed significantly, None otherwise
        """
        if flight_id not in self.flight_monitors:
            logger.warning(f"No flight monitor found for {flight_id}")
            return None
        
        monitor = self.flight_monitors[flight_id]
        status_info = monitor.update_status(status, delay_minutes)
        
        if status_info is None:
            return None
        
        # Only create alert for significant status changes
        if status == "delayed" and delay_minutes > 15:
            severity = AlertSeverity.CRITICAL if delay_minutes > 60 else AlertSeverity.HIGH
            alert = Alert(
                alert_id=self._generate_alert_id(),
                alert_type=AlertType.FLIGHT_DELAY,
                severity=severity,
                title=f"Flight Delay: {monitor.flight_number}",
                message=f"Flight {monitor.flight_number} delayed by {delay_minutes} minutes",
                created_at=datetime.now(),
                metadata={
                    "flight_id": flight_id,
                    "flight_number": monitor.flight_number,
                    "airline": monitor.airline,
                    "delay_minutes": delay_minutes,
                    "scheduled_departure": monitor.scheduled_departure.isoformat()
                }
            )
            
            self._trigger_alert(alert)
            return alert
        
        elif status == "cancelled":
            alert = Alert(
                alert_id=self._generate_alert_id(),
                alert_type=AlertType.FLIGHT_DELAY,
                severity=AlertSeverity.CRITICAL,
                title=f"Flight Cancelled: {monitor.flight_number}",
                message=f"Flight {monitor.flight_number} has been cancelled",
                created_at=datetime.now(),
                metadata={
                    "flight_id": flight_id,
                    "flight_number": monitor.flight_number,
                    "airline": monitor.airline,
                    "status": "cancelled"
                }
            )
            
            self._trigger_alert(alert)
            return alert
        
        return None
    
    # Weather Monitoring
    
    def add_weather_monitor(self, destination: str, temp: float, 
                           condition: str, forecast_date: datetime):
        """
        Add a weather monitor for destination.
        
        Args:
            destination: Destination city/location
            temp: Current temperature
            condition: Weather condition
            forecast_date: Date of forecast
        """
        monitor = WeatherMonitor(
            destination=destination,
            current_temp=temp,
            current_condition=condition,
            forecast_date=forecast_date
        )
        self.weather_monitors[destination] = monitor
        logger.info(f"Added weather monitor for {destination}")
    
    def check_weather_update(self, destination: str, new_temp: float, 
                            new_condition: str) -> Optional[Alert]:
        """
        Check weather changes and create alert if significant.
        
        Args:
            destination: Destination
            new_temp: New temperature
            new_condition: New weather condition
            
        Returns:
            Alert if weather changed significantly, None otherwise
        """
        if destination not in self.weather_monitors:
            logger.warning(f"No weather monitor found for {destination}")
            return None
        
        monitor = self.weather_monitors[destination]
        weather_info = monitor.update_weather(new_temp, new_condition)
        
        if weather_info is None:
            return None
        
        # Create alert for significant weather changes
        severity = AlertSeverity.HIGH if weather_info["temp_change"] > 15 else AlertSeverity.MEDIUM
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            alert_type=AlertType.WEATHER_CHANGE,
            severity=severity,
            title=f"Weather Change: {destination}",
            message=f"Weather in {destination} changed to {new_condition} ({new_temp}°C)",
            created_at=datetime.now(),
            metadata={
                "destination": destination,
                "old_temp": weather_info["old_temp"],
                "new_temp": weather_info["new_temp"],
                "temp_change": weather_info["temp_change"],
                "old_condition": weather_info["old_condition"],
                "new_condition": weather_info["new_condition"]
            }
        )
        
        self._trigger_alert(alert)
        return alert
    
    # Booking Reminders
    
    def create_booking_reminder(self, item_type: str, item_name: str, 
                               booking_deadline: datetime) -> Alert:
        """
        Create a booking reminder alert.
        
        Args:
            item_type: Type of item (flight, hotel, activity)
            item_name: Name of item
            booking_deadline: Deadline for booking
            
        Returns:
            Created Alert
        """
        days_until = (booking_deadline - datetime.now()).days
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            alert_type=AlertType.BOOKING_REMINDER,
            severity=AlertSeverity.MEDIUM if days_until > 3 else AlertSeverity.HIGH,
            title=f"Booking Reminder: {item_name}",
            message=f"Book your {item_type} within {days_until} days to secure the price",
            created_at=datetime.now(),
            metadata={
                "item_type": item_type,
                "item_name": item_name,
                "booking_deadline": booking_deadline.isoformat(),
                "days_until": days_until
            }
        )
        
        self._trigger_alert(alert)
        return alert
    
    # Alert Management
    
    def get_unread_alerts(self) -> List[Alert]:
        """Get all unread alerts."""
        return [alert for alert in self.alerts if not alert.is_read]
    
    def get_alerts_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Get alerts by type."""
        return [alert for alert in self.alerts if alert.alert_type == alert_type]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def mark_alert_as_read(self, alert_id: str):
        """Mark an alert as read."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.is_read = True
                logger.info(f"Marked alert {alert_id} as read")
                return
    
    def mark_all_as_read(self):
        """Mark all alerts as read."""
        for alert in self.alerts:
            alert.is_read = True
        logger.info("Marked all alerts as read")
    
    def get_alerts_since(self, since: datetime) -> List[Alert]:
        """Get alerts created since a specific time."""
        return [alert for alert in self.alerts if alert.created_at >= since]
    
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        old_count = len(self.alerts)
        self.alerts = [alert for alert in self.alerts if alert.created_at >= cutoff]
        removed = old_count - len(self.alerts)
        logger.info(f"Cleared {removed} alerts older than {days} days")
    
    def export_alerts(self) -> Dict:
        """Export all alerts to dictionary."""
        return {
            "total_alerts": len(self.alerts),
            "unread_count": len(self.get_unread_alerts()),
            "alerts": [alert.to_dict() for alert in sorted(self.alerts, key=lambda a: a.created_at, reverse=True)]
        }
    
    def get_summary(self) -> Dict:
        """Get alerts summary."""
        alert_types = {}
        severities = {}
        
        for alert in self.alerts:
            alert_types[alert.alert_type.value] = alert_types.get(alert.alert_type.value, 0) + 1
            severities[alert.severity.value] = severities.get(alert.severity.value, 0) + 1
        
        return {
            "total_alerts": len(self.alerts),
            "unread_alerts": len(self.get_unread_alerts()),
            "alert_types": alert_types,
            "severities": severities,
            "price_monitors": len(self.price_monitors),
            "flight_monitors": len(self.flight_monitors),
            "weather_monitors": len(self.weather_monitors)
        }
