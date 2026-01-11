#!/usr/bin/env python3
"""Database Referee - Command Line Interface Version."""

from src.constraint_parser import ConstraintParser
from src.models import Constraint

def print_header():
    """Print application header."""
    print("\n" + "=" * 70)
    print("⚖️  DATABASE REFEREE - Decision Support Tool")
    print("=" * 70)
    print("Help you choose between PostgreSQL, DynamoDB, and Redis")
    print("=" * 70 + "\n")

def get_user_input():
    """Get constraint inputs from user."""
    print("Please answer the following questions about your database needs:\n")
    
    # Data Structure
    print("1. What type of data structure do you need?")
    print("   Options: Relational, JSON, Key-Value")
    data_structure = input("   Enter choice: ").strip()
    
    # Read/Write Ratio
    print("\n2. What percentage of operations are reads? (0-100)")
    try:
        read_write_ratio = int(input("   Enter percentage: ").strip())
    except ValueError:
        read_write_ratio = 50
    
    # Consistency Level
    print("\n3. What consistency level do you need?")
    print("   Options: Strong, Eventual")
    consistency_level = input("   Enter choice: ").strip()
    
    # Query Complexity
    print("\n4. What is your query complexity?")
    print("   Options: Simple, Moderate, Complex")
    query_complexity = input("   Enter choice: ").strip()
    
    # Scale
    print("\n5. What is your expected data scale (GB)?")
    try:
        scale_gb = float(input("   Enter size in GB: ").strip())
    except ValueError:
        scale_gb = 10.0
    
    # Latency
    print("\n6. What is your latency requirement (milliseconds)?")
    try:
        latency_ms = float(input("   Enter latency in ms: ").strip())
    except ValueError:
        latency_ms = 5.0
    
    # Team Expertise
    print("\n7. What is your team's database expertise?")
    print("   Options: Low, Medium, High")
    team_expertise = input("   Enter choice: ").strip()
    
    # Persistence
    print("\n8. Is data persistence critical? (yes/no)")
    persistence_input = input("   Enter choice: ").strip().lower()
    requires_persistence = persistence_input in ['yes', 'y', 'true', '1']
    
    return {
        "data_structure": data_structure,
        "read_write_ratio": read_write_ratio,
        "consistency_level": consistency_level,
        "query_complexity": query_complexity,
        "scale_gb": scale_gb,
        "latency_ms": latency_ms,
        "team_expertise": team_expertise,
        "requires_persistence": requires_persistence,
    }

def display_constraint_summary(constraint: Constraint):
    """Display the parsed constraint summary."""
    print("\n" + "=" * 70)
    print("📋 YOUR CONSTRAINTS SUMMARY")
    print("=" * 70)
    print(f"Data Structure:        {constraint.data_structure}")
    print(f"Read/Write Ratio:      {constraint.read_write_ratio}% reads")
    print(f"Consistency Level:     {constraint.consistency_level}")
    print(f"Query Complexity:      {constraint.query_complexity}")
    print(f"Data Scale:            {constraint.scale_gb} GB")
    print(f"Latency Requirement:   {constraint.latency_ms} ms")
    print(f"Team Expertise:        {constraint.team_expertise}")
    print(f"Persistence Required:  {'Yes' if constraint.requires_persistence else 'No'}")
    print("=" * 70 + "\n")

def main():
    """Main application loop."""
    print_header()
    
    while True:
        # Get user input
        raw_inputs = get_user_input()
        
        # Parse and validate constraints
        constraint, error = ConstraintParser.parse_constraints(raw_inputs)
        
        if error:
            print("\n" + "❌ " * 20)
            print(f"VALIDATION ERROR: {error.message}")
            print("❌ " * 20 + "\n")
            
            retry = input("Would you like to try again? (yes/no): ").strip().lower()
            if retry not in ['yes', 'y']:
                print("\nThank you for using Database Referee!")
                break
            continue
        
        # Display summary
        print("\n✅ Constraints validated successfully!\n")
        display_constraint_summary(constraint)
        
        # Show next steps
        print("=" * 70)
        print("🔄 NEXT STEPS")
        print("=" * 70)
        print("1. Disqualification Engine - Eliminates unsuitable databases")
        print("2. Scoring Engine - Calculates weighted scores")
        print("3. Report Generator - Creates detailed trade-off analysis")
        print("4. Final Recommendation - Shows winner with pros/cons")
        print("\nThese features are coming soon!")
        print("=" * 70 + "\n")
        
        # Ask if user wants to try another scenario
        another = input("Would you like to analyze another scenario? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            print("\nThank you for using Database Referee!")
            break
        
        print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Thank you for using Database Referee!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your input and try again.")
