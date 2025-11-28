# Concierge Agent: The Future of Travel Planning

![Concierge Agent Banner](https://via.placeholder.com/1200x300?text=Concierge+Agent:+Your+Personal+AI+Travel+Orchestrator)

## 1. The Problem
**Travel planning is broken.**
Planning a single trip today requires juggling dozens of disconnected platforms: Expedia for flights, Airbnb for stays, TripAdvisor for activities, government sites for visas, and weather apps for packing.
*   **Information Overload**: Users are drowning in tabs and conflicting reviews.
*   **Context Switching**: Data doesn't flow between apps. Your flight app doesn't know you need a visa, and your hotel app doesn't know it's raining.
*   **Decision Fatigue**: The stress of coordinating logistics often overshadows the excitement of travel.

## 2. The Solution
**Concierge Agent: A Multi-Agent AI Orchestrator.**
We built a collaborative workforce of specialized AI agents powered by **Google's Agent Development Kit (ADK)** and **Gemini** models. Instead of a simple chatbot, we have a team of experts working in unison to handle every aspect of your trip.

### Key Features
*   **Unified Experience**: Replace 10+ apps with one conversation.
*   **Active Orchestration**: Proactively checks requirements (visas, weather) based on your bookings.
*   **15+ Capabilities**: From planning and booking to real-time translation and emergency support.

## 3. Architecture
The system follows a hub-and-spoke **Multi-Agent Architecture** orchestrated by a Root Coordinator.

```mermaid
graph TD
    User((User)) <--> Root[Concierge Coordinator<br/>(Root Agent)]
    
    Root -->|Delegates Planning| Planning[Planning Agent]
    Root -->|Delegates Booking| Booking[Booking Agent]
    Root -->|Delegates Utilities| Utility[Utility Agent]
    Root -->|Delegates Search| Search[Search Agent]
    Root -->|Delegates Social| Social[Social Agent]

    subgraph "Planning Capabilities"
        Planning --> T1(Destinations)
        Planning --> T2(Itineraries)
        Planning --> T3(Activities)
    end

    subgraph "Booking Capabilities"
        Booking --> T4(Flights)
        Booking --> T5(Hotels)
        Booking --> T6(Rides)
    end

    subgraph "Utility Capabilities"
        Utility --> T7(Weather/Currency)
        Utility --> T8(Translation)
        Utility --> T9(Visa/Insurance)
    end

    subgraph "Real-Time Info"
        Search --> T10(Google Search)
    end

    subgraph "User Profile"
        Social --> T11(Preferences)
        Social --> T12(Feedback/Share)
    end
```

### Components
1.  **Root Coordinator**: The "Head Concierge" that understands intent and delegates tasks.
2.  **Planning Agent**: Crafts personalized itineraries.
3.  **Booking Agent**: Handles flights, hotels, and rides.
4.  **Utility Agent**: Manages logistics (visas, currency, insurance).
5.  **Search Agent**: Fetches real-time data (news, events) via Google Search.
6.  **Social Agent**: Manages user preferences and feedback.

## 4. Setup & Deployment

### Prerequisites
*   Python 3.11+
*   Google Cloud Project with Vertex AI API enabled
*   `GOOGLE_API_KEY` environment variable set

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/AIforBharat/tree/Kaggle/Kaggle/Concierge_Agent_Kaggle.git
cd Concierge_Agent_Kaggle

# Install dependencies
pip install google-adk uvicorn python-dotenv
```

### Running Locally
We provide a fixed runner script for easy local testing:

```bash
# Run the GUI launcher
python run_gui_fixed.py
```
*   **URL**: `http://127.0.0.1:8000`
*   **Action**: Opens your browser automatically to the chat interface.

## 5. File Structure
```
Concierge_Agent_Kaggle/
├── Concierge_Agent.ipynb                       # Interactive notebook implementation
├── requirements.txt                            # Project dependencies
├── README.md                                   # This documentation
└── MCP_IMPLEMENTATION_SUMMARY.md               # MCP Implementation Summary
└── QUICKSTART.ipynb                            # Quick start guide


```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
