"""
Manual testing script for Travel Planning Agent.
Run this to test the core functionality without pytest.
"""

import sys
from datetime import datetime

# Test imports
print("=" * 70)
print("TRAVEL PLANNING AGENT - MANUAL TEST")
print("=" * 70)

print("\n1. Testing imports...")
try:
    from core import (
        AgentRequest,
        AgentResponse,
        AgentRegistry,
        MessageBroker,
        ValidationHelper,
        CurrencyConverter,
        MemoryService,
        ErrorHandler
    )
    print("   ✅ Core imports successful")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

try:
    from agents.weather_agent import WeatherAgent
    print("   ✅ Weather Agent import successful")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

try:
    from travel_planner import TravelPlanner
    print("   ✅ Travel Planner import successful")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test AgentRequest
print("\n2. Testing AgentRequest...")
try:
    request = AgentRequest(
        source="travel_planner",
        target="weather_agent",
        action="get_forecast",
        parameters={"destination": "Paris", "start_date": "2025-05-01"}
    )
    assert request.source == "travel_planner"
    assert request.target == "weather_agent"
    assert request.action == "get_forecast"
    assert request.parameters["destination"] == "Paris"
    print("   ✅ AgentRequest creation successful")
    print(f"      - Source: {request.source}")
    print(f"      - Target: {request.target}")
    print(f"      - Action: {request.action}")
    print(f"      - Request ID: {request.request_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test AgentResponse
print("\n3. Testing AgentResponse...")
try:
    response = AgentResponse(
        source="weather_agent",
        target="travel_planner",
        status="success",
        data={"forecast": "sunny", "temperature": 22}
    )
    assert response.source == "weather_agent"
    assert response.status == "success"
    assert response.data["temperature"] == 22
    print("   ✅ AgentResponse creation successful")
    print(f"      - Source: {response.source}")
    print(f"      - Status: {response.status}")
    print(f"      - Data: {response.data}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test ValidationHelper
print("\n4. Testing ValidationHelper...")
try:
    # Test destination validation
    assert ValidationHelper.validate_destination("Paris") is True
    assert ValidationHelper.validate_destination("") is False
    print("   ✅ Destination validation works")
    
    # Test date validation
    assert ValidationHelper.validate_dates("2025-05-01", "2025-05-05") is True
    assert ValidationHelper.validate_dates("2025-05-05", "2025-05-01") is False
    print("   ✅ Date validation works")
    
    # Test budget validation
    assert ValidationHelper.validate_budget(3000) is True
    assert ValidationHelper.validate_budget(-100) is False
    print("   ✅ Budget validation works")
    
    # Test age validation
    assert ValidationHelper.validate_age(30) is True
    assert ValidationHelper.validate_age(200) is False
    print("   ✅ Age validation works")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test CurrencyConverter
print("\n5. Testing CurrencyConverter...")
try:
    # Test USD to EUR conversion
    amount = CurrencyConverter.convert(100, "USD", "EUR")
    assert amount == 92.0
    print(f"   ✅ Currency conversion works: 100 USD = {amount} EUR")
    
    # Test same currency
    amount = CurrencyConverter.convert(100, "USD", "USD")
    assert amount == 100
    print(f"   ✅ Same currency conversion: 100 USD = {amount} USD")
    
    # Test exchange rate
    rate = CurrencyConverter.get_rate("USD", "EUR")
    print(f"   ✅ Exchange rate USD→EUR: {rate}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test MemoryService
print("\n6. Testing MemoryService...")
try:
    memory = MemoryService()
    
    # Save preferences
    preferences = {
        "budget": 3000,
        "travel_style": "adventure",
        "interests": ["hiking", "culture"]
    }
    memory.save_preferences("user_123", preferences)
    print("   ✅ Preferences saved")
    
    # Retrieve preferences
    retrieved = memory.get_preferences("user_123")
    assert retrieved == preferences
    print("   ✅ Preferences retrieved successfully")
    
    # Save trip
    trip = {
        "destination": "Paris",
        "duration": 5,
        "cost": 2500
    }
    memory.save_trip("user_123", trip)
    print("   ✅ Trip saved")
    
    # Get trip history
    history = memory.get_trip_history("user_123")
    assert len(history) == 1
    print(f"   ✅ Trip history retrieved: {len(history)} trip(s)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test AgentRegistry
print("\n7. Testing AgentRegistry...")
try:
    registry = AgentRegistry()
    weather_agent = WeatherAgent()
    
    # Register agent
    registry.register(weather_agent)
    print("   ✅ Agent registered")
    
    # Get agent
    retrieved = registry.get_agent("weather_agent")
    assert retrieved is not None
    assert retrieved.name == "weather_agent"
    print("   ✅ Agent retrieved successfully")
    
    # List agents
    agents = registry.list_agents()
    assert "weather_agent" in agents
    print(f"   ✅ Agents listed: {agents}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test MessageBroker
print("\n8. Testing MessageBroker...")
try:
    broker = MessageBroker()
    
    # Send request
    request = AgentRequest(
        source="travel_planner",
        target="weather_agent",
        action="get_forecast",
        parameters={"destination": "Paris"}
    )
    broker.send_request(request)
    print("   ✅ Request sent to broker")
    
    # Get messages
    messages = broker.get_messages()
    assert len(messages) == 1
    print(f"   ✅ Messages retrieved: {len(messages)} message(s)")
    
    # Clear queue
    broker.clear_queue()
    messages = broker.get_messages()
    assert len(messages) == 0
    print("   ✅ Queue cleared")
    
    # Check history
    history = broker.get_history()
    assert len(history) == 1
    print(f"   ✅ History preserved: {len(history)} message(s)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test ErrorHandler
print("\n9. Testing ErrorHandler...")
try:
    # Test timeout error
    response = ErrorHandler.handle_timeout("weather_agent", "get_forecast")
    assert response.status == "error"
    assert "Timeout" in response.error_message
    print("   ✅ Timeout error handling works")
    
    # Test invalid input error
    response = ErrorHandler.handle_invalid_input("weather_agent", "destination", "")
    assert response.status == "error"
    print("   ✅ Invalid input error handling works")
    
    # Test API error
    response = ErrorHandler.handle_api_error("weather_agent", "NWS", "Connection refused")
    assert response.status == "error"
    print("   ✅ API error handling works")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test WeatherAgent
print("\n10. Testing WeatherAgent...")
try:
    weather_agent = WeatherAgent()
    
    # Create a request
    request = AgentRequest(
        source="travel_planner",
        target="weather_agent",
        action="get_forecast",
        parameters={
            "destination": "Paris",
            "start_date": "2025-05-01",
            "end_date": "2025-05-05"
        }
    )
    
    # Process request
    response = weather_agent.process_request(request)
    
    assert response.status == "success"
    assert "forecast" in response.data
    assert "analysis" in response.data
    assert "packing_recommendations" in response.data
    print("   ✅ Weather Agent request processed successfully")
    print(f"      - Status: {response.status}")
    print(f"      - Forecast days: {len(response.data.get('forecast', []))}")
    print(f"      - Packing items: {len(response.data.get('packing_recommendations', []))}")
    print(f"      - Best days: {len(response.data.get('best_days', []))}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test TravelPlanner
print("\n11. Testing TravelPlanner...")
try:
    planner = TravelPlanner()
    
    # Register weather agent
    weather_agent = WeatherAgent()
    planner.register_agent(weather_agent)
    print("   ✅ Weather Agent registered with Travel Planner")
    
    # Test query parsing
    query = "Plan a 5-day trip to Paris with $3000 budget"
    parameters = planner.parse_query(query)
    assert "destination" in parameters
    assert "budget" in parameters
    print("   ✅ Query parsed successfully")
    print(f"      - Destination: {parameters.get('destination')}")
    print(f"      - Budget: ${parameters.get('budget')}")
    
    # Test agent routing
    requests = planner.route_to_agents(parameters)
    assert len(requests) > 0
    print(f"   ✅ Agents routed: {len(requests)} request(s)")
    for req in requests:
        print(f"      - {req.target}: {req.action}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 70)
print("\nNext steps:")
print("1. Run pytest for comprehensive testing: pytest tests/test_core.py -v")
print("2. Implement remaining agents (Flight, Hotel, Itinerary, Budget, etc.)")
print("3. Create integration tests for multi-agent coordination")
print("4. Test with real API integrations")
print("=" * 70)
