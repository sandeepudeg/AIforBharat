# Travel Planning Agent - Communication Architecture

## System Overview

The Travel Planning Agent uses a **hub-and-spoke architecture** where the Travel_Planner acts as the central orchestrator, coordinating 8 specialized agents to handle different aspects of travel planning.

---

## Communication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                 │
│                    (CLI / Streamlit / Chat / API)                           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ User Query
                                     │ "Plan a 5-day trip to Paris"
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRAVEL_PLANNER (Hub)                                │
│                                                                             │
│  1. Parse user query                                                        │
│  2. Extract parameters (destination, dates, budget, interests, age)         │
│  3. Determine required agents                                               │
│  4. Route to specialized agents (parallel or sequential)                    │
│  5. Aggregate responses                                                     │
│  6. Coordinate with Budget_Agent for cost analysis                          │
│  7. Store in memory (preferences, trip history)                             │
│  8. Format final response                                                   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┬───────────┐
        │                            │                            │           │
        ▼                            ▼                            ▼           ▼
   ┌─────────────┐            ┌─────────────┐            ┌─────────────┐ ┌──────────┐
   │  Weather    │            │   Flight    │            │    Hotel    │ │Itinerary │
   │   Agent     │            │    Agent    │            │    Agent    │ │  Agent   │
   └──────┬──────┘            └──────┬──────┘            └──────┬──────┘ └────┬─────┘
          │                          │                          │             │
          │ "Get weather for        │ "Search flights          │ "Find hotels │ "Create
          │  Paris, May 1-5"        │  NYC→Paris, May 1-5"     │  in Paris"   │  5-day
          │                          │                          │             │  itinerary"
          ▼                          ▼                          ▼             ▼
   ┌─────────────────────────────────────────────────────────────────────────┐
   │                    EXTERNAL APIs & SERVICES                             │
   │                                                                         │
   │  • National Weather Service API                                        │
   │  • Flight Search APIs (Skyscanner, Kayak)                             │
   │  • Hotel Search APIs (Booking.com, Google Hotels)                     │
   │  • Google Maps API (distances, transit)                               │
   │  • TripAdvisor API (attractions, reviews)                             │
   │  • Google Translate API (translations)                                │
   │  • Currency Exchange API (exchange rates)                             │
   │  • Google Calendar API (calendar export)                              │
   │  • Visa Information APIs (VisaHQ, iVisa)                              │
   │  • Bedrock Memory Service (user preferences)                          │
   └─────────────────────────────────────────────────────────────────────────┘
        │                          │                          │             │
        │ Weather data             │ Flight options           │ Hotel list  │ Activities
        │ (JSON)                   │ (JSON)                   │ (JSON)      │ (JSON)
        │                          │                          │             │
        ▼                          ▼                          ▼             ▼
   ┌─────────────┐            ┌─────────────┐            ┌─────────────┐ ┌──────────┐
   │  Weather    │            │   Flight    │            │    Hotel    │ │Itinerary │
   │   Agent     │            │    Agent    │            │    Agent    │ │  Agent   │
   │ (Process)   │            │ (Process)   │            │ (Process)   │ │(Process) │
   └──────┬──────┘            └──────┬──────┘            └──────┬──────┘ └────┬─────┘
          │                          │                          │             │
          │ Formatted               │ Sorted flights           │ Filtered    │ Day-by-day
          │ forecast                │ with prices              │ hotels      │ plan
          │                          │                          │             │
          └──────────────────────────┼──────────────────────────┴─────────────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────────────┐
        │                                                                │
        │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
        │  │   Budget     │  │  Visa & Age  │  │Local Transport
        │  │   Agent      │  │   Agent      │  │   Agent      │        │
        │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
        │         │                 │                 │                 │
        │         │ Analyze costs   │ Check visa      │ Suggest local  │
        │         │ Convert currency│ Filter by age   │ transport      │
        │         │                 │                 │                 │
        │         ▼                 ▼                 ▼                 │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │  Budget breakdown                                    │   │
        │  │  Currency conversion                                 │   │
        │  │  Visa requirements                                   │   │
        │  │  Age-appropriate activities                          │   │
        │  │  Local transport options                             │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                                │
        └────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────────────┐
        │                                                                │
        │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
        │  │  Language    │  │  Calendar    │  │   Memory     │        │
        │  │   Agent      │  │  Integration │  │   Service    │        │
        │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
        │         │                 │                 │                 │
        │         │ Translate       │ Export to       │ Store prefs     │
        │         │ content         │ calendar        │ & history       │
        │         │                 │                 │                 │
        │         ▼                 ▼                 ▼                 │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │  Translated itinerary                               │   │
        │  │  Calendar events                                     │   │
        │  │  User preferences saved                              │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                                │
        └────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRAVEL_PLANNER (Aggregator)                         │
