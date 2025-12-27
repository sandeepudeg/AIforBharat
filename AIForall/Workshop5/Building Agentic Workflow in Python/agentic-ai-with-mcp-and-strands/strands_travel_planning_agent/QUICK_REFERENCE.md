# Travel Planning Agent - Quick Reference Guide

## How Agents Communicate - Visual Summary

### The Hub-and-Spoke Model

```
                    ┌─────────────────────┐
                    │  TRAVEL_PLANNER     │
                    │   (Central Hub)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────┐            ┌─────────┐          ┌─────────┐
   │ Weather │            │ Flight  │          │  Hotel  │
   │ Agent   │            │ Agent   │          │ Agent   │
   └─────────┘            └─────────┘          └─────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  EXTERNAL APIs      │
                    │  (Weather, Flights, │
                    │   Hotels, Maps)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────┐            ┌─────────┐          ┌─────────┐
   │ Budget  │            │  Visa   │          │ Local   │
   │ Agent   │            │ & Age   │          │Transport│
   │         │            │ Agent   │          │ Agent   │
   └─────────┘            └─────────┘          └─────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  TRAVEL_PLANNER     │
                    │  (Aggregator)       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  COMPLETE TRIP PLAN  │
                    │  (All Details)       │
                    └──────────────────────┘
```

---

## Agent Responsibilities at a Glance

| Agent | Input | Process | Output |
|-------|-------|---------|--------|
| **Weather_Agent** | Destination, dates | Call NWS API, analyze forecast | Weather forecast, packing tips |
| **Flight_Agent** | Origin, destination, dates, budget | Search flights, filter, sort | Flight options, prices, links |
| **Hotel_Agent** | Destination, dates, budget | Search hotels, filter, rate | Hotel options, amenities, ratings |
| **Itinerary_Agent** | Destination, duration, interests | Generate activities, calculate times | Day-by-day plan, attractions |
| **Budget_Agent** | All costs, currencies | Calculate breakdown, convert | Budget analysis, suggestions |
| **Visa_and_Age_Agent** | Origin, destination, age, activities | Check requirements, filter | Visa info, age restrictions |
| **Local_Transport_Agent** | Airport, hotel, preferences | Suggest transport options | Transport options, costs, times |
| **Language_Agent** | Text, target language | Translate content | Translated text, local phrases |

---

## Communication Patterns

### Pattern 1: Simple Query (Weather Only)
```
User: "What's the weather in Paris?"
    ↓
Travel_Planner → Weather_Agent
    ↓
Weather_Agent → NWS API
    ↓
Response: Forecast
    ↓
Time: ~2-3 seconds
```

### Pattern 2: Complete Trip Planning
```
User: "Plan a 5-day trip to Paris with $3000 budget"
    ↓
Travel_Planner routes to ALL agents (parallel):
    ├→ Weather_Agent
    ├→ Flight_Agent
    ├→ Hotel_Agent
    ├→ Itinerary_Agent
    └→ (wait for all)
    ↓
Travel_Planner routes to coordination agents:
    ├→ Budget_Agent (analyze costs)
    ├→ Visa_and_Age_Agent (check requirements)
    └→ Local_Transport_Agent (suggest transport)
    ↓
Travel_Planner aggregates all responses
    ↓
Response: Complete trip plan
    ↓
Time: ~5-8 seconds
```

### Pattern 3: Follow-Up Question
```
User: "Can you find cheaper hotels?"
    ↓
Travel_Planner → Hotel_Agent (with lower budget)
    ↓
Hotel_Agent → Hotel API
    ↓
Travel_Planner → Budget_Agent (recalculate)
    ↓
Response: Alternative hotels with new budget
    ↓
Time: ~3-5 seconds
```

---

## Message Flow Example

### Step 1: User Query
```
"Plan a 5-day trip to Paris with $3000 budget"
```

### Step 2: Travel_Planner Parses
```
destination: "Paris"
duration: 5 days
budget: $3000
interests: [inferred from context]
```

### Step 3: Travel_Planner Routes (Parallel)
```
→ Weather_Agent: "Get forecast for Paris, May 1-5"
→ Flight_Agent: "Search flights NYC→Paris, May 1-5, budget $1000"
→ Hotel_Agent: "Find hotels in Paris, May 1-5, budget $1200"
→ Itinerary_Agent: "Create 5-day itinerary for Paris"
```

### Step 4: Agents Call APIs
```
Weather_Agent → NWS API → Forecast data
Flight_Agent → Skyscanner API → Flight options
Hotel_Agent → Booking.com API → Hotel options
Itinerary_Agent → Google Maps + TripAdvisor → Activities
```

### Step 5: Agents Return Results
```
Weather_Agent: "Sunny, 22°C, perfect weather"
Flight_Agent: "3 options, cheapest $650"
Hotel_Agent: "5 options, best rated $1120"
Itinerary_Agent: "25 activities planned"
```

