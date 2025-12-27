# Travel Planning Agent - Reference Pattern Implementation

## Overview

The Travel Planning Agent has been updated to follow the **reference pattern** from `english_assistant.py` and `teachers_assistant.py` in the `strands_multi_agent_example` directory.

## Key Improvements

### 1. @tool Decorator Pattern

**Before**:
```python
class TravelPlanner(Agent):
    def __init__(self, session_manager=None):
        super().__init__(
            model=model,
            tools=[
                self.plan_trip,
                self.get_weather_info,
                # ...
            ]
        )
    
    def plan_trip(self, ...):
        # Implementation
```

**After**:
```python
@tool
def plan_trip(destination: str, start_date: str, ...) -> dict:
    """Create a comprehensive travel plan."""
    # Implementation

@tool
def get_weather_info(destination: str, ...) -> dict:
    """Get weather information."""
    # Implementation

def create_travel_planner(session_manager=None) -> Agent:
    travel_planner = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[
            plan_trip,
            get_weather_info,
            # ...
        ]
    )
    return travel_planner
```

### 2. Factory Function Pattern

Instead of a class-based approach, we now use a factory function:

```python
def create_travel_planner(session_manager=None) -> Agent:
    """Create and return a Travel Planner agent."""
    _init_agents(session_manager)
    
    model = BedrockModel(...)
    
    travel_planner = Agent(
        model=model,
        system_prompt=system_prompt,
        session_manager=session_manager,
        tools=[plan_trip, get_weather_info, ...]
    )
    
    return travel_planner
```

### 3. Module-Level Agent Instances

Specialized agents are initialized at module level:

```python
_weather_agent = None
_flight_agent = None
# ... etc

def _init_agents(session_manager=None):
    """Initialize all specialized agents."""
    global _weather_agent, _flight_agent, ...
    
    _weather_agent = WeatherAgent(session_manager=session_manager)
    _flight_agent = FlightAgent(session_manager=session_manager)
    # ...
```

### 4. Tool Functions Access Global Agents

Each tool function accesses the global agent instances:

```python
@tool
def get_weather_info(destination: str, start_date: str, end_date: str) -> dict:
    """Get weather information from Weather Agent."""
    logger.info(f"Getting weather for {destination}")
    return _weather_agent.get_forecast(destination, start_date, end_date)
```

## Comparison with Reference Implementation

### Reference Pattern (english_assistant.py)

```python
from strands import Agent, tool

@tool
def english_assistant(query: str) -> str:
    """Process English language queries."""
    formatted_query = f"Analyze and respond to: {query}"
    
    english_agent = Agent(
        system_prompt=ENGLISH_ASSISTANT_SYSTEM_PROMPT,
        tools=[editor, file_read, file_write],
    )
    agent_response = english_agent(formatted_query)
    return str(agent_response)
```

### Our Implementation (travel_planner.py)

```python
from strands import Agent, tool

@tool
def plan_trip(destination: str, start_date: str, ...) -> dict:
    """Create a comprehensive travel plan."""
    plan = {
        "destination": destination,
        "sections": {}
    }
    
    plan["sections"]["weather"] = get_weather_info(destination, start_date, end_date)
    plan["sections"]["flights"] = search_flights("NYC", destination, start_date)
    # ...
    
    return plan

def create_travel_planner(session_manager=None) -> Agent:
    """Create and return a Travel Planner agent."""
    _init_agents(session_manager)
    
    travel_planner = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[plan_trip, get_weather_info, search_flights, ...]
    )
    
    return travel_planner
```

## Usage Pattern

### Reference Pattern (teachers_assistant.py)

```python
from strands import Agent
from english_assistant import english_assistant
from math_assistant import math_assistant

teacher_agent = Agent(
    model=bedrock_model,
    system_prompt=TEACHER_SYSTEM_PROMPT,
    tools=[english_assistant, math_assistant, ...]
)

response = teacher_agent("What is the square root of 16?")
```

### Our Implementation

```python
from travel_planner import create_travel_planner

planner = create_travel_planner()

response = planner("Plan a 5-day trip to Paris with $3000 budget")
```

