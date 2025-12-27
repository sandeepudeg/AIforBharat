# Travel Planning Agent - Exact Pattern Match with english_assistant.py

## ✅ Pattern Confirmation

The Travel Planner now follows the **exact pattern** from `english_assistant.py`.

## Pattern Breakdown

### english_assistant.py Pattern

```python
from strands import Agent, tool

ENGLISH_ASSISTANT_SYSTEM_PROMPT = """..."""

@tool
def english_assistant(query: str) -> str:
    """Process and respond to English language queries."""
    formatted_query = f"Analyze and respond to: {query}"
    
    try:
        print("Routed to English Assistant")
        
        english_agent = Agent(
            system_prompt=ENGLISH_ASSISTANT_SYSTEM_PROMPT,
            tools=[editor, file_read, file_write],
        )
        agent_response = english_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your question..."
    except Exception as e:
        return f"Error processing your query: {str(e)}"
```

### Our Implementation Pattern

```python
from strands import Agent, tool

WEATHER_SYSTEM_PROMPT = """..."""
FLIGHT_SYSTEM_PROMPT = """..."""
# ... more system prompts ...

@tool
def weather_assistant(query: str) -> str:
    """Process and respond to weather-related travel queries."""
    formatted_query = f"Analyze and respond to this travel weather question: {query}"
    
    try:
        logger.info("Routed to Weather Assistant")
        
        weather_agent = Agent(
            system_prompt=WEATHER_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = weather_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your weather question..."
    except Exception as e:
        return f"Error processing your weather query: {str(e)}"

@tool
def flight_assistant(query: str) -> str:
    """Process and respond to flight-related travel queries."""
    # Same pattern as weather_assistant
    ...

@tool
def hotel_assistant(query: str) -> str:
    """Process and respond to hotel-related travel queries."""
    # Same pattern as weather_assistant
    ...

# ... 5 more assistant tools ...

def create_travel_planner(session_manager=None) -> Agent:
    """Create and return a Travel Planner agent."""
    model = BedrockModel(...)
    
    travel_planner = Agent(
        model=model,
        system_prompt=TRAVEL_PLANNER_SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=[
            weather_assistant,
            flight_assistant,
            hotel_assistant,
            itinerary_assistant,
            budget_assistant,
            language_assistant,
            visa_age_assistant,
            transport_assistant
        ]
    )
    
    return travel_planner
```

## Key Pattern Elements

### 1. System Prompts
✅ Defined at module level
```python
WEATHER_SYSTEM_PROMPT = """..."""
FLIGHT_SYSTEM_PROMPT = """..."""
# ... etc
```

### 2. @tool Decorator
✅ Each assistant is a @tool decorated function
```python
@tool
def weather_assistant(query: str) -> str:
    ...

@tool
def flight_assistant(query: str) -> str:
    ...
```

### 3. Function Signature
✅ Takes query string, returns string
```python
def weather_assistant(query: str) -> str:
```

### 4. Query Formatting
✅ Formats the query with context
```python
formatted_query = f"Analyze and respond to this travel weather question: {query}"
```

### 5. Agent Creation Inside Tool
✅ Creates Agent inside the tool function
```python
weather_agent = Agent(
    system_prompt=WEATHER_SYSTEM_PROMPT,
    tools=[],
)
```

### 6. Agent Invocation
✅ Calls agent with formatted query
```python
agent_response = weather_agent(formatted_query)
```

### 7. Response Handling
✅ Converts to string and checks length
```python
text_response = str(agent_response)

if len(text_response) > 0:
    return text_response

return "I apologize, but I couldn't properly analyze..."
```

### 8. Error Handling
✅ Catches exceptions and returns error message
```python
except Exception as e:
    return f"Error processing your weather query: {str(e)}"
```

### 9. Factory Function
✅ Creates main orchestrator agent
```python
def create_travel_planner(session_manager=None) -> Agent:
    travel_planner = Agent(
        model=model,
        system_prompt=TRAVEL_PLANNER_SYSTEM_PROMPT,
        tools=[
            weather_assistant,
            flight_assistant,
            # ... all assistant tools
        ]
    )
    return travel_planner
```

## Comparison Table

