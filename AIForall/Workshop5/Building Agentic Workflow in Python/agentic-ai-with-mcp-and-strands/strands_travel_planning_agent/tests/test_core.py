"""
Unit tests for core components of the Travel Planning Agent.
"""

import pytest
from datetime import datetime
from ..core import (
    AgentRequest,
    AgentResponse,
    AgentRegistry,
    MessageBroker,
    ValidationHelper,
    CurrencyConverter,
    MemoryService,
    ErrorHandler
)


class TestAgentRequest:
    """Test AgentRequest message format."""
    
    def test_create_agent_request(self):
        """Test creating an agent request."""
        request = AgentRequest(
            source="travel_planner",
            target="weather_agent",
            action="get_forecast",
            parameters={"destination": "Paris"}
        )
        
        assert request.source == "travel_planner"
        assert request.target == "weather_agent"
        assert request.action == "get_forecast"
        assert request.parameters["destination"] == "Paris"
        assert request.timestamp is not None
        assert request.request_id is not None


class TestAgentResponse:
    """Test AgentResponse message format."""
    
    def test_create_success_response(self):
        """Test creating a success response."""
        response = AgentResponse(
            source="weather_agent",
            target="travel_planner",
            status="success",
            data={"forecast": "sunny"}
        )
        
        assert response.source == "weather_agent"
        assert response.target == "travel_planner"
        assert response.status == "success"
        assert response.data["forecast"] == "sunny"
        assert response.error_message is None
    
    def test_create_error_response(self):
        """Test creating an error response."""
        response = AgentResponse(
            source="weather_agent",
            target="travel_planner",
            status="error",
            data={},
            error_message="API timeout"
        )
        
        assert response.status == "error"
        assert response.error_message == "API timeout"


class TestAgentRegistry:
    """Test agent registry."""
    
    def test_register_and_get_agent(self):
        """Test registering and retrieving agents."""
        from ..agents.weather_agent import WeatherAgent
        
        registry = AgentRegistry()
        agent = WeatherAgent()
        
        registry.register(agent)
        
        retrieved = registry.get_agent("weather_agent")
        assert retrieved is not None
        assert retrieved.name == "weather_agent"
    
    def test_list_agents(self):
        """Test listing all agents."""
        from ..agents.weather_agent import WeatherAgent
        
        registry = AgentRegistry()
        agent1 = WeatherAgent()
        
        registry.register(agent1)
        
        agents = registry.list_agents()
        assert "weather_agent" in agents


class TestMessageBroker:
    """Test message broker."""
    
    def test_send_and_receive_messages(self):
        """Test sending and receiving messages."""
        broker = MessageBroker()
        
        request = AgentRequest(
            source="travel_planner",
            target="weather_agent",
            action="get_forecast",
            parameters={}
        )
        
        broker.send_request(request)
        
        messages = broker.get_messages()
        assert len(messages) == 1
        assert messages[0]["type"] == "request"
    
    def test_message_history(self):
        """Test message history tracking."""
        broker = MessageBroker()
        
        request = AgentRequest(
            source="travel_planner",
            target="weather_agent",
            action="get_forecast",
            parameters={}
        )
        
        broker.send_request(request)
        broker.clear_queue()
        
        history = broker.get_history()
        assert len(history) == 1


class TestValidationHelper:
    """Test input validation."""
    
    def test_validate_destination(self):
        """Test destination validation."""
        assert ValidationHelper.validate_destination("Paris") is True
        assert ValidationHelper.validate_destination("") is False
        assert ValidationHelper.validate_destination("   ") is False
    
    def test_validate_dates(self):
        """Test date validation."""
        assert ValidationHelper.validate_dates("2025-05-01", "2025-05-05") is True
        assert ValidationHelper.validate_dates("2025-05-05", "2025-05-01") is False
        assert ValidationHelper.validate_dates("invalid", "2025-05-05") is False
    
    def test_validate_budget(self):
        """Test budget validation."""
        assert ValidationHelper.validate_budget(3000) is True
        assert ValidationHelper.validate_budget(3000.50) is True
        assert ValidationHelper.validate_budget(-100) is False
        assert ValidationHelper.validate_budget(0) is False
    
    def test_validate_age(self):
        """Test age validation."""
        assert ValidationHelper.validate_age(30) is True
        assert ValidationHelper.validate_age(0) is False
        assert ValidationHelper.validate_age(150) is False
        assert ValidationHelper.validate_age(200) is False


class TestCurrencyConverter:
    """Test currency conversion."""
    
    def test_convert_usd_to_eur(self):
        """Test USD to EUR conversion."""
        amount = CurrencyConverter.convert(100, "USD", "EUR")
        assert amount == 92.0
    
    def test_convert_same_currency(self):
        """Test converting same currency."""
        amount = CurrencyConverter.convert(100, "USD", "USD")
        assert amount == 100
    
    def test_get_exchange_rate(self):
        """Test getting exchange rate."""
        rate = CurrencyConverter.get_rate("USD", "EUR")
        assert rate == 0.92
    
    def test_invalid_conversion(self):
        """Test invalid currency conversion."""
        with pytest.raises(ValueError):
            CurrencyConverter.convert(100, "USD", "XYZ")


class TestMemoryService:
    """Test memory service."""
    
    def test_save_and_get_preferences(self):
        """Test saving and retrieving preferences."""
        memory = MemoryService()
        
        preferences = {
            "budget": 3000,
            "travel_style": "adventure",
            "interests": ["hiking", "culture"]
        }
        
        memory.save_preferences("user_123", preferences)
        retrieved = memory.get_preferences("user_123")
        
        assert retrieved == preferences
    
    def test_save_and_get_trip_history(self):
        """Test saving and retrieving trip history."""
        memory = MemoryService()
        
        trip = {
            "destination": "Paris",
            "duration": 5,
            "cost": 2500
        }
        
        memory.save_trip("user_123", trip)
        history = memory.get_trip_history("user_123")
        
        assert len(history) == 1
        assert history[0]["destination"] == "Paris"


class TestErrorHandler:
    """Test error handling."""
    
    def test_handle_timeout(self):
        """Test timeout error handling."""
        response = ErrorHandler.handle_timeout("weather_agent", "get_forecast")
        
        assert response.status == "error"
        assert "Timeout" in response.error_message
    
    def test_handle_invalid_input(self):
        """Test invalid input error handling."""
        response = ErrorHandler.handle_invalid_input("weather_agent", "destination", "")
        
        assert response.status == "error"
        assert "Invalid" in response.error_message
    
    def test_handle_api_error(self):
        """Test API error handling."""
        response = ErrorHandler.handle_api_error("weather_agent", "NWS", "Connection refused")
        
        assert response.status == "error"
        assert "API error" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