│                                                                             │
│  1. Combine all agent responses                                             │
│  2. Verify completeness (flights, hotels, itinerary, budget)               │
│  3. Check for conflicts (calendar, budget overages)                        │
│  4. Format comprehensive trip plan                                         │
│  5. Add booking links and next steps                                       │
│  6. Store trip in memory                                                   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ Complete Trip Plan
                                     │ (All details, costs, links)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                 │
│                    Display Complete Trip Plan                               │
│                                                                             │
│  ✓ Weather forecast for each day                                           │
│  ✓ Flight options with prices                                              │
│  ✓ Hotel recommendations                                                   │
│  ✓ Day-by-day itinerary                                                    │
│  ✓ Budget breakdown (home & local currency)                                │
│  ✓ Visa requirements & documents                                           │
│  ✓ Age-appropriate activities                                              │
│  ✓ Local transportation options                                            │
│  ✓ Calendar export link                                                    │
│  ✓ Booking links                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Communication Patterns

### Pattern 1: Parallel Agent Execution
Used for independent queries (most common):

```
Travel_Planner
    ├─→ Weather_Agent ─→ (call API) ─→ return results
    ├─→ Flight_Agent  ─→ (call API) ─→ return results
    ├─→ Hotel_Agent   ─→ (call API) ─→ return results
    └─→ Itinerary_Agent → (call API) ─→ return results
    
    (All run simultaneously, ~2-3 seconds total)
    
    ↓ (wait for all to complete)
    
    Aggregate results
```

### Pattern 2: Sequential Agent Execution
Used when one agent needs results from another:

```
Travel_Planner
    ↓
    → Weather_Agent (get weather)
    ↓ (wait for response)
    → Flight_Agent (get flights)
    ↓ (wait for response)
    → Hotel_Agent (get hotels)
    ↓ (wait for response)
    → Budget_Agent (analyze costs with selected items)
    ↓ (wait for response)
    → Visa_and_Age_Agent (check requirements)
    ↓ (wait for response)
    → Local_Transport_Agent (suggest transport)
    ↓
    Return complete plan
```

### Pattern 3: Conditional Agent Routing
Used when query type determines which agents are needed:

```
Travel_Planner analyzes query:

IF query contains "weather":
    → Weather_Agent

IF query contains "flights":
    → Flight_Agent

IF query contains "hotels":
    → Hotel_Agent

IF query contains "activities":
    → Itinerary_Agent

IF query contains "budget":
    → Budget_Agent

IF query contains "visa":
    → Visa_and_Age_Agent

IF query contains "transport":
    → Local_Transport_Agent

IF query is comprehensive (plan a trip):
    → All agents (parallel)
```

---

## Message Format Examples

### 1. User Query → Travel_Planner

```json
{
  "type": "user_query",
  "content": "Plan a 5-day trip to Paris with $3000 budget",
  "metadata": {
    "user_id": "user_123",
    "timestamp": "2025-01-15T10:30:00Z",
    "session_id": "session_456"
  }
}
```

### 2. Travel_Planner → Weather_Agent

