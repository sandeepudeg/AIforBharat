import json
import os

NOTEBOOK_PATH = r"d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent\Concierge_Agent.ipynb"

NEW_DOC_CONTENT = [
    "# Concierge Agent: Your Personal AI Travel Orchestrator\n",
    "\n",
    "## 1. The Problem\n",
    "**Travel planning is broken.**\n",
    "Planning a single trip today requires juggling dozens of disconnected platforms: Expedia for flights, Airbnb for stays, TripAdvisor for activities, government sites for visas, and weather apps for packing.\n",
    "*   **Information Overload**: Users are drowning in tabs and conflicting reviews.\n",
    "*   **Context Switching**: Data doesn't flow between apps.\n",
    "*   **Decision Fatigue**: The stress of coordinating logistics often overshadows the excitement of travel.\n",
    "\n",
    "## 2. The Solution\n",
    "**Concierge Agent: A Multi-Agent AI Orchestrator.**\n",
    "We built a collaborative workforce of specialized AI agents powered by **Google's Agent Development Kit (ADK)** and **Gemini** models.\n",
    "*   **Unified Experience**: Replace 10+ apps with one conversation.\n",
    "*   **Active Orchestration**: Proactively checks requirements (visas, weather) based on your bookings.\n",
    "*   **15+ Capabilities**: From planning and booking to real-time translation and emergency support.\n",
    "\n",
    "## 3. Architecture\n",
    "The system follows a hub-and-spoke **Multi-Agent Architecture** orchestrated by a Root Coordinator.\n",
    "\n",
    "- **Root Coordinator**: The \"Head Concierge\" that understands intent and delegates tasks.\n",
    "- **Planning Agent**: Crafts personalized itineraries.\n",
    "- **Booking Agent**: Handles flights, hotels, and rides.\n",
    "- **Utility Agent**: Manages logistics (visas, currency, insurance).\n",
    "- **Search Agent**: Fetches real-time data (news, events) via Google Search.\n",
    "- **Social Agent**: Manages user preferences and feedback.\n",
    "\n",
    "## 4. How to Run This Notebook\n",
    "1.  **Install Dependencies**: Run the first code cell to install `google-adk`.\n",
    "2.  **Set API Key**: Ensure your `GOOGLE_API_KEY` is set in the environment or the `.env` file.\n",
    "3.  **Run All Cells**: Execute all cells to define the agents and tools.\n",
    "4.  **Launch**: The final cell will start the ADK web server.\n"
]

def update_notebook():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Error: Notebook not found at {NOTEBOOK_PATH}")
        return

    try:
        with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Create the new cell structure
        new_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": NEW_DOC_CONTENT
        }

        # Check if the first cell is markdown
        if nb.get('cells') and nb['cells'][0]['cell_type'] == 'markdown':
            print("Updating existing first markdown cell...")
            nb['cells'][0]['source'] = NEW_DOC_CONTENT
        else:
            print("Inserting new markdown cell at the beginning...")
            nb['cells'].insert(0, new_cell)
        
        with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1) # Using indent=1 to minimize diff noise if possible, or standard 4
            
        print("✅ Notebook documentation updated successfully.")
        
    except Exception as e:
        print(f"❌ Failed to update notebook: {e}")

if __name__ == "__main__":
    update_notebook()
