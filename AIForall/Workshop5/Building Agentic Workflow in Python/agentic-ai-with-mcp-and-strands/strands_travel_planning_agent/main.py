#!/usr/bin/env python3
"""
Travel Planning Agent - Main Entry Point

This script demonstrates how to use the Strands-based Travel Planning system.
Uses the @tool decorator pattern from the Strands framework.
"""

import logging
from travel_planner import create_travel_planner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_mode():
    """Run demo with predefined travel queries."""
    print("\n" + "="*60)
    print("🌍 Travel Planning Agent - Demo Mode")
    print("="*60 + "\n")
    
    planner = create_travel_planner()
    
    # Demo queries
    demo_queries = [
        "What's the weather forecast for Paris from June 1-5?",
        "Find me flights from New York to Paris on June 1st",
        "Search for hotels in Paris for June 1-5",
        "Create a 5-day itinerary for Paris with culture and food interests",
        "What's the budget breakdown for a $3000 trip over 5 days?",
        "What are the visa requirements for US citizens traveling to France?",
        "What local transportation options are available in Paris?",
        "How do I say 'Hello' in French?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"Demo {i}: {query}")
        print("-" * 40)
        try:
            response = planner(query)
            print(f"Response: {str(response)[:200]}...")
            print()
        except Exception as e:
            print(f"Error: {str(e)}\n")


def interactive_mode():
    """Run interactive mode for user queries."""
    print("\n" + "="*60)
    print("🌍 Travel Planning Agent - Interactive Mode")
    print("="*60)
    print("\nAsk any travel-related question and I'll help you plan!")
    print("Type 'exit' to quit.\n")
    
    planner = create_travel_planner()
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            print("\n🔄 Processing your query...")
            response = planner(user_input)
            print(f"\n✅ Response:\n{str(response)}")
        
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def single_query_mode(query: str):
    """Run with a single query."""
    print("\n" + "="*60)
    print("🌍 Travel Planning Agent - Single Query Mode")
    print("="*60 + "\n")
    
    planner = create_travel_planner()
    
    print(f"Query: {query}\n")
    print("🔄 Processing...\n")
    
    try:
        response = planner(query)
        print(f"✅ Response:\n{str(response)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_mode()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            single_query_mode(" ".join(sys.argv[1:]))
    else:
        # Default to interactive mode
        interactive_mode()