```json
{
  "type": "agent_request",
  "source": "travel_planner",
  "target": "weather_agent",
  "action": "get_forecast",
  "parameters": {
    "destination": "Paris",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "start_date": "2025-05-01",
    "end_date": "2025-05-05"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 3. Weather_Agent → Travel_Planner

```json
{
  "type": "agent_response",
  "source": "weather_agent",
  "target": "travel_planner",
  "status": "success",
  "data": {
    "destination": "Paris",
    "forecast": [
      {
        "date": "2025-05-01",
        "high_temp": 22,
        "low_temp": 15,
        "condition": "Sunny",
        "precipitation_chance": 10
      }
    ],
    "recommendation": "Excellent weather for outdoor activities"
  },
  "timestamp": "2025-01-15T10:31:00Z"
}
```

### 4. Travel_Planner → Budget_Agent (with multiple items)

```json
{
  "type": "agent_request",
  "source": "travel_planner",
  "target": "budget_agent",
  "action": "analyze_budget",
  "parameters": {
    "total_budget": 3000,
    "home_currency": "USD",
    "destination_currency": "EUR",
    "trip_duration_days": 5,
    "selected_items": {
      "flights": {
        "cost": 650,
        "currency": "USD"
      },
      "hotel": {
        "cost": 1120,
        "currency": "EUR",
        "nights": 4
      },
      "activities": {
        "cost": 510,
        "currency": "EUR"
      }
    }
  },
  "timestamp": "2025-01-15T10:35:00Z"
}
```

### 5. Budget_Agent → Travel_Planner (with currency conversion)

```json
{
  "type": "agent_response",
  "source": "budget_agent",
  "target": "travel_planner",
  "status": "success",
  "data": {
    "budget_analysis": {
      "total_budget_usd": 3000,
      "total_budget_eur": 2750,
      "breakdown": {
        "flights": {
          "usd": 650,
          "eur": 597,
          "percentage": 22
        },
        "hotel": {
          "usd": 1220,
          "eur": 1120,
          "percentage": 41
        },
        "activities": {
          "usd": 555,
          "eur": 510,
          "percentage": 19
        }
      },
      "total_spent_usd": 2425,
      "total_spent_eur": 2227,
      "remaining_usd": 575,
      "remaining_eur": 523,
      "status": "WITHIN_BUDGET"
    }
  },
  "timestamp": "2025-01-15T10:36:00Z"
}
```

### 6. Travel_Planner → Visa_and_Age_Agent

```json
{
  "type": "agent_request",
  "source": "travel_planner",
  "target": "visa_and_age_agent",
  "action": "check_requirements",
  "parameters": {
    "origin_country": "USA",
    "destination_country": "France",
    "traveler_age": 30,
    "activities": [
      "museum_visit",
      "wine_tasting",
      "hiking",
      "nightclub"
    ]
  },
  "timestamp": "2025-01-15T10:37:00Z"
}
```

### 7. Visa_and_Age_Agent → Travel_Planner

```json
{
  "type": "agent_response",
  "source": "visa_and_age_agent",
  "target": "travel_planner",
  "status": "success",
  "data": {
    "visa_requirements": {
      "required": false,
      "reason": "US citizens can visit France visa-free for up to 90 days",
      "documents": ["Valid passport (6+ months validity)"],
      "processing_time": "N/A"
    },
    "age_restrictions": {
      "museum_visit": {
        "allowed": true,
        "notes": "All ages welcome"
      },
      "wine_tasting": {
        "allowed": true,
        "notes": "Age 18+ for alcohol tasting"
      },
      "hiking": {
        "allowed": true,
        "notes": "All ages welcome"
      },
      "nightclub": {
        "allowed": true,
        "notes": "Age 18+ required"
      }
    },
    "filtered_activities": [
      "museum_visit",
      "wine_tasting",
      "hiking",
      "nightclub"
    ]
  },
  "timestamp": "2025-01-15T10:38:00Z"
}
```

### 8. Travel_Planner → Local_Transport_Agent

```json
{
  "type": "agent_request",
  "source": "travel_planner",
  "target": "local_transport_agent",
  "action": "suggest_transport",
  "parameters": {
    "origin": "CDG Airport, Paris",
    "destination": "Hotel Le Marais, Paris",
    "date": "2025-05-01",
    "time": "14:30",
    "preferences": ["cost_effective", "reliable"]
  },
  "timestamp": "2025-01-15T10:39:00Z"
}
```

### 9. Local_Transport_Agent → Travel_Planner

```json
{
  "type": "agent_response",
  "source": "local_transport_agent",
  "target": "travel_planner",
  "status": "success",
  "data": {
    "transport_options": [
      {
        "type": "public_transit",
        "description": "RER B train + Metro",
        "cost_eur": 12.45,
        "duration_minutes": 45,
        "convenience": 4,
        "instructions": "Take RER B to Châtelet, then Metro Line 4 to Saint-Paul"
      },
      {
        "type": "taxi",
        "description": "Taxi from CDG",
        "cost_eur": 55,
        "duration_minutes": 30,
        "convenience": 5,
        "instructions": "Taxi stand at Terminal 2E"
      },
      {
        "type": "ride_share",
        "description": "Uber/Bolt",
        "cost_eur": 35,
        "duration_minutes": 35,
        "convenience": 4,
        "instructions": "Order via app at baggage claim"
      }
    ],
    "recommendation": "Public transit offers best value"
  },
  "timestamp": "2025-01-15T10:40:00Z"
}
```

---

## Data Flow for Complete Trip Planning

```
User Input
    ↓
