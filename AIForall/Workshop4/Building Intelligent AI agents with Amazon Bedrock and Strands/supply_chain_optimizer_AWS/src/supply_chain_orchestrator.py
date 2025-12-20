#!/usr/bin/env python3
"""
Supply Chain Orchestrator Agent

A master agent that uses all supply chain agents as tools.
This agent can be asked to perform supply chain operations and will
automatically call the appropriate tools.
"""

import os
from strands import Agent
from strands.models import BedrockModel

from src.agents.agent_tools import (
    forecast_demand,
    optimize_inventory,
    create_purchase_order,
    detect_anomalies,
    generate_report,
    get_inventory_status,
    sync_data_from_knowledge_base,
    retrieve_from_knowledge_base,
)
from src.config import logger

# Enable rich UI for tools
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"


# System prompt for the orchestrator
SYSTEM_PROMPT = """You are a Supply Chain Optimization Agent. You have access to powerful tools to manage supply chain operations.

Your capabilities:
1. **Forecast Demand** - Analyze sales history and generate demand forecasts with confidence intervals
2. **Optimize Inventory** - Calculate optimal order quantities and reorder points
3. **Create Purchase Orders** - Place orders with suppliers
4. **Detect Anomalies** - Identify inventory issues and supply chain problems
5. **Generate Reports** - Create analytics reports with KPIs
6. **Check Inventory Status** - Get current inventory levels
7. **Sync Data from Knowledge Base** - Retrieve and store data from Bedrock Knowledge Base to DynamoDB
8. **Retrieve from Knowledge Base** - Search and retrieve specific data from knowledge base

When a user asks about supply chain operations:
- Use sync_data_from_knowledge_base to load data from knowledge base first
- Use retrieve_from_knowledge_base to search for specific data
- Use forecast_demand to predict future demand
- Use optimize_inventory to calculate optimal quantities
- Use create_purchase_order to place orders
- Use detect_anomalies to identify issues
- Use generate_report to create analytics
- Use get_inventory_status to check current levels

Always provide clear, actionable recommendations based on the data.
When multiple operations are needed, perform them in logical sequence.
"""


def create_orchestrator_agent():
    """Create and return the orchestrator agent."""
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    )
    
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            forecast_demand,
            optimize_inventory,
            create_purchase_order,
            detect_anomalies,
            generate_report,
            get_inventory_status,
            sync_data_from_knowledge_base,
            retrieve_from_knowledge_base,
        ],
    )
    
    return agent


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("  SUPPLY CHAIN OPTIMIZATION ORCHESTRATOR")
    print("="*70)
    print("\n✨ I can help you with:")
    print("   📊 Forecast demand for products")
    print("   📦 Optimize inventory levels")
    print("   🛒 Create purchase orders")
    print("   ⚠️  Detect supply chain anomalies")
    print("   📈 Generate analytics reports")
    print("   📋 Check inventory status")
    print("   🔄 Sync data from Knowledge Base")
    print("   🔍 Retrieve data from Knowledge Base")
    print("\n💡 Example queries:")
    print("   • 'Sync data from knowledge base'")
    print("   • 'Forecast demand for PROD-001'")
    print("   • 'Optimize inventory for PROD-001'")
    print("   • 'Create a purchase order for 1500 units'")
    print("   • 'Check for anomalies in PROD-001'")
    print("   • 'Generate a report for all products'")
    print("\n🚪 Type 'exit' to quit")
    print("="*70 + "\n")


def run_interactive_mode():
    """Run the agent in interactive mode."""
    print_header()
    
    agent = create_orchestrator_agent()
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                print("💭 Please enter a message or type 'exit' to quit\n")
                continue
            
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("\n" + "="*70)
                print("👋 Thanks for using Supply Chain Orchestrator!")
                print("🎉 Have a great day!")
                print("="*70 + "\n")
                break
            
            print("\n🤖 Orchestrator: ", end="")
            response = agent(user_input)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n" + "="*70)
            print("👋 Orchestrator interrupted!")
            print("="*70 + "\n")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"\n❌ An error occurred: {str(e)}")
            print("💡 Please try again or type 'exit' to quit\n")


def run_example_workflow():
    """Run an example workflow demonstrating the orchestrator."""
    print_header()
    print("Running example workflow...\n")
    
    agent = create_orchestrator_agent()
    
    # Example 1: Forecast demand
    print("📊 STEP 1: Forecasting demand...")
    print("-" * 70)
    query1 = """
    I need to forecast demand for product PROD-001. 
    Here's the sales data for the last 12 months:
    - January: 95 units
    - February: 105 units
    - March: 100 units
    - April: 110 units
    - May: 98 units
    - June: 115 units
    - July: 120 units
    - August: 110 units
    - September: 105 units
    - October: 125 units
    - November: 130 units
    - December: 140 units
    
    Please forecast for the next 30 days.
    """
    response1 = agent(query1)
    print(f"Response: {response1}\n")
    
    # Example 2: Optimize inventory
    print("\n📦 STEP 2: Optimizing inventory...")
    print("-" * 70)
    query2 = """
    Based on the forecast, optimize inventory for PROD-001.
    Annual demand is approximately 1350 units.
    Ordering cost is $50 per order.
    Holding cost is $2 per unit per year.
    """
    response2 = agent(query2)
    print(f"Response: {response2}\n")
    
    # Example 3: Create purchase order
    print("\n🛒 STEP 3: Creating purchase order...")
    print("-" * 70)
    query3 = """
    Create a purchase order for PROD-001 with:
    - Supplier: SUPP-001
    - Quantity: 1500 units
    - Unit price: $10.50
    - Expected delivery: 7 days
    """
    response3 = agent(query3)
    print(f"Response: {response3}\n")
    
    # Example 4: Detect anomalies
    print("\n⚠️  STEP 4: Detecting anomalies...")
    print("-" * 70)
    query4 = """
    Check for anomalies in PROD-001 inventory:
    - Current inventory: 500 units
    - Forecasted inventory: 1000 units
    - 80% confidence interval: 950 units
    - 95% confidence interval: 900 units
    """
    response4 = agent(query4)
    print(f"Response: {response4}\n")
    
    # Example 5: Generate report
    print("\n📈 STEP 5: Generating report...")
    print("-" * 70)
    query5 = """
    Generate an analytics report with:
    - Inventory: PROD-001 with 500 units worth $5250
    - Forecast: 1000 units forecasted, 950 actual
    - Supplier: SUPP-001 with 95% reliability
    """
    response5 = agent(query5)
    print(f"Response: {response5}\n")
    
    print("\n" + "="*70)
    print("✓ Example workflow completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        # Run example workflow
        run_example_workflow()
    else:
        # Run interactive mode
        run_interactive_mode()
