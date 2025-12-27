# Travel Planning Agent - Strands Framework Implementation

## Overview

This is a complete refactoring of the Travel Planning Agent to use the **Strands Agent Framework** with **Bedrock models** for LLM-powered reasoning and decision-making.

## Architecture

### Hub-and-Spoke Pattern with Strands

```
┌─────────────────────────────────────────────────────────────┐
│                    Travel Planner (Hub)                     │
│                   Strands Agent with Tools                  │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Weather │  │ Flight  │  │ Hotel   │  │Itinerary│
    │ Agent   │  │ Agent   │  │ Agent   │  │ Agent   │
    └─────────┘  └─────────┘  └─────────┘  └─────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Budget  │  │Language │  │ Visa/Age│  │Transport│
    │ Agent   │  │ Agent   │  │ Agent   │  │ Agent   │
    └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

## Key Components

### 1. Travel Planner (Orchestrator)

**File**: `travel_planner.py`

```python
class TravelPlanner(Agent):
    """Central orchestrator using Strands framework."""
    
    def __init__(self, session_manager=None):
        # Initialize with Bedrock model
        model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
        
        # Define tools for LLM to call
        super().__init__(
            model=model,
            system_prompt="...",
            tools=[
                self.plan_trip,
                self.get_weather_info,
                self.search_flights,
                # ... more tools
            ]
        )
        
        # Initialize all specialized agents
        self.weather_agent = WeatherAgent()
        self.flight_agent = FlightAgent()
        # ... more agents
```

**Responsibilities**:
- Orchestrates all specialized agents
- Provides tools for LLM to call
- Aggregates responses from multiple agents
- Creates comprehensive travel plans

### 2. Specialized Agents

Each agent inherits from `strands.Agent` and implements domain-specific tools:

#### Weather Agent (`agents/weather_agent.py`)
```python
class WeatherAgent(Agent):
    def __init__(self, session_manager=None):
        super().__init__(
            model=BedrockModel(...),
            system_prompt="You are a weather expert...",
            tools=[
                self.get_forecast,
                self.analyze_weather,
                self.get_packing_recommendations,
                self.identify_best_days
            ]
        )
```

**Tools**:
- `get_forecast(destination, start_date, end_date)` - Get weather forecast
- `analyze_weather(destination, start_date, end_date)` - Analyze patterns
- `get_packing_recommendations(destination, start_date, end_date)` - Packing tips
- `identify_best_days(destination, start_date, end_date)` - Best travel days

#### Flight Agent (`agents/flight_agent.py`)
**Tools**:
- `search_flights(origin, destination, date)` - Search available flights
- `filter_by_budget(flights, max_price)` - Filter by budget
- `compare_flights(flights)` - Compare options
- `find_round_trip(origin, destination, departure_date, return_date)` - Round-trip search

#### Hotel Agent (`agents/hotel_agent.py`)
**Tools**:
- `search_hotels(destination, check_in, check_out)` - Search hotels
- `filter_by_budget(hotels, max_price_per_night)` - Budget filter
- `filter_by_amenities(hotels, required_amenities)` - Amenity filter
- `get_recommendations(destination, budget, preferences)` - Recommendations

#### Itinerary Agent (`agents/itinerary_agent.py`)
**Tools**:
- `create_itinerary(destination, start_date, end_date, interests)` - Create day-by-day plan
- `get_attractions(destination, interests)` - Get attractions
- `suggest_meals(destination, day)` - Meal suggestions
- `calculate_travel_time(origin, destination, transport_mode)` - Travel time

#### Budget Agent (`agents/budget_agent.py`)
**Tools**:
- `calculate_total_cost(...)` - Calculate total trip cost
- `get_budget_breakdown(total_budget, trip_days)` - Budget allocation
- `convert_currency(amount, from_currency, to_currency)` - Currency conversion
- `get_cost_saving_tips(destination, trip_type)` - Money-saving tips

#### Language Agent (`agents/language_agent.py`)
**Tools**:
- `translate_text(text, source_language, target_language)` - Translate text
- `get_common_phrases(destination, language)` - Common phrases
- `get_language_guide(destination)` - Language guide
- `get_pronunciation(phrase, language)` - Pronunciation help

#### Visa and Age Agent (`agents/visa_age_agent.py`)
**Tools**:
- `check_visa_requirement(origin_country, destination_country)` - Visa check
- `check_age_restriction(activity, age)` - Age restriction check
- `filter_activities_by_age(activities, age)` - Filter activities
- `get_visa_application_info(destination_country)` - Visa application details

#### Local Transport Agent (`agents/local_transport_agent.py`)
**Tools**:
- `search_transport_options(destination, route_type)` - Transport options
- `get_airport_transfer(destination, passengers)` - Airport transfers
- `estimate_travel_cost(origin, destination, transport_mode, distance_km)` - Cost estimate
- `rate_convenience(transport_mode)` - Convenience rating

## How It Works

### 1. User Query

```python
planner = TravelPlanner()
result = planner("Plan a 5-day trip to Paris with a $3000 budget")
```

### 2. LLM Processing

The Bedrock model receives the query and:
1. Analyzes the request
2. Determines which agents are needed
3. Calls appropriate tools (agent methods)
4. Synthesizes responses into a comprehensive plan

### 3. Agent Coordination

```
User Query
    ↓