Travel_Planner (Parse & Route)
    ├─→ Weather_Agent ─→ Forecast data
    ├─→ Flight_Agent ─→ Flight options
    ├─→ Hotel_Agent ─→ Hotel options
    ├─→ Itinerary_Agent ─→ Activities & schedule
    └─→ (Wait for all)
    ↓
Travel_Planner (Coordinate)
    ├─→ Budget_Agent ─→ Cost analysis + currency conversion
    ├─→ Visa_and_Age_Agent ─→ Requirements & filtering
    ├─→ Local_Transport_Agent ─→ Transport options
    └─→ (Wait for all)
    ↓
Travel_Planner (Enhance)
    ├─→ Language_Agent ─→ Translations
    ├─→ Calendar Integration ─→ Export events
    └─→ Memory Service ─→ Store preferences
    ↓
Travel_Planner (Aggregate)
    ├─ Combine all responses
    ├─ Verify completeness
    ├─ Check for conflicts
    ├─ Format final response
    └─ Add booking links
    ↓
User Response
    (Complete trip plan with all details)
```

---

## Error Handling & Fallbacks

### Scenario 1: API Timeout

```
Flight_Agent calls Skyscanner API
    ↓
API doesn't respond within 30 seconds
    ↓
Flight_Agent retries (up to 3 times with exponential backoff)
    ↓
If still fails:
    - Return fallback message
    - Suggest manual search links
    - Continue with other agents
    ↓
Travel_Planner includes in response:
    "Flights: Unable to fetch live data. 
     Try: [link to Skyscanner]"
```

### Scenario 2: Budget Exceeded

```
Travel_Planner receives:
    - Budget: $3000
    - Flights: $1500
    - Hotels: $1800
    - Total: $3300 (exceeds budget)
    ↓
Budget_Agent alerts:
    "Budget exceeded by $300"
    ↓
Suggests alternatives:
    - Cheaper hotel: $1500 (saves $300)
    - Budget airline: $1200 (saves $300)
    ↓
Travel_Planner presents options to user
```

### Scenario 3: Visa Required

```
Visa_and_Age_Agent checks:
    Origin: USA
    Destination: India
    ↓
Visa required: YES
    ↓
Returns:
    - Visa type: Tourist visa
    - Processing time: 5-7 business days
    - Cost: $100
    - Required documents: [list]
    - Application link: [URL]
    ↓
Travel_Planner alerts user:
    "Visa required for India. 
     Allow 5-7 days for processing."
```

---

## Real-Time Monitoring & Alerts

### Price Drop Alert

```
User books flight for $850
    ↓
Travel_Planner monitors price
    ↓
Price drops to $700
    ↓
Alert sent to user:
    "Price dropped! You could save $150 by rebooking"
```

### Flight Delay Alert

```
User's flight is scheduled
    ↓
Travel_Planner monitors flight status
    ↓
Flight delayed by 2 hours
    ↓
Alert sent to user:
    "Your flight is delayed by 2 hours. 
     New arrival: 12:00 PM instead of 10:00 AM"
```

### Weather Alert

```
User's trip is in 3 days
    ↓
Travel_Planner monitors weather
    ↓
Severe weather predicted
    ↓
Alert sent to user:
    "Severe weather expected in Paris on May 3-4.
     Consider rescheduling outdoor activities."
```

---

## Summary: Communication Architecture

The Travel Planning Agent uses a **centralized hub-and-spoke model** where:

1. **Travel_Planner** acts as the central hub
2. **8 Specialized Agents** are the spokes
3. **External APIs** provide data
4. **Memory Service** stores preferences
5. **User Interface** displays results

**Key Characteristics:**
- ✅ Parallel execution for independent queries
- ✅ Sequential execution for dependent queries
- ✅ Intelligent routing based on query type
- ✅ Comprehensive error handling
- ✅ Real-time monitoring and alerts
- ✅ Currency conversion and localization
- ✅ Visa and age requirement checking
- ✅ Calendar integration
- ✅ Local transportation suggestions
- ✅ Memory persistence for personalization

**Communication Speed:**
- Simple query (weather only): ~2-3 seconds
- Complete trip planning: ~5-8 seconds
- Follow-up modifications: ~3-5 seconds
