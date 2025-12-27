#!/usr/bin/env python3
"""
Tests for Alerts Service

Tests price monitoring, flight delay detection, and weather alerts.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alerts_service import (
    AlertsService, Alert, AlertType, AlertSeverity,
    PriceMonitor, FlightMonitor, WeatherMonitor
)


class TestPriceMonitoring:
    """Tests for price monitoring functionality."""
    
    def test_add_price_monitor(self):
        """Test adding a price monitor."""
        service = AlertsService()
        service.add_price_monitor("flight_123", "flight", 500.0, "USD")
        
        assert "flight_123" in service.price_monitors
        monitor = service.price_monitors["flight_123"]
        assert monitor.current_price == 500.0
        assert monitor.item_type == "flight"
    
    def test_price_drop_detection(self):
        """Test detecting price drops."""
        service = AlertsService()
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        
        # Price drops by 10% - should trigger alert
        alert = service.check_price_update("flight_123", 450.0)
        
        assert alert is not None
        assert alert.alert_type == AlertType.PRICE_DROP
        assert alert.severity == AlertSeverity.MEDIUM  # 10% drop = MEDIUM
        assert "10" in alert.message
    
    def test_price_increase_detection(self):
        """Test detecting price increases."""
        service = AlertsService()
        service.add_price_monitor("hotel_456", "hotel", 200.0, "EUR", threshold_percent=5.0)
        
        # Price increases by 8% - should trigger alert
        alert = service.check_price_update("hotel_456", 216.0)
        
        assert alert is not None
        assert alert.alert_type == AlertType.PRICE_INCREASE
        assert alert.severity == AlertSeverity.MEDIUM
    
    def test_price_change_below_threshold(self):
        """Test that small price changes don't trigger alerts."""
        service = AlertsService()
        service.add_price_monitor("flight_789", "flight", 500.0, "USD", threshold_percent=5.0)
        
        # Price drops by 2% - below threshold
        alert = service.check_price_update("flight_789", 490.0)
        
        assert alert is None
    
    def test_multiple_price_monitors(self):
        """Test managing multiple price monitors."""
        service = AlertsService()
        service.add_price_monitor("flight_1", "flight", 500.0, "USD")
        service.add_price_monitor("flight_2", "flight", 600.0, "USD")
        service.add_price_monitor("hotel_1", "hotel", 200.0, "EUR")
        
        assert len(service.price_monitors) == 3
        
        # Update one price
        alert = service.check_price_update("flight_1", 450.0)
        assert alert is not None
        
        # Others should be unaffected
        assert service.price_monitors["flight_2"].current_price == 600.0
        assert service.price_monitors["hotel_1"].current_price == 200.0


class TestFlightMonitoring:
    """Tests for flight monitoring functionality."""
    
    def test_add_flight_monitor(self):
        """Test adding a flight monitor."""
        service = AlertsService()
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        
        service.add_flight_monitor("flight_aa100", "AA100", departure, arrival, "American Airlines")
        
        assert "flight_aa100" in service.flight_monitors
        monitor = service.flight_monitors["flight_aa100"]
        assert monitor.flight_number == "AA100"
        assert monitor.current_status == "on_time"
    
    def test_flight_delay_detection(self):
        """Test detecting flight delays."""
        service = AlertsService()
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        
        service.add_flight_monitor("flight_ua200", "UA200", departure, arrival, "United Airlines")
        
        # Flight delayed by 45 minutes - should trigger alert
        alert = service.check_flight_status("flight_ua200", "delayed", delay_minutes=45)
        
        assert alert is not None
        assert alert.alert_type == AlertType.FLIGHT_DELAY
        assert alert.severity == AlertSeverity.HIGH
        assert "45" in alert.message
    
    def test_flight_cancellation_alert(self):
        """Test detecting flight cancellations."""
        service = AlertsService()
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        
        service.add_flight_monitor("flight_sw300", "SW300", departure, arrival, "Southwest Airlines")
        
        # Flight cancelled - should trigger critical alert
        alert = service.check_flight_status("flight_sw300", "cancelled")
        
        assert alert is not None
        assert alert.alert_type == AlertType.FLIGHT_DELAY
        assert alert.severity == AlertSeverity.CRITICAL
        assert "cancelled" in alert.message.lower()
    
    def test_small_delay_no_alert(self):
        """Test that small delays don't trigger alerts."""
        service = AlertsService()
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        
        service.add_flight_monitor("flight_dl400", "DL400", departure, arrival, "Delta Airlines")
        
        # Flight delayed by 10 minutes - below threshold
        alert = service.check_flight_status("flight_dl400", "delayed", delay_minutes=10)
        
        assert alert is None
    
    def test_flight_status_transitions(self):
        """Test flight status transitions."""
        service = AlertsService()
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        
        service.add_flight_monitor("flight_ba500", "BA500", departure, arrival, "British Airways")
        
        # Transition: on_time -> boarding (no alert)
        alert = service.check_flight_status("flight_ba500", "boarding")
        assert alert is None
        
        # Transition: boarding -> delayed (alert)
        alert = service.check_flight_status("flight_ba500", "delayed", delay_minutes=30)
        assert alert is not None