| Element | english_assistant.py | Travel Planner |
|---------|----------------------|----------------|
| System Prompt | ✅ Module level | ✅ Module level (8 prompts) |
| @tool Decorator | ✅ 1 tool | ✅ 8 tools |
| Function Signature | ✅ `(query: str) -> str` | ✅ `(query: str) -> str` |
| Query Formatting | ✅ Yes | ✅ Yes |
| Agent Creation | ✅ Inside tool | ✅ Inside tool |
| Agent Invocation | ✅ `agent(formatted_query)` | ✅ `agent(formatted_query)` |
| Response Handling | ✅ Convert to string | ✅ Convert to string |
| Error Handling | ✅ Try/except | ✅ Try/except |
| Factory Function | ✅ Implicit | ✅ Explicit `create_travel_planner()` |

## Usage Pattern

### english_assistant.py Usage
```python
from teachers_assistant import teacher_agent

response = teacher_agent("What is grammar?")
```

### Travel Planner Usage
```python
from travel_planner import create_travel_planner

planner = create_travel_planner()
response = planner("What's the weather in Paris?")
```

## How It Works

### Flow Diagram

```
User Query
    ↓
create_travel_planner()
    ↓
Travel Planner Agent (Strands)
    ├─→ Analyzes query
    ├─→ Decides which tool to call
    │   (weather_assistant, flight_assistant, etc.)
    ↓
Selected Tool (@tool decorated function)
    ├─→ Formats query with context
    ├─→ Creates specialized Agent
    ├─→ Calls agent with formatted query
    ├─→ Gets response from LLM
    ├─→ Converts to string
    ├─→ Returns response
    ↓
Travel Planner Agent
    ├─→ Receives response from tool
    ├─→ May call other tools
    ├─→ Synthesizes final response
    ↓
User Response
```

## 8 Specialized Assistants

1. **weather_assistant** - Weather and climate queries
2. **flight_assistant** - Flight and booking queries
3. **hotel_assistant** - Hotel and accommodation queries
4. **itinerary_assistant** - Itinerary and activity queries
5. **budget_assistant** - Budget and cost queries
6. **language_assistant** - Language and translation queries
7. **visa_age_assistant** - Visa and age restriction queries
8. **transport_assistant** - Transport and logistics queries

Each follows the exact same pattern as `english_assistant.py`.

## Key Advantages of This Pattern

### 1. Separation of Concerns
- Each tool is independent
- Each tool has its own system prompt
- Each tool creates its own agent

### 2. Scalability
- Easy to add new assistants
- Just add a new @tool function
- Add to tools list in create_travel_planner()

### 3. Flexibility
- Each assistant can have different tools
- Each assistant can have different system prompt
- Each assistant can have different behavior

### 4. Clarity
- Clear what each tool does
- Clear error handling
- Clear response format

### 5. Consistency
- Follows Strands framework pattern
- Matches reference implementation
- Proven pattern from examples

## Example: Adding a New Assistant

To add a new assistant (e.g., restaurant recommendations):

```python
RESTAURANT_SYSTEM_PROMPT = """You are a restaurant expert..."""

@tool
def restaurant_assistant(query: str) -> str:
    """Process and respond to restaurant-related queries."""
    formatted_query = f"Analyze and respond to this restaurant question: {query}"
    
    try:
        logger.info("Routed to Restaurant Assistant")
        
        restaurant_agent = Agent(
            system_prompt=RESTAURANT_SYSTEM_PROMPT,
            tools=[],
        )
        agent_response = restaurant_agent(formatted_query)
        text_response = str(agent_response)
        
        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your restaurant question..."
    except Exception as e:
        return f"Error processing your restaurant query: {str(e)}"

def create_travel_planner(session_manager=None) -> Agent:
    """Create and return a Travel Planner agent."""
    travel_planner = Agent(
        model=model,
        system_prompt=TRAVEL_PLANNER_SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=[
            weather_assistant,
            flight_assistant,
            hotel_assistant,
            itinerary_assistant,
            budget_assistant,
            language_assistant,
            visa_age_assistant,
            transport_assistant,
            restaurant_assistant  # Add new tool
        ]
    )
    
    return travel_planner
```

## Summary

✅ **Exact Pattern Match Confirmed**

The Travel Planning Agent now follows the **exact pattern** from `english_assistant.py`:

- ✅ Module-level system prompts
- ✅ @tool decorated functions
- ✅ Query formatting with context
- ✅ Agent creation inside tool
- ✅ Agent invocation with formatted query
- ✅ String response handling
- ✅ Error handling with try/except
- ✅ Factory function for orchestrator
- ✅ 8 specialized assistants
- ✅ Scalable and extensible design

This is the **correct Strands framework pattern** for multi-agent systems.

---

**Pattern Source**: `strands_multi_agent_example/english_assistant.py`
**Implementation**: `strands_travel_planning_agent/travel_planner.py`
**Status**: ✅ Exact Match