## Benefits of This Pattern

### 1. Cleaner Code
- No class inheritance needed
- Functions are simpler and more focused
- Easier to understand data flow

### 2. Better Composability
- Tools can be easily added/removed
- Agents can be composed from different tools
- Flexible tool combinations

### 3. Consistent with Strands Examples
- Follows the reference implementation pattern
- Uses @tool decorator consistently
- Matches the teachers_assistant pattern

### 4. Easier Testing
- Tools can be tested independently
- No class state to manage
- Simpler mocking and patching

### 5. Better Separation of Concerns
- Tool functions are pure (mostly)
- Agent initialization is separate
- Clear responsibility boundaries

## Migration Guide

### If You Have Old Code

**Old**:
```python
from travel_planner import TravelPlanner

planner = TravelPlanner()
weather = planner.get_weather_info("Paris", "2024-06-01", "2024-06-05")
```

**New**:
```python
from travel_planner import create_travel_planner

planner = create_travel_planner()
response = planner("What's the weather in Paris from June 1-5?")
```

### Key Differences

| Aspect | Old | New |
|--------|-----|-----|
| Creation | `TravelPlanner()` | `create_travel_planner()` |
| Type | Class instance | Agent instance |
| Tool calls | Direct method calls | LLM-driven tool calls |
| Interaction | Programmatic | Natural language |

## Architecture Diagram

### Old Pattern
```
User Code
    ↓
TravelPlanner (Class)
    ├─→ self.weather_agent
    ├─→ self.flight_agent
    └─→ self.hotel_agent
```

### New Pattern
```
User Code
    ↓
create_travel_planner()
    ↓
Agent (Strands)
    ├─→ @tool plan_trip
    ├─→ @tool get_weather_info
    ├─→ @tool search_flights
    └─→ (LLM decides which tools to call)
    ↓
Global Agents
    ├─→ _weather_agent
    ├─→ _flight_agent
    └─→ _hotel_agent
```

## Tool Definitions

All tools follow this pattern:

```python
@tool
def tool_name(param1: str, param2: str, ...) -> ReturnType:
    """
    Clear description of what the tool does.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
    """
    logger.info(f"Tool called with {param1}")
    
    # Use global agent instances
    result = _specialized_agent.method(param1, param2)
    
    return result
```

## Example: Adding a New Tool

To add a new tool to the Travel Planner:

```python
@tool
def get_restaurant_recommendations(destination: str, cuisine: str) -> list:
    """Get restaurant recommendations for a destination."""
    logger.info(f"Getting {cuisine} restaurants in {destination}")
    
    # Use a specialized agent or implement directly
    return _restaurant_agent.search_restaurants(destination, cuisine)

def create_travel_planner(session_manager=None) -> Agent:
    """Create and return a Travel Planner agent."""
    _init_agents(session_manager)
    
    travel_planner = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[
            plan_trip,
            get_weather_info,
            search_flights,
            # ... existing tools ...
            get_restaurant_recommendations  # Add new tool
        ]
    )
    
    return travel_planner
```

## Testing Tools

Each tool can be tested independently:

```python
from travel_planner import get_weather_info

# Test the tool directly
result = get_weather_info("Paris", "2024-06-01", "2024-06-05")
assert result is not None
assert "daily_forecasts" in result
print("✅ Weather tool test passed")
```

## Session Management

Session management works the same way:

```python
from strands.session.s3_session_manager import S3SessionManager
from travel_planner import create_travel_planner

session_manager = S3SessionManager(
    session_id="trip_123",
    bucket="my-bucket",
    prefix="user_456"
)

planner = create_travel_planner(session_manager=session_manager)
response = planner("Plan a trip to Paris")
```

## Summary

The Travel Planning Agent now follows the **reference pattern** from the Strands examples:

✅ Uses `@tool` decorator for tool functions
✅ Uses factory function to create agents
✅ Maintains global agent instances
✅ Cleaner, more composable code
✅ Consistent with Strands framework examples
✅ Easier to test and extend

This pattern is more aligned with the Strands framework best practices and makes the code more maintainable and extensible.
