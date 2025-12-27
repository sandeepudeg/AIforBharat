# Travel Planning Agent - Quick Start Guide

## Installation

```bash
# Install dependencies
pip install strands bedrock

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

## Running the Application

### Demo Mode (Recommended for First Run)
```bash
python main.py demo
```
Demonstrates all agents with predefined travel queries.

### Interactive Mode
```bash
python main.py interactive
```
Interactive CLI for testing individual agents.

### Single Query
```bash
python main.py "Plan a trip to Paris"
```

## Programmatic Usage

### Basic Example
```python
from travel_planner import TravelPlanner

# Create planner
planner = TravelPlanner()

# Get weather
weather = planner.get_weather_info("Paris", "2024-06-01", "2024-06-05")
print(f"Weather forecast: {len(weather['daily_forecasts'])} days")

# Search flights
flights = planner.search_flights("NYC", "Paris", "2024-06-01")
print(f"Found {len(flights)} flights")

# Search hotels
hotels = planner.search_hotels("Paris", "2024-06-01", "2024-06-05")
print(f"Found {len(hotels)} hotels")

# Create complete plan
plan = planner.plan_trip("Paris", "2024-06-01", "2024-06-05", 3000)
print(f"Trip plan created with {len(plan['sections'])} sections")
```

### With Session Management
```python
from strands.session.s3_session_manager import S3SessionManager
from travel_planner import TravelPlanner

# Create session manager
session_manager = S3SessionManager(
    session_id="trip_123",
    bucket="my-bucket",
    prefix="user_456"
)

# Create planner with session
planner = TravelPlanner(session_manager=session_manager)

# Use planner (state is persisted)
weather = planner.get_weather_info("Paris", "2024-06-01", "2024-06-05")
```

## Available Agents

### 1. Weather Agent
```python
weather = planner.get_weather_info("Paris", "2024-06-01", "2024-06-05")
```

### 2. Flight Agent
```python
flights = planner.search_flights("NYC", "Paris", "2024-06-01")
```

### 3. Hotel Agent
```python
hotels = planner.search_hotels("Paris", "2024-06-01", "2024-06-05")
```

### 4. Itinerary Agent
```python
itinerary = planner.create_itinerary("Paris", "2024-06-01", "2024-06-05", 
                                     interests=["culture", "food"])
```

### 5. Budget Agent
```python
budget = planner.estimate_budget(3000, 5)  # $3000 for 5 days
```

### 6. Language Agent
```python
translation = planner.translate_text("Hello", "French")
```

### 7. Visa and Age Agent
```python
visa = planner.check_visa_requirements("USA", "France")
```

### 8. Local Transport Agent
```python
transport = planner.get_local_transport("Paris")
```

## Testing Individual Agents

### Weather Agent
```python
from agents import WeatherAgent

agent = WeatherAgent()
forecast = agent.get_forecast("Paris", "2024-06-01", "2024-06-05")
print(f"Forecast: {forecast}")
```

### Flight Agent
```python
from agents import FlightAgent

agent = FlightAgent()
flights = agent.search_flights("NYC", "Paris", "2024-06-01")
print(f"Flights: {flights}")
```

### Hotel Agent
```python
from agents import HotelAgent

agent = HotelAgent()
hotels = agent.search_hotels("Paris", "2024-06-01", "2024-06-05")
print(f"Hotels: {hotels}")
```

### Itinerary Agent
```python
from agents import ItineraryAgent

agent = ItineraryAgent()
itinerary = agent.create_itinerary("Paris", "2024-06-01", "2024-06-05")
print(f"Itinerary: {itinerary}")
```

### Budget Agent
```python
from agents import BudgetAgent

agent = BudgetAgent()
budget = agent.get_budget_breakdown(3000, 5)
print(f"Budget: {budget}")
```

### Language Agent
```python
from agents import LanguageAgent

agent = LanguageAgent()
translation = agent.translate_text("Hello", "English", "French")
print(f"Translation: {translation}")
```

### Visa and Age Agent
```python
from agents import VisaAgeAgent

agent = VisaAgeAgent()
visa = agent.check_visa_requirement("USA", "France")
print(f"Visa: {visa}")
```

### Local Transport Agent
```python
from agents import LocalTransportAgent

agent = LocalTransportAgent()
transport = agent.search_transport_options("Paris")
print(f"Transport: {transport}")
```

## Common Tasks

### Plan a Complete Trip
```python
planner = TravelPlanner()

# Create comprehensive plan
plan = planner.plan_trip(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-05",
    budget=3000,
    interests=["culture", "food"]
)

# Access different sections
weather = plan["sections"]["weather"]
flights = plan["sections"]["flights"]
hotels = plan["sections"]["hotels"]
itinerary = plan["sections"]["itinerary"]
budget = plan["sections"]["budget"]
visa = plan["sections"]["visa"]
transport = plan["sections"]["transport"]
```

### Search and Filter Flights
```python
planner = TravelPlanner()

# Search flights
flights = planner.search_flights("NYC", "Paris", "2024-06-01")

# Filter by budget (using Flight Agent directly)
from agents import FlightAgent
agent = FlightAgent()
budget_flights = agent.filter_by_budget(flights, max_price=500)
```

### Get Hotel Recommendations
```python
planner = TravelPlanner()

# Get recommendations
from agents import HotelAgent
agent = HotelAgent()
recommendations = agent.get_recommendations(
    destination="Paris",
    budget=200,
    preferences=["WiFi", "Pool", "Restaurant"]
)
```

### Create Detailed Itinerary
```python
planner = TravelPlanner()

# Create itinerary
itinerary = planner.create_itinerary(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-05",
    interests=["culture", "food", "nature"]
)

# Access daily plans
for day_plan in itinerary["daily_itinerary"]:
    print(f"Day {day_plan['day']}: {day_plan['morning']['activity']}")
```

### Check Travel Eligibility
```python
planner = TravelPlanner()

# Check visa
visa = planner.check_visa_requirements("USA", "India")
print(f"Visa required: {visa['visa_required']}")

# Check age restrictions
from agents import VisaAgeAgent
agent = VisaAgeAgent()
eligible = agent.check_age_restriction("Bungee Jumping", age=25)
print(f"Eligible: {eligible['eligible']}")
```

## Troubleshooting

### AWS Credentials Error
```
Error: Unable to locate credentials
```
Solution: Set AWS environment variables
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### Bedrock Model Error
```
Error: Model not found
```
Solution: Ensure model is available in your region
```python
model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
```

### S3 Session Error
```
Error: Bucket not found
```
Solution: Create S3 bucket or disable session management
```python
planner = TravelPlanner()  # No session manager
```

## Documentation

- **STRANDS_IMPLEMENTATION.md** - Detailed implementation guide
- **REFACTORING_SUMMARY.md** - Summary of changes
- **STRANDS_REFACTORING_COMPLETE.md** - Complete refactoring details
- **main.py** - Usage examples and CLI interface

## Next Steps

1. Run demo: `python main.py demo`
2. Try interactive mode: `python main.py interactive`
3. Integrate into your application
4. Extend with real APIs
5. Deploy to production

## Support

For issues or questions:
1. Check documentation files
2. Review example code in main.py
3. Test individual agents
4. Check AWS credentials and region