Travel Planner (LLM)
    ├─→ Calls: get_weather_info("Paris", ...)
    │   └─→ Weather Agent returns forecast
    ├─→ Calls: search_flights("NYC", "Paris", ...)
    │   └─→ Flight Agent returns options
    ├─→ Calls: search_hotels("Paris", ...)
    │   └─→ Hotel Agent returns options
    ├─→ Calls: create_itinerary("Paris", ...)
    │   └─→ Itinerary Agent returns day-by-day plan
    └─→ Synthesizes all data into final plan
```

### 4. Response

The LLM returns a comprehensive travel plan with:
- Weather forecast and packing recommendations
- Flight options with comparisons
- Hotel recommendations
- Day-by-day itinerary
- Budget breakdown
- Visa requirements
- Local transportation options
- Language tips

## Session Management

All agents support S3-based session persistence:

```python
from strands.session.s3_session_manager import S3SessionManager

session_manager = S3SessionManager(
    session_id="travel_session_123",
    bucket="my-bucket",
    prefix="user_123"
)

planner = TravelPlanner(session_manager=session_manager)
```

This enables:
- Persistent conversation history
- User preference tracking
- Multi-session support
- Distributed deployment

## Differences from Previous Implementation

### Previous (Custom BaseAgent)
```python
class WeatherAgent(BaseAgent):
    def process_request(self, request: AgentRequest) -> AgentResponse:
        # Manual request/response handling
        return self._create_response(...)
```

### Current (Strands Framework)
```python
class WeatherAgent(Agent):
    def __init__(self, session_manager=None):
        super().__init__(
            model=BedrockModel(...),
            tools=[self.get_forecast, ...]
        )
    
    def get_forecast(self, destination, start_date, end_date):
        # LLM calls this tool directly
        return forecast_data
```

## Key Advantages

1. **LLM-Powered Reasoning**: Bedrock models make intelligent decisions
2. **Automatic Tool Calling**: LLM decides which tools to use
3. **Session Persistence**: S3-based state management
4. **Scalability**: Works across distributed systems
5. **Framework Integration**: Leverages Strands ecosystem
6. **Natural Language**: Users interact in natural language
7. **Multi-Agent Coordination**: Automatic agent orchestration

## Usage Examples

### Demo Mode
```bash
python main.py demo
```

### Interactive Mode
```bash
python main.py interactive
```

### Single Query
```bash
python main.py "Plan a trip to Tokyo"
```

### Programmatic Usage
```python
from travel_planner import TravelPlanner

planner = TravelPlanner()

# Get weather
weather = planner.get_weather_info("Paris", "2024-06-01", "2024-06-05")

# Search flights
flights = planner.search_flights("NYC", "Paris", "2024-06-01")

# Create complete plan
plan = planner.plan_trip("Paris", "2024-06-01", "2024-06-05", 3000)
```

## Configuration

### Environment Variables

```bash
# AWS Credentials (for Bedrock)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# S3 Session Storage (optional)
export STRANDS_BUCKET_NAME=your-bucket-name
```

### Model Configuration

Edit `travel_planner.py` to change the model:

```python
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",  # Change model here
    temperature=0.3  # Adjust creativity (0-1)
)
```

## Testing

Each agent can be tested independently:

```python
from agents import WeatherAgent

agent = WeatherAgent()
forecast = agent.get_forecast("Paris", "2024-06-01", "2024-06-05")
print(forecast)
```

## Future Enhancements

1. **Real API Integration**: Replace mock data with real APIs
2. **Advanced Reasoning**: Use multi-step reasoning for complex queries
3. **User Preferences**: Learn and remember user preferences
4. **Real-time Updates**: Live flight and weather updates
5. **Payment Integration**: Direct booking capabilities
6. **Mobile App**: Mobile interface for travel planning
7. **Collaborative Planning**: Multi-user trip planning

## References

- [Strands Agent Framework](https://docs.strands.ai)
- [Bedrock Models](https://docs.aws.amazon.com/bedrock/)
- [S3 Session Manager](https://docs.strands.ai/session-management)