### Step 6: Travel_Planner Coordinates
```
→ Budget_Agent: "Analyze $650 + $1120 + activities"
→ Visa_and_Age_Agent: "Check USA→France requirements"
→ Local_Transport_Agent: "Suggest CDG→Hotel transport"
```

### Step 7: Coordination Agents Return
```
Budget_Agent: "Total $2280, remaining $720"
Visa_and_Age_Agent: "No visa needed, all activities OK"
Local_Transport_Agent: "Public transit $12, taxi $55"
```

### Step 8: Travel_Planner Aggregates
```
Combines all responses into complete trip plan:
✓ Weather forecast
✓ Flight options
✓ Hotel recommendations
✓ Day-by-day itinerary
✓ Budget breakdown
✓ Visa info
✓ Transport options
✓ Booking links
```

### Step 9: User Receives
```
Complete trip plan with all details, costs, and links
```

---

## Agent Communication Methods

### 1. Direct Method Calls
```python
# Travel_Planner calls Weather_Agent directly
weather_data = weather_agent.get_forecast(
    destination="Paris",
    start_date="2025-05-01",
    end_date="2025-05-05"
)
```

### 2. Tool-Based API Calls
```python
# Agents use http_request tool to call external APIs
response = http_request(
    method="GET",
    url="https://api.weather.gov/points/48.8566,2.3522"
)
```

### 3. Message Passing
```python
# Agents communicate via structured messages
message = {
    "type": "agent_request",
    "source": "travel_planner",
    "target": "budget_agent",
    "action": "analyze_budget",
    "parameters": {...}
}
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INPUT                             │
│              "Plan a trip to Paris"                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TRAVEL_PLANNER                             │
│  Parse → Extract → Route → Coordinate → Aggregate          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐     ┌─────────┐
   │ Weather │      │ Flight  │     │ Hotel   │
   │ Results │      │ Results │     │ Results │
   └────┬────┘      └────┬────┘     └────┬────┘
        │                │               │
        └────────────────┼───────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Budget + Visa + Transport     │
        │  Analysis & Coordination       │
        └────────────────────┬───────────┘
                             │
                             ▼
        ┌────────────────────────────────┐
        │  COMPLETE TRIP PLAN            │
        │  (All details, costs, links)   │
        └────────────────────┬───────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      USER OUTPUT                            │
│              Complete trip plan with all details            │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features of Communication

### ✅ Parallel Execution
- Multiple agents work simultaneously
- Reduces total response time
- Efficient resource usage

### ✅ Sequential Coordination
- Budget_Agent waits for other agents
- Visa_and_Age_Agent filters based on itinerary
- Local_Transport_Agent uses hotel location

### ✅ Error Handling
- Timeouts with retries
- Fallback suggestions
- Graceful degradation

### ✅ Currency Conversion
- Automatic exchange rate lookup
- Dual-currency display
- Accurate cost calculations

### ✅ Visa & Age Checking
- Automatic requirement lookup
- Activity filtering
- Document checklists

### ✅ Calendar Integration
- Event creation
- Conflict detection
- Export to Google Calendar/iCal

### ✅ Local Transportation
- Multiple options (taxi, transit, ride-share)
- Cost and time estimates
- Step-by-step directions

### ✅ Memory Persistence
- Stores user preferences
- Remembers past trips
- Personalizes recommendations

---

## Response Times

| Query Type | Agents Used | Time |
|-----------|------------|------|
| Weather only | 1 | 2-3 sec |
| Flights only | 1 | 2-3 sec |
| Hotels only | 1 | 2-3 sec |
| Weather + Flights | 2 | 3-4 sec |
| Complete trip | 8 | 5-8 sec |
| Follow-up question | 2-3 | 3-5 sec |

---

## Error Scenarios & Handling

### Scenario 1: API Timeout
```
Flight_Agent → Skyscanner API (timeout)
    ↓
Retry 3 times with exponential backoff
    ↓
If still fails:
    Return fallback: "Try manual search at [link]"
    Continue with other agents
```

### Scenario 2: Budget Exceeded
```
Budget_Agent detects: $3300 > $3000 budget
    ↓
Alert user: "Budget exceeded by $300"
    ↓
Suggest alternatives:
    - Cheaper hotel (saves $300)
    - Budget airline (saves $300)
```

### Scenario 3: Visa Required
```
Visa_and_Age_Agent checks: USA → India
    ↓
Visa required: YES
    ↓
Return:
    - Visa type: Tourist
    - Processing: 5-7 days
    - Cost: $100
    - Documents: [list]
    - Link: [application URL]
```

---

## Summary

The Travel Planning Agent communicates through:

1. **Central Hub** (Travel_Planner) coordinates all agents
2. **Parallel Execution** for independent queries
3. **Sequential Coordination** for dependent queries
4. **External APIs** for real-time data
5. **Memory Service** for personalization
6. **Structured Messages** for agent communication
7. **Error Handling** with fallbacks
8. **Real-Time Monitoring** for alerts

**Result**: Complete, personalized trip plans in 5-8 seconds with all necessary details, costs, and booking links.
