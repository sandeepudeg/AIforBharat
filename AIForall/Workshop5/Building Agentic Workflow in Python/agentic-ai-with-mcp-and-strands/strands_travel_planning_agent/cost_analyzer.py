#!/usr/bin/env python3
"""
Cost Analyzer Component

Analyzes flight prices and categorizes options by cost.
Calculates cost effectiveness scores and identifies deals.
"""

import logging
from enum import Enum
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PriceTier(Enum):
    """Price tier classification."""
    BUDGET = "Budget"
    ECONOMY = "Economy"
    PREMIUM = "Premium"


class CostAnalyzer:
    """Analyzes flight prices and identifies cost patterns."""
    
    # Price tier thresholds
    BUDGET_THRESHOLD = 300
    ECONOMY_THRESHOLD = 600
    
    # Deal thresholds
    GREAT_DEAL_THRESHOLD = 0.20  # 20% savings
    EXCEPTIONAL_SAVINGS_THRESHOLD = 0.30  # 30% savings
    
    @staticmethod
    def categorize_by_price_tier(flights: List[Dict]) -> List[Dict]:
        """
        Categorize flights into price tiers.
        
        Args:
            flights: List of flight dictionaries
            
        Returns:
            List of flights with price_tier added
        """
        categorized = []
        for flight in flights:
            price = flight.get("price", 0)
            
            if price < CostAnalyzer.BUDGET_THRESHOLD:
                tier = PriceTier.BUDGET
            elif price < CostAnalyzer.ECONOMY_THRESHOLD:
                tier = PriceTier.ECONOMY
            else:
                tier = PriceTier.PREMIUM
            
            flight_copy = flight.copy()
            flight_copy["price_tier"] = tier.value
            categorized.append(flight_copy)
        
        return categorized
    
    @staticmethod
    def calculate_cost_effectiveness_score(flight: Dict) -> float:
        """
        Calculate cost effectiveness score (price per hour of travel).
        
        Lower score = better value.
        
        Args:
            flight: Flight dictionary with price and duration_minutes
            
        Returns:
            Cost effectiveness score
        """
        price = flight.get("price", 0)
        duration_minutes = flight.get("duration_minutes", 1)
        
        # Convert minutes to hours
        duration_hours = max(0.1, duration_minutes / 60)
        
        return price / duration_hours
    
    @staticmethod
    def identify_cheapest_flight(flights: List[Dict]) -> Optional[Dict]:
        """
        Find the cheapest flight.
        
        Args:
            flights: List of flights
            
        Returns:
            Cheapest flight or None if empty
        """
        if not flights:
            return None
        
        # Use flight_id as tiebreaker to ensure deterministic result
        return min(flights, key=lambda f: (f.get("price", float('inf')), f.get("flight_id", "")))
    
    @staticmethod
    def identify_best_value_flight(flights: List[Dict]) -> Optional[Dict]:
        """
        Find the best value flight (lowest cost effectiveness score).
        
        Args:
            flights: List of flights
            
        Returns:
            Best value flight or None if empty
        """
        if not flights:
            return None
        
        # Use flight_id as tiebreaker to ensure deterministic result
        return min(
            flights,
            key=lambda f: (
                CostAnalyzer.calculate_cost_effectiveness_score(f),
                f.get("flight_id", "")
            )
        )
    
    @staticmethod
    def calculate_average_price(flights: List[Dict]) -> float:
        """
        Calculate average price of flights.
        
        Args:
            flights: List of flights
            
        Returns:
            Average price
        """
        if not flights:
            return 0
        
        prices = [f.get("price", 0) for f in flights]
        return sum(prices) / len(prices)
    
    @staticmethod
    def identify_price_outliers(flights: List[Dict]) -> Dict:
        """
        Find unusually cheap and expensive flights.
        
        Args:
            flights: List of flights
            
        Returns:
            Dictionary with cheap_outliers and expensive_outliers
        """
        if not flights:
            return {"cheap_outliers": [], "expensive_outliers": []}
        
        prices = [f.get("price", 0) for f in flights]
        avg_price = sum(prices) / len(prices)
        std_dev = (sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5
        
        cheap_threshold = avg_price - (2 * std_dev)
        expensive_threshold = avg_price + (2 * std_dev)
        
        cheap_outliers = [f for f in flights if f.get("price", 0) < cheap_threshold]
        expensive_outliers = [f for f in flights if f.get("price", 0) > expensive_threshold]
        
        return {
            "cheap_outliers": cheap_outliers,
            "expensive_outliers": expensive_outliers,
            "average_price": avg_price,
            "std_dev": std_dev
        }
    
    @staticmethod
    def add_cost_metrics(flights: List[Dict], average_price: Optional[float] = None) -> List[Dict]:
        """
        Add cost metrics to flights (price tier, cost effectiveness, deal flags).
        
        Args:
            flights: List of flights
            average_price: Average price for comparison (calculated if not provided)
            
        Returns:
            List of flights with cost metrics added
        """
        if not flights:
            return []
        
        # Calculate average if not provided
        if average_price is None:
            average_price = CostAnalyzer.calculate_average_price(flights)
        
        # Categorize by price tier
        categorized = CostAnalyzer.categorize_by_price_tier(flights)
        
        # Find cheapest and best value
        cheapest = CostAnalyzer.identify_cheapest_flight(categorized)
        best_value = CostAnalyzer.identify_best_value_flight(categorized)
        
        # Create a unique identifier for comparison (use index as fallback)
        cheapest_idx = None
        best_value_idx = None
        
        if cheapest:
            for idx, f in enumerate(categorized):
                if f.get("flight_id") == cheapest.get("flight_id") and f.get("price") == cheapest.get("price"):
                    cheapest_idx = idx
                    break
        
        if best_value:
            best_value_score = CostAnalyzer.calculate_cost_effectiveness_score(best_value)
            for idx, f in enumerate(categorized):
                if CostAnalyzer.calculate_cost_effectiveness_score(f) == best_value_score and f.get("flight_id") == best_value.get("flight_id"):
                    best_value_idx = idx
                    break
        
        # Add metrics to each flight
        result = []
        for idx, flight in enumerate(categorized):
            flight_copy = flight.copy()
            price = flight_copy.get("price", 0)
            
            # Cost effectiveness score
            flight_copy["cost_effectiveness_score"] = CostAnalyzer.calculate_cost_effectiveness_score(flight_copy)
            
            # Savings vs average
            savings_vs_avg = ((average_price - price) / average_price * 100) if average_price > 0 else 0
            flight_copy["savings_vs_average"] = round(savings_vs_avg, 2)
            
            # Deal flags
            flight_copy["is_great_deal"] = savings_vs_avg > (CostAnalyzer.GREAT_DEAL_THRESHOLD * 100)
            flight_copy["is_exceptional_savings"] = savings_vs_avg > (CostAnalyzer.EXCEPTIONAL_SAVINGS_THRESHOLD * 100)
            
            # Cheapest and best value flags (only mark the first one found)
            flight_copy["is_cheapest"] = (idx == cheapest_idx)
            flight_copy["is_best_value"] = (idx == best_value_idx)
            
            # Deal indicator emoji
            if flight_copy["is_cheapest"]:
                flight_copy["deal_indicator"] = "💰 Cheapest"
            elif flight_copy["is_best_value"]:
                flight_copy["deal_indicator"] = "⭐ Best Value"
            elif flight_copy["is_exceptional_savings"]:
                flight_copy["deal_indicator"] = "🎉 Exceptional Savings"
            elif flight_copy["is_great_deal"]:
                flight_copy["deal_indicator"] = "✨ Great Deal"
            else:
                flight_copy["deal_indicator"] = ""
            
            result.append(flight_copy)
        
        return result