class TestWeatherMonitoring:
    """Tests for weather monitoring functionality."""
    
    def test_add_weather_monitor(self):
        """Test adding a weather monitor."""
        service = AlertsService()
        forecast_date = datetime.now() + timedelta(days=3)
        
        service.add_weather_monitor("Paris", 15.0, "Sunny", forecast_date)
        
        assert "Paris" in service.weather_monitors
        monitor = service.weather_monitors["Paris"]
        assert monitor.current_temp == 15.0
        assert monitor.current_condition == "Sunny"
    
    def test_temperature_change_alert(self):
        """Test detecting significant temperature changes."""
        service = AlertsService()
        forecast_date = datetime.now() + timedelta(days=3)
        
        service.add_weather_monitor("Tokyo", 20.0, "Cloudy", forecast_date)
        
        # Temperature drops by 12°C - should trigger alert
        alert = service.check_weather_update("Tokyo", 8.0, "Rainy")
        
        assert alert is not None
        assert alert.alert_type == AlertType.WEATHER_CHANGE
        assert alert.severity == AlertSeverity.MEDIUM  # 12°C change = MEDIUM
        assert "8" in alert.message
    
    def test_weather_condition_change_alert(self):
        """Test detecting weather condition changes."""
        service = AlertsService()
        forecast_date = datetime.now() + timedelta(days=3)
        
        service.add_weather_monitor("London", 12.0, "Sunny", forecast_date)
        
        # Condition changes to stormy - should trigger alert
        alert = service.check_weather_update("London", 12.0, "Stormy")
        
        assert alert is not None
        assert alert.alert_type == AlertType.WEATHER_CHANGE
        assert "Stormy" in alert.message
    
    def test_small_temperature_change_no_alert(self):
        """Test that small temperature changes don't trigger alerts."""
        service = AlertsService()
        forecast_date = datetime.now() + timedelta(days=3)
        
        service.add_weather_monitor("Barcelona", 22.0, "Sunny", forecast_date)
        
        # Temperature changes by 3°C - below threshold
        alert = service.check_weather_update("Barcelona", 25.0, "Sunny")
        
        assert alert is None


class TestAlertManagement:
    """Tests for alert management functionality."""
    
    def test_alert_callbacks(self):
        """Test alert callback registration and triggering."""
        service = AlertsService()
        triggered_alerts = []
        
        def callback(alert):
            triggered_alerts.append(alert)
        
        service.register_alert_callback(callback)
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        
        # Trigger alert
        service.check_price_update("flight_123", 450.0)
        
        assert len(triggered_alerts) == 1
        assert triggered_alerts[0].alert_type == AlertType.PRICE_DROP
    
    def test_unread_alerts(self):
        """Test tracking unread alerts."""
        service = AlertsService()
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        
        # Create alert
        service.check_price_update("flight_123", 450.0)
        
        unread = service.get_unread_alerts()
        assert len(unread) == 1
        
        # Mark as read
        service.mark_alert_as_read(unread[0].alert_id)
        
        unread = service.get_unread_alerts()
        assert len(unread) == 0
    
    def test_get_alerts_by_type(self):
        """Test filtering alerts by type."""
        service = AlertsService()
        
        # Create price alert
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_123", 450.0)
        
        # Create weather alert
        service.add_weather_monitor("Paris", 15.0, "Sunny", datetime.now() + timedelta(days=3))
        service.check_weather_update("Paris", 5.0, "Rainy")
        
        price_alerts = service.get_alerts_by_type(AlertType.PRICE_DROP)
        weather_alerts = service.get_alerts_by_type(AlertType.WEATHER_CHANGE)
        
        assert len(price_alerts) == 1
        assert len(weather_alerts) == 1
    
    def test_get_alerts_by_severity(self):
        """Test filtering alerts by severity."""
        service = AlertsService()
        
        # Create high severity alert
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_123", 400.0)  # 20% drop = HIGH
        
        # Create medium severity alert
        service.add_price_monitor("hotel_456", "hotel", 200.0, "EUR", threshold_percent=5.0)
        service.check_price_update("hotel_456", 190.0)  # 5% drop = MEDIUM
        
        high_alerts = service.get_alerts_by_severity(AlertSeverity.HIGH)
        medium_alerts = service.get_alerts_by_severity(AlertSeverity.MEDIUM)
        
        assert len(high_alerts) >= 1
        assert len(medium_alerts) >= 1
    
    def test_booking_reminder(self):
        """Test creating booking reminders."""
        service = AlertsService()
        deadline = datetime.now() + timedelta(days=5)
        
        alert = service.create_booking_reminder("flight", "AA100 to Paris", deadline)
        
        assert alert.alert_type == AlertType.BOOKING_REMINDER
        assert "AA100" in alert.title
        assert "days" in alert.message
    
    def test_clear_old_alerts(self):
        """Test clearing old alerts."""
        service = AlertsService()
        
        # Create alert
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_123", 450.0)
        
        assert len(service.alerts) == 1
        
        # Manually set alert to old date
        service.alerts[0].created_at = datetime.now() - timedelta(days=10)
        
        # Clear alerts older than 7 days
        service.clear_old_alerts(days=7)
        
        assert len(service.alerts) == 0
    
    def test_export_alerts(self):
        """Test exporting alerts."""
        service = AlertsService()
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_123", 450.0)
        
        export = service.export_alerts()
        
        assert export["total_alerts"] == 1
        assert len(export["alerts"]) == 1
        assert export["alerts"][0]["alert_type"] == "price_drop"
    
    def test_get_summary(self):
        """Test getting alerts summary."""
        service = AlertsService()
        
        # Create various alerts
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_123", 450.0)
        
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        service.add_flight_monitor("flight_ua200", "UA200", departure, arrival, "United")
        service.check_flight_status("flight_ua200", "delayed", delay_minutes=45)
        
        summary = service.get_summary()
        
        assert summary["total_alerts"] == 2
        assert summary["price_monitors"] == 1
        assert summary["flight_monitors"] == 1


class TestAlertIntegration:
    """Integration tests for alerts service."""
    
    def test_multiple_monitors_and_alerts(self):
        """Test managing multiple monitors and alerts simultaneously."""
        service = AlertsService()
        
        # Add multiple monitors
        service.add_price_monitor("flight_1", "flight", 500.0, "USD")
        service.add_price_monitor("hotel_1", "hotel", 200.0, "EUR")
        
        departure = datetime.now() + timedelta(days=5)
        arrival = departure + timedelta(hours=3)
        service.add_flight_monitor("flight_aa100", "AA100", departure, arrival, "American")
        
        service.add_weather_monitor("Paris", 15.0, "Sunny", datetime.now() + timedelta(days=3))
        
        # Trigger multiple alerts
        alert1 = service.check_price_update("flight_1", 450.0)
        alert2 = service.check_flight_status("flight_aa100", "delayed", delay_minutes=30)
        alert3 = service.check_weather_update("Paris", 5.0, "Rainy")
        
        assert alert1 is not None
        assert alert2 is not None
        assert alert3 is not None
        assert len(service.alerts) == 3
    
    def test_alert_persistence_across_checks(self):
        """Test that alerts persist across multiple checks."""
        service = AlertsService()
        service.add_price_monitor("flight_123", "flight", 500.0, "USD", threshold_percent=5.0)
        
        # First check - triggers alert
        alert1 = service.check_price_update("flight_123", 450.0)
        assert alert1 is not None
        
        # Second check - no new alert (price stable)
        alert2 = service.check_price_update("flight_123", 450.0)
        assert alert2 is None
        
        # But first alert should still be in history
        assert len(service.alerts) == 1
    
    def test_mark_all_as_read(self):
        """Test marking all alerts as read."""
        service = AlertsService()
        
        # Create multiple alerts
        service.add_price_monitor("flight_1", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_1", 450.0)
        
        service.add_price_monitor("flight_2", "flight", 600.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_2", 540.0)
        
        assert len(service.get_unread_alerts()) == 2
        
        service.mark_all_as_read()
        
        assert len(service.get_unread_alerts()) == 0
    
    def test_get_alerts_since(self):
        """Test getting alerts since a specific time."""
        service = AlertsService()
        
        # Create first alert
        service.add_price_monitor("flight_1", "flight", 500.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_1", 450.0)
        
        # Wait a moment
        import time
        time.sleep(0.1)
        
        cutoff_time = datetime.now()
        
        # Create second alert
        service.add_price_monitor("flight_2", "flight", 600.0, "USD", threshold_percent=5.0)
        service.check_price_update("flight_2", 540.0)
        
        # Get alerts since cutoff
        recent_alerts = service.get_alerts_since(cutoff_time)
        
        assert len(recent_alerts) == 1
        assert recent_alerts[0].metadata["item_id"] == "flight_2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
